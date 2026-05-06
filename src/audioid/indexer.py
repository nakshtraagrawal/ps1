from __future__ import annotations

import pickle
from collections import defaultdict
from pathlib import Path
from typing import Any

from .config import DATASET_DIR, INDEX_PATH
from .fingerprint import hashes_only
from .metadata import load_song_records
from .preprocessing import load_audio_standard


def build_index(dataset_dir: Path = DATASET_DIR, max_files: int | None = None) -> dict[str, Any]:
    inverted_index: dict[int, list[tuple[str, int]]] = defaultdict(list)
    song_meta: dict[str, dict[str, str | float]] = {}
    song_hash_counts: dict[str, int] = {}
    skipped_decode: list[dict[str, str]] = []

    records, skipped_metadata = load_song_records(dataset_dir=dataset_dir)
    processed = 0
    for meta in records:
        try:
            signal, _ = load_audio_standard(meta.path)
        except Exception as e:
            skipped_decode.append({"song_id": meta.song_id, "path": meta.path, "error": str(e)})
            continue
        hashes = hashes_only(signal)
        song_meta[meta.song_id] = {
            "song_id": meta.song_id,
            "title": meta.title,
            "artist": meta.artist,
            "duration": meta.duration,
            "genre": meta.genre,
            "path": meta.path,
        }
        song_hash_counts[meta.song_id] = len(hashes)
        for h, t in hashes:
            inverted_index[h].append((meta.song_id, t))
        processed += 1
        if max_files is not None and processed >= max_files:
            break

    payload = {
        "index": dict(inverted_index),
        "songs": song_meta,
        "song_hash_counts": song_hash_counts,
        "skipped_metadata": skipped_metadata,
        "skipped_decode": skipped_decode,
    }
    return payload


def save_index(payload: dict[str, Any], index_path: Path = INDEX_PATH) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("wb") as f:
        pickle.dump(payload, f)


def load_index(index_path: Path = INDEX_PATH) -> dict[str, Any]:
    with index_path.open("rb") as f:
        return pickle.load(f)

