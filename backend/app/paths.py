from pathlib import Path
import sys
import platform


def base_dir() -> Path:
    """
    Resolve the base directory for runtime assets (data, stockfish, frontend_dist).
    - In a frozen/packaged app, this is the directory containing the executable.
    - In development, this is the repository root directory.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    # backend/app/paths.py -> backend/app -> backend -> repo root
    return Path(__file__).resolve().parents[2]


def resource_base_dir() -> Path:
    """
    Base directory where packaged resources live.
    - PyInstaller onefile: sys._MEIPASS temp folder (if present)
    - PyInstaller onedir: use '<base_dir>/_internal' if it exists
    - Dev: repo root
    """
    # PyInstaller onefile extraction dir
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    base = base_dir()
    internal = base / "_internal"
    if internal.exists():
        return internal
    return base


def data_dir() -> Path:
    """
    Ensure and return the persistent data directory.
    """
    d = base_dir() / "data"
    (d / "analysis").mkdir(parents=True, exist_ok=True)
    return d


def frontend_dist_dir() -> Path:
    """
    Directory containing built frontend assets.
    - Prefer 'frontend_dist' next to the executable (packaged).
    - Fallback to 'frontend/dist' (dev layout).
    - Finally, look under PyInstaller resource dir ('_internal/frontend_dist').
    """
    base = base_dir()
    primary = base / "frontend_dist"
    if primary.exists():
        return primary
    fallback = base / "frontend" / "dist"
    if fallback.exists():
        return fallback
    # PyInstaller places datas under _internal in some configurations
    internal = resource_base_dir() / "frontend_dist"
    return internal


def stockfish_binary_path() -> Path:
    """
    Resolve the expected Stockfish binary path, selecting the right build for the OS/arch.
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Candidate file names by platform/arch (ordered by preference)
    candidates = []
    if system.startswith("darwin"):  # macOS
        if "arm" in machine or "aarch64" in machine:
            candidates = [
                "stockfish_macos_silicon",   # your canonical name
                # fallbacks
                "stockfish_macos_arm64",
                "stockfish_arm64",
                "stockfish_binary",
                "stockfish",
            ]
        else:
            candidates = [
                "stockfish_macos_intel",     # your canonical name
                # fallbacks
                "stockfish_macos_x86_64",
                "stockfish_x86_64",
                "stockfish_binary",
                "stockfish",
            ]
    elif system.startswith("win"):  # Windows
        candidates = [
            "stockfish_windows.exe",        # your canonical name
            # fallbacks
            "stockfish.exe",
            "stockfish_windows_x86_64.exe",
            "stockfish_binary.exe",
            "stockfish_binary",
        ]
    else:  # Linux and others
        if "arm" in machine or "aarch64" in machine:
            candidates = [
                # you didn't specify arm linux; try common names
                "stockfish_linux_arm64",
                "stockfish_arm64",
                "stockfish_linux",
                "stockfish_binary",
                "stockfish",
            ]
        else:
            candidates = [
                "stockfish_linux",           # your canonical name
                # fallbacks
                "stockfish_linux_x86_64",
                "stockfish_x86_64",
                "stockfish_binary",
                "stockfish",
            ]

    # Search locations: next to exe, then packaged resources (_internal)
    stockfish_dir_primary = base_dir() / "stockfish"
    stockfish_dir_internal = resource_base_dir() / "stockfish"
    for name in candidates:
        p = stockfish_dir_primary / name
        if p.exists():
            return p
        p2 = stockfish_dir_internal / name
        if p2.exists():
            return p2

    # Fallback to default path to aid error messages
    return stockfish_dir_primary / "stockfish_binary"


