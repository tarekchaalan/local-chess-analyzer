import hashlib
import io
import os
import tarfile
import zipfile
from dataclasses import replace

import httpx
import pytest

from lca.tools import fetch_stockfish as fs


def _tar_with(member: str, payload: bytes) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        info = tarfile.TarInfo(member)
        info.size = len(payload)
        tf.addfile(info, io.BytesIO(payload))
    return buf.getvalue()


def _zip_with(member: str, payload: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(member, payload)
    return buf.getvalue()


@pytest.fixture
def fake_assets(monkeypatch):
    """Replace the pinned asset table with tiny fake archives served by a MockTransport."""
    linux_bin = b"#!/bin/sh\necho fake-stockfish\n"
    win_bin = b"MZfake"
    linux_tar = _tar_with("stockfish/stockfish-ubuntu-x86-64-avx2", linux_bin)
    win_zip = _zip_with("stockfish/stockfish-windows-x86-64-avx2.exe", win_bin)
    assets = {
        "linux": replace(fs.ASSETS["linux"], sha256=hashlib.sha256(linux_tar).hexdigest()),
        "windows": replace(fs.ASSETS["windows"], sha256=hashlib.sha256(win_zip).hexdigest()),
        "bad": replace(
            fs.ASSETS["linux"],
            key="bad",
            archive="bad.tar",
            target="stockfish_bad",
            sha256="0" * 64,
        ),
    }
    monkeypatch.setattr(fs, "ASSETS", assets)
    served = {
        "stockfish-ubuntu-x86-64-avx2.tar": linux_tar,
        "stockfish-windows-x86-64-avx2.zip": win_zip,
        "bad.tar": linux_tar,
    }
    hits = []

    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1]
        hits.append(name)
        if name not in served:
            return httpx.Response(404)
        return httpx.Response(
            200, content=served[name], headers={"Content-Length": str(len(served[name]))}
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    return client, hits, linux_bin, win_bin


def test_fetch_installs_executable_and_stamp(tmp_path, fake_assets):
    client, hits, linux_bin, _ = fake_assets
    paths = fs.fetch(["linux"], tmp_path, client=client, log=lambda _m: None)
    target = tmp_path / "stockfish_linux"
    assert paths == [target]
    assert target.read_bytes() == linux_bin
    assert os.access(target, os.X_OK)
    assert (tmp_path / ".stockfish_linux.sha256").exists()
    assert fs.is_installed(tmp_path, fs.ASSETS["linux"])


def test_fetch_skips_when_installed_and_force_redownloads(tmp_path, fake_assets):
    client, hits, _, _ = fake_assets
    fs.fetch(["linux"], tmp_path, client=client, log=lambda _m: None)
    fs.fetch(["linux"], tmp_path, client=client, log=lambda _m: None)
    assert hits.count("stockfish-ubuntu-x86-64-avx2.tar") == 1
    fs.fetch(["linux"], tmp_path, client=client, force=True, log=lambda _m: None)
    assert hits.count("stockfish-ubuntu-x86-64-avx2.tar") == 2


def test_tampered_binary_is_reinstalled(tmp_path, fake_assets):
    client, hits, linux_bin, _ = fake_assets
    fs.fetch(["linux"], tmp_path, client=client, log=lambda _m: None)
    (tmp_path / "stockfish_linux").write_bytes(b"corrupted")
    assert not fs.is_installed(tmp_path, fs.ASSETS["linux"])
    fs.fetch(["linux"], tmp_path, client=client, log=lambda _m: None)
    assert (tmp_path / "stockfish_linux").read_bytes() == linux_bin


def test_zip_assets_are_extracted(tmp_path, fake_assets):
    client, _, _, win_bin = fake_assets
    fs.fetch(["windows"], tmp_path, client=client, log=lambda _m: None)
    assert (tmp_path / "stockfish_windows.exe").read_bytes() == win_bin


def test_checksum_mismatch_installs_nothing(tmp_path, fake_assets):
    client, _, _, _ = fake_assets
    with pytest.raises(fs.FetchError, match="sha256 mismatch"):
        fs.fetch(["bad"], tmp_path, client=client, log=lambda _m: None)
    assert not (tmp_path / "stockfish_bad").exists()


def test_http_error(tmp_path, fake_assets, monkeypatch):
    client, _, _, _ = fake_assets
    monkeypatch.setitem(
        fs.ASSETS, "missing", replace(fs.ASSETS["linux"], key="missing", archive="nope.tar")
    )
    with pytest.raises(fs.FetchError, match="HTTP 404"):
        fs.fetch(["missing"], tmp_path, client=client, log=lambda _m: None)


def test_detect_platform_matches_config_candidates():
    key = fs.detect_platform()
    assert key in fs.ASSETS


def test_pinned_checksums_look_real():
    for asset in fs.ASSETS.values():
        assert len(asset.sha256) == 64 and set(asset.sha256) <= set("0123456789abcdef"), asset.key
