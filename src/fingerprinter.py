"""Fingerprinter facade for STFT peak-hash extraction."""

from __future__ import annotations

import numpy as np

from src.audioid.fingerprint import fingerprint, hashes_only, log_spectrogram


def fingerprint_signal(signal: np.ndarray) -> tuple[np.ndarray, list[object], list[tuple[int, int]]]:
    """Run full fingerprint extraction for one normalized signal."""
    return fingerprint(signal)


def fingerprint_hashes(signal: np.ndarray) -> list[tuple[int, int]]:
    """Return only hash tuples for indexing and matching."""
    return hashes_only(signal)


def spectrogram(signal: np.ndarray) -> np.ndarray:
    """Return log spectrogram used for visualization/debug."""
    return log_spectrogram(signal)
