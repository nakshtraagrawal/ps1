"""Matcher facade for offset-histogram confidence scoring."""

from __future__ import annotations

from typing import Any

from src.audioid.matcher import match_query


def identify_from_hashes(
    query_hashes: list[tuple[int, int]],
    payload: dict[str, Any],
    confidence_threshold: float,
) -> dict[str, Any]:
    """Run candidate selection and confidence scoring on query hashes."""
    return match_query(query_hashes, payload, confidence_threshold=confidence_threshold)
