"""Lightweight integration test for end-to-end index + identify flow."""

from __future__ import annotations

import soundfile as sf

from src.audioid.config import SAMPLE_RATE
from src.audioid.indexer import build_index
from src.audioid.service import AudioIdentifierService


def test_end_to_end_identifies_dataset_song() -> None:
    """Build small index subset and identify one known track."""
    payload = build_index(max_files=1)
    assert len(payload["songs"]) == 1, "Expected one indexed song in integration setup"
    song_id = next(iter(payload["songs"].keys()))
    song_path = payload["songs"][song_id]["path"]
    service = AudioIdentifierService()
    service.payload = payload
    service.ready = True
    signal, sample_rate = sf.read(song_path)
    max_samples = int(SAMPLE_RATE * 10.0)
    if signal.ndim > 1:
        signal = signal[:, 0]
    short_signal = signal[:max_samples]
    result = service.identify_signal(signal=short_signal, sr=sample_rate, threshold=0.0)
    assert result.get("song_id") == song_id, "Expected indexed song to self-identify correctly"
