"""Single entrypoint for local application startup."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """Start the FastAPI service on configurable local port."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.app:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    main()
