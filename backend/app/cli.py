import webbrowser
import uvicorn
import platform
import subprocess
from backend.app.main import app
from backend.app.paths import base_dir, resource_base_dir

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 42069


def main():
    # macOS: after first user approval, clear quarantine on the whole bundle to avoid repeated prompts
    try:
        if platform.system().lower().startswith("darwin"):
            targets = {base_dir(), resource_base_dir()}
            for t in targets:
                try:
                    subprocess.run(
                        ["xattr", "-dr", "com.apple.quarantine", str(t)],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except Exception:
                    pass
    except Exception:
        pass

    url = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/"
    try:
        webbrowser.open(url)
    except Exception:
        pass
    uvicorn.run(
        app,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()


