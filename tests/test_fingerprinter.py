"""Unit tests for spectrogram hashing pipeline."""

from __future__ import annotations

import numpy as np

from src.fingerprinter import fingerprint_hashes


def test_fingerprint_generates_hashes_for_tone() -> None:
    """Verify that a non-silent tone generates at least one hash."""
    sample_rate = 11025
    time_axis = np.linspace(0, 2.0, int(sample_rate * 2.0), endpoint=False, dtype=np.float32)
    signal = 0.7 * np.sin(2.0 * np.pi * 440.0 * time_axis).astype(np.float32)
    hashes = fingerprint_hashes(signal)
    assert len(hashes) > 0, "Expected hashes for a valid tonal signal"
