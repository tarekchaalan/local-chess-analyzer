"""Download the pinned Stockfish release for this (or every) platform into `stockfish/`.

    uv run fetch-stockfish                 # current platform
    uv run fetch-stockfish --platform all  # every platform (CI / packaging)
    uv run fetch-stockfish --force         # re-download even if present

Binaries are not committed to git; this script is how dev checkouts, CI builds and the
Docker image obtain them. Every archive is verified against a pinned sha256 before use.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import platform
import stat
import sys
import tarfile
import zipfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import httpx

from ..config import Paths

RELEASE = "sf_17.1"
BASE_URL = f"https://github.com/official-stockfish/Stockfish/releases/download/{RELEASE}/"


@dataclass(frozen=True)
class Asset:
    key: str  # platform key used on the command line
    archive: str  # release asset name
    member: str  # path of the binary inside the archive
    target: str  # file name we install as (what lca.config looks for)
    sha256: str  # of the downloaded archive


# avx2 builds: the fastest variant that still runs on every x86-64 CPU from the last decade.
ASSETS: dict[str, Asset] = {
    "macos-silicon": Asset(
        "macos-silicon",
        "stockfish-macos-m1-apple-silicon.tar",
        "stockfish/stockfish-macos-m1-apple-silicon",
        "stockfish_macos_silicon",
        "4e23165eb8f353c221ff7ab6716f0a160c3993dadf90d0c0ad982a7ade4091c9",
    ),
    "macos-intel": Asset(
        "macos-intel",
        "stockfish-macos-x86-64-avx2.tar",
        "stockfish/stockfish-macos-x86-64-avx2",
        "stockfish_macos_intel",
        "5438769678323fecbb582a6c232a0e905490bc568088e4d4f8bbb9f1fb530245",
    ),
    "linux": Asset(
        "linux",
        "stockfish-ubuntu-x86-64-avx2.tar",
        "stockfish/stockfish-ubuntu-x86-64-avx2",
        "stockfish_linux",
        "09e953222dbe80aaea5c33dab265413b295cb8376418445c877708c61e31987d",
    ),
    "windows": Asset(
        "windows",
        "stockfish-windows-x86-64-avx2.zip",
        "stockfish/stockfish-windows-x86-64-avx2.exe",
        "stockfish_windows.exe",
        "92a77f8d8116b4331696eeb7b232bd03db30d6641a6ce1be1759478b8931d28b",
    ),
}


class FetchError(Exception):
    pass


def detect_platform() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arm = "arm" in machine or "aarch64" in machine
    if system.startswith("darwin"):
        return "macos-silicon" if arm else "macos-intel"
    if system.startswith("win"):
        return "windows"
    if arm:
        raise FetchError(
            "No official Stockfish build for Linux ARM; build from source and set the "
            "engine path in Settings"
        )
    return "linux"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stamp_path(dest: Path, asset: Asset) -> Path:
    return dest / f".{asset.target}.sha256"


def is_installed(dest: Path, asset: Asset) -> bool:
    """True if the binary is present and matches the checksum recorded when it was installed."""
    binary = dest / asset.target
    stamp = _stamp_path(dest, asset)
    if not binary.exists() or not stamp.exists():
        return False
    recorded = stamp.read_text().strip().split()
    return (
        len(recorded) == 2 and recorded[0] == asset.sha256 and recorded[1] == _sha256_file(binary)
    )


def download(
    client: httpx.Client, asset: Asset, progress: Callable[[int, int], None] | None = None
) -> bytes:
    url = BASE_URL + asset.archive
    buf = io.BytesIO()
    with client.stream("GET", url, follow_redirects=True) as r:
        if r.status_code != 200:
            raise FetchError(f"{url} returned HTTP {r.status_code}")
        total = int(r.headers.get("Content-Length", "0"))
        done = 0
        for chunk in r.iter_bytes(1 << 20):
            buf.write(chunk)
            done += len(chunk)
            if progress:
                progress(done, total)
    data = buf.getvalue()
    actual = _sha256(data)
    if actual != asset.sha256:
        raise FetchError(
            f"{asset.archive}: sha256 mismatch\n  expected {asset.sha256}\n  got      {actual}"
        )
    return data


def extract(data: bytes, asset: Asset) -> bytes:
    if asset.archive.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            try:
                return zf.read(asset.member)
            except KeyError as e:
                raise FetchError(f"{asset.member} not found in {asset.archive}") from e
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
        try:
            member = tf.getmember(asset.member)
        except KeyError as e:
            raise FetchError(f"{asset.member} not found in {asset.archive}") from e
        f = tf.extractfile(member)
        if f is None:
            raise FetchError(f"{asset.member} is not a regular file")
        return f.read()


def install(dest: Path, asset: Asset, binary: bytes) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / asset.target
    tmp = target.with_name(target.name + ".part")
    tmp.write_bytes(binary)
    if not asset.target.endswith(".exe"):
        tmp.chmod(tmp.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    os.replace(tmp, target)
    _stamp_path(dest, asset).write_text(f"{asset.sha256} {_sha256(binary)}\n")
    return target


def fetch(
    keys: Iterable[str],
    dest: Path,
    *,
    force: bool = False,
    client: httpx.Client | None = None,
    log: Callable[[str], None] = print,
) -> list[Path]:
    own_client = client is None
    client = client or httpx.Client(
        timeout=120.0, headers={"User-Agent": "LocalChessAnalyzer fetch-stockfish"}
    )
    installed: list[Path] = []
    try:
        for key in keys:
            asset = ASSETS[key]
            if not force and is_installed(dest, asset):
                log(f"{asset.target}: already installed")
                installed.append(dest / asset.target)
                continue
            log(f"{asset.target}: downloading {asset.archive} ({RELEASE})")
            last = [-1]

            def progress(done: int, total: int, _last=last) -> None:
                pct = int(100 * done / total) if total else 0
                if pct // 10 != _last[0] // 10:
                    _last[0] = pct
                    log(f"  {done / 1048576:6.1f} MB  {pct:3d}%")

            data = download(client, asset, progress)
            binary = extract(data, asset)
            path = install(dest, asset, binary)
            log(f"{asset.target}: installed ({len(binary) / 1048576:.1f} MB)")
            installed.append(path)
    finally:
        if own_client:
            client.close()
    return installed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--platform",
        default="auto",
        choices=["auto", "all", *ASSETS],
        help="which build to fetch (default: the current machine's)",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="directory to install into (default: <repo>/stockfish)",
    )
    parser.add_argument(
        "--force", action="store_true", help="re-download even if already installed"
    )
    args = parser.parse_args(argv)

    dest = args.dest or (Paths().base_dir() / "stockfish")
    try:
        keys = (
            list(ASSETS)
            if args.platform == "all"
            else [detect_platform() if args.platform == "auto" else args.platform]
        )
        fetch(keys, dest, force=args.force)
    except (FetchError, httpx.HTTPError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
