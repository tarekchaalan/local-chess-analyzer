import webbrowser
import uvicorn
from backend.app.main import app

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 42069


def main():
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


