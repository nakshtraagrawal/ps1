"""End-to-end query orchestration facade."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.audioid.service import AudioIdentifierService


class QueryPipeline:
    """Thin orchestration class for query identification calls."""

    def __init__(self) -> None:
        self._service = AudioIdentifierService()
        self._service.load_or_build()

    def identify_file(self, file_path: Path, threshold: float) -> dict[str, Any]:
        """Identify best match for a local audio file."""
        return self._service.identify_file(file_path=file_path, threshold=threshold)

    def identify_bytes(self, payload: bytes, threshold: float) -> dict[str, Any]:
        """Identify best match for uploaded audio bytes."""
        return self._service.identify_bytes(file_bytes=payload, threshold=threshold)
