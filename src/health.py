"""Health status helpers for service readiness checks."""

from __future__ import annotations

from typing import Any


def build_health_status(payload: dict[str, Any], ready: bool) -> dict[str, Any]:
    """Create a consistent health payload for API responses."""
    song_count = len(payload.get("songs", {}))
    return {"ready": ready, "index_loaded": bool(payload), "songs_indexed": song_count}
