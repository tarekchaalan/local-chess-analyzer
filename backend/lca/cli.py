"""Desktop entrypoint: start the server on localhost and open the browser."""

from __future__ import annotations

import logging
import platform
import subprocess
import threading
import time
import webbrowser

import uvicorn

# Absolute imports: PyInstaller runs this file as a top-level script.
from lca.config import Paths
from lca.main import create_app

HOST = "127.0.0.1"
PORT = 42069


def _clear_macos_quarantine(paths: Paths) -> None:
    """After the user approves the app once, stop Gatekeeper re-prompting for bundled files."""
    if not platform.system().lower().startswith("darwin"):
        return
    for target in {paths.base_dir(), paths.resource_dir()}:
        subprocess.run(
            ["xattr", "-dr", "com.apple.quarantine", str(target)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _open_browser_later(url: str, delay: float = 1.0) -> None:
    def _open() -> None:
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001 - opening a browser is best effort
            pass

    threading.Thread(target=_open, daemon=True).start()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    paths = Paths()
    _clear_macos_quarantine(paths)
    app = create_app(paths)
    url = f"http://{HOST}:{PORT}/"
    print(f"Local Chess Analyzer running at {url}  (Ctrl+C to stop)")
    _open_browser_later(url)
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
