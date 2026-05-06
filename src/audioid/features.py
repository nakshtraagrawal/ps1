from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from .fingerprint import fingerprint


@dataclass
class FeaturePacket:
    """Unified output container for interchangeable feature extractors."""

    feature_type: str
    payload: dict


class FeatureExtractor(Protocol):
    """Abstract feature extraction contract."""

    def extract(self, signal: np.ndarray) -> FeaturePacket:
        ...


class FingerprintFeatureExtractor:
    """
    Baseline deterministic extractor used by the matcher/indexer.
    Produces spectrogram, constellation peaks, and pairwise hashes.
    """

    def extract(self, signal: np.ndarray) -> FeaturePacket:
        spec, peaks, hashes = fingerprint(signal)
        return FeaturePacket(
            feature_type="fingerprint",
            payload={"spectrogram": spec, "peaks": peaks, "hashes": hashes},
        )


class SpectralEmbeddingExtractor:
    """
    Paper-ready embedding interface.

    This module defines where learned embeddings would plug in
    (e.g., CNN/transformer embeddings for ANN search) without
    changing ingestion/matching API surfaces.
    """

    def extract(self, signal: np.ndarray) -> FeaturePacket:
        # Placeholder embedding: compact spectral summary vector.
        # Kept intentionally simple as a baseline for architecture demonstration.
        embedding = np.array(
            [float(np.mean(signal)), float(np.std(signal)), float(np.max(np.abs(signal)))],
            dtype=np.float32,
        )
        return FeaturePacket(feature_type="embedding", payload={"vector": embedding})

