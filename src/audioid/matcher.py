from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .config import DEFAULT_CONFIDENCE_THRESHOLD, MIN_ALIGNED_HASHES


def match_query(
    query_hashes: list[tuple[int, int]],
    payload: dict[str, Any],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    index: dict[int, list[tuple[str, int]]] = payload["index"]
    songs: dict[str, dict[str, str]] = payload["songs"]
    offset_counts_by_song: dict[str, Counter[int]] = defaultdict(Counter)
    total_hits = 0

    for h, query_t in query_hashes:
        for song_id, song_t in index.get(h, []):
            offset = song_t - query_t
            offset_counts_by_song[song_id][offset] += 1
            total_hits += 1

    if not offset_counts_by_song or not query_hashes:
        return {"matched": False, "reason": "No Match Found", "confidence": 0.0}

    best_song_id = None
    best_offset_peak = 0
    best_offset = 0

    best_song_total_hits = 0
    for song_id, offset_counter in offset_counts_by_song.items():
        offset, peak = offset_counter.most_common(1)[0]
        if peak > best_offset_peak:
            best_song_id = song_id
            best_offset_peak = peak
            best_offset = offset
            best_song_total_hits = sum(offset_counter.values())

    if best_song_id is None:
        return {"matched": False, "reason": "No Match Found", "confidence": 0.0}

    # Confidence calibration:
    # - query_coverage rewards how much of query aligns to one song/offset
    # - peak_dominance penalizes diffuse/noisy candidate alignments
    query_coverage = best_offset_peak / max(1, len(query_hashes))
    peak_dominance = best_offset_peak / max(1, best_song_total_hits)
    confidence = 0.7 * query_coverage + 0.3 * peak_dominance

    meta = songs[best_song_id]
    matched = best_offset_peak > MIN_ALIGNED_HASHES and confidence >= confidence_threshold

    return {
        "matched": matched,
        "reason": None if matched else "Below confidence threshold",
        "song_id": best_song_id,
        "song": meta["title"],
        "artist": meta["artist"],
        "genre": meta["genre"],
        "offset_bin": best_offset,
        "aligned_matches": best_offset_peak,
        "total_query_hashes": len(query_hashes),
        "confidence": confidence,
        "total_hash_hits": total_hits,
    }

