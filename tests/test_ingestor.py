"""Tests for metadata ingestion and fallback behavior."""

from __future__ import annotations

from pathlib import Path

from src.ingestor import load_dataset_records


def test_ingestor_handles_missing_dataset_path() -> None:
    """Verify loader reports skipped rows when dataset path is invalid."""
    records, skipped = load_dataset_records(dataset_dir=Path("does_not_exist"))
    assert len(records) == 0, "Expected zero records for missing dataset directory"
    assert isinstance(skipped, list), "Expected skipped diagnostics list"
