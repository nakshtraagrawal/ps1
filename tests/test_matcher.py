"""Unit tests for offset-histogram matching."""

from __future__ import annotations

from src.matcher import identify_from_hashes


def test_matcher_prefers_song_with_stronger_peak() -> None:
    """Ensure candidate with strongest aligned offset wins."""
    payload = {
        "index": {
            11: [("song_a", 10), ("song_b", 40)],
            12: [("song_a", 15)],
            13: [("song_a", 20)],
        },
        "songs": {
            "song_a": {"title": "song_a", "artist": "A", "genre": "x"},
            "song_b": {"title": "song_b", "artist": "B", "genre": "y"},
        },
    }
    query_hashes = [(11, 5), (12, 10), (13, 15)]
    result = identify_from_hashes(query_hashes=query_hashes, payload=payload, confidence_threshold=0.0)
    assert result["song_id"] == "song_a", "Expected song_a to win via consistent offset alignment"
