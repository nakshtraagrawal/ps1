from __future__ import annotations

import os
import threading
import webbrowser

import uvicorn


def open_browser(port: int) -> None:
    webbrowser.open(f"http://127.0.0.1:{port}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    threading.Timer(1.5, lambda: open_browser(port)).start()
    uvicorn.run("src.app:app", host="127.0.0.1", port=port, reload=False)

