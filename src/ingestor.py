"""Dataset ingestion facade with validation and skip-on-error semantics."""

from __future__ import annotations

from pathlib import Path

from src.audioid.metadata import SongRecord, load_song_records


def load_dataset_records(dataset_dir: Path | None = None) -> tuple[list[SongRecord], list[dict[str, str]]]:
    """Load validated dataset metadata from configured sources."""
    if dataset_dir is None:
        return load_song_records()
    return load_song_records(dataset_dir=dataset_dir)
