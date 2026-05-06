"""Indexing facade for offline build and persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.audioid.indexer import build_index, load_index, save_index


def build_hash_index(dataset_dir: Path | None = None, max_files: int | None = None) -> dict[str, Any]:
    """Build an inverted hash index from dataset audio files."""
    if dataset_dir is None:
        return build_index(max_files=max_files)
    return build_index(dataset_dir=dataset_dir, max_files=max_files)


def persist_hash_index(payload: dict[str, Any], index_path: Path | None = None) -> None:
    """Persist index payload to disk."""
    if index_path is None:
        save_index(payload)
    else:
        save_index(payload, index_path=index_path)


def restore_hash_index(index_path: Path | None = None) -> dict[str, Any]:
    """Load index payload from disk."""
    if index_path is None:
        return load_index()
    return load_index(index_path=index_path)
