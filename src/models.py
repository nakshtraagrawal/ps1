"""Domain models for metadata and match responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchResult:
    """Structured match payload used for API-facing responses."""

    song_id: str
    song: str
    artist: str
    confidence: float
    matched: bool
