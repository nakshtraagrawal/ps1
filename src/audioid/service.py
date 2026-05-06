from __future__ import annotations

import io
import time
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from .config import INDEX_PATH, MAX_QUERY_SECONDS, SAMPLE_RATE
from .fingerprint import fingerprint
from .indexer import build_index, load_index, save_index
from .matcher import match_query
from .metadata import load_song_records
from .preprocessing import load_audio_standard
from .query_validation import validate_query


class AudioIdentifierService:
    def __init__(self) -> None:
        self.payload: dict[str, Any] = {}
        self.ready = False

    def load_or_build(self) -> None:
        expected_song_count = self._expected_song_count()
        if INDEX_PATH.exists():
            self.payload = load_index()
            indexed_song_count = len(self.payload.get("songs", {}))
            # Auto-recover from accidental partial indexes (e.g., built with --limit).
            if indexed_song_count < max(1, expected_song_count // 2):
                self.payload = build_index()
                save_index(self.payload)
        else:
            self.payload = build_index()
            save_index(self.payload)
        self.ready = True

    def _expected_song_count(self) -> int:
        records, _ = load_song_records()
        return len(records)

    def identify_file(self, file_path: Path, threshold: float) -> dict[str, Any]:
        try:
            signal, sr = load_audio_standard(file_path)
        except Exception as e:
            raise ValueError("Could not decode audio file. Use a valid WAV/MP3 clip.") from e
        return self.identify_signal(signal, sr, threshold)

    def identify_bytes(self, file_bytes: bytes, threshold: float) -> dict[str, Any]:
        try:
            signal, sr = sf.read(io.BytesIO(file_bytes))
            signal, sr = load_audio_standard_signal(signal, sr)
        except Exception as e:
            raise ValueError("Could not decode uploaded audio. Try a WAV file.") from e
        return self.identify_signal(signal, sr, threshold)

    def identify_signal(self, signal, sr: int, threshold: float) -> dict[str, Any]:
        start = time.perf_counter()
        signal, sr = load_audio_standard_signal(signal, sr)
        signal, was_trimmed = trim_query_to_max_duration(signal=signal, sr=sr)
        ok, reason = validate_query(signal, sr)
        if not ok:
            return {
                "matched": False,
                "error_code": "INVALID_QUERY",
                "error": reason,
                "confidence": 0.0,
                "latency": f"{time.perf_counter() - start:.3f}s",
            }

        t_extract_start = time.perf_counter()
        _, _, query_hashes = fingerprint(signal.astype(np.float32))
        t_extract_end = time.perf_counter()
        t_match_start = time.perf_counter()
        result = match_query(query_hashes, self.payload, confidence_threshold=threshold)
        t_match_end = time.perf_counter()
        result["latency"] = f"{time.perf_counter() - start:.3f}s"
        result["timings_ms"] = {
            "feature_extraction": round((t_extract_end - t_extract_start) * 1000, 2),
            "matching": round((t_match_end - t_match_start) * 1000, 2),
            "total": round((time.perf_counter() - start) * 1000, 2),
        }
        result["query_trimmed"] = was_trimmed
        return result


def load_audio_standard_signal(signal, sr: int):
    if isinstance(signal, np.ndarray) and signal.ndim > 1:
        signal = np.mean(signal, axis=1)
    signal = np.asarray(signal, dtype=np.float32)
    if sr != SAMPLE_RATE:
        import librosa

        signal = librosa.resample(signal, orig_sr=sr, target_sr=SAMPLE_RATE).astype(np.float32)
        sr = SAMPLE_RATE
    return signal, sr


def trim_query_to_max_duration(signal: np.ndarray, sr: int) -> tuple[np.ndarray, bool]:
    """Clamp long inputs to max query length for robust identification."""
    max_samples = int(MAX_QUERY_SECONDS * sr)
    if len(signal) <= max_samples:
        return signal, False
    return signal[:max_samples], True

