"""Filesystem layout for dev checkouts and frozen (PyInstaller) bundles."""

from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

# Candidate Stockfish binary names per platform/arch, most preferred first.
_ENGINE_CANDIDATES: dict[tuple[str, str], list[str]] = {
    ("darwin", "arm"): ["stockfish_macos_silicon", "stockfish_macos_arm64", "stockfish"],
    ("darwin", "x86"): ["stockfish_macos_intel", "stockfish_macos_x86_64", "stockfish"],
    ("windows", "any"): ["stockfish_windows.exe", "stockfish.exe"],
    ("linux", "arm"): ["stockfish_linux_arm64", "stockfish_linux", "stockfish"],
    ("linux", "x86"): ["stockfish_linux", "stockfish_linux_x86_64", "stockfish"],
}


def _platform_key() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "arm" if ("arm" in machine or "aarch64" in machine) else "x86"
    if system.startswith("win"):
        return ("windows", "any")
    if system.startswith("darwin"):
        return ("darwin", arch)
    return ("linux", arch)


@dataclass(frozen=True)
class Paths:
    """Resolves runtime directories.

    Resolution order for the base: explicit `base` (tests) > `LCA_BASE_DIR` env (Docker) >
    the executable's folder when frozen (desktop bundle) > the repository root (dev).
    """

    base: Path | None = None

    def base_dir(self) -> Path:
        if self.base is not None:
            return self.base
        env = os.environ.get("LCA_BASE_DIR")
        if env:
            return Path(env)
        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent
        # backend/lca/config.py -> backend/lca -> backend -> repo root
        return Path(__file__).resolve().parents[2]

    def resource_dir(self) -> Path:
        """Where packaged resources live (PyInstaller `_internal`/`_MEIPASS`), else base."""
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        internal = self.base_dir() / "_internal"
        return internal if internal.exists() else self.base_dir()

    def data_dir(self) -> Path:
        d = self.base_dir() / "data"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def db_path(self) -> Path:
        return self.data_dir() / "lca.db"

    def frontend_dist_dir(self) -> Path | None:
        candidates = [
            self.base_dir() / "frontend_dist",
            self.base_dir() / "frontend" / "dist",
            self.resource_dir() / "frontend_dist",
        ]
        for c in candidates:
            if (c / "index.html").exists():
                return c
        return None

    def openings_path(self) -> Path:
        return Path(__file__).resolve().parent / "data" / "openings.json"

    def default_engine_path(self) -> Path:
        names = _ENGINE_CANDIDATES[_platform_key()]
        search_dirs = [self.base_dir() / "stockfish", self.resource_dir() / "stockfish"]
        for name in names:
            for d in search_dirs:
                p = d / name
                if p.exists():
                    return p
        return search_dirs[0] / names[0]
