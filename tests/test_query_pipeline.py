"""Tests for invalid query rejection in pipeline service."""

from __future__ import annotations

import numpy as np

from src.audioid.service import AudioIdentifierService


def test_query_pipeline_rejects_silent_signal() -> None:
    """Confirm silent query is rejected with structured error."""
    service = AudioIdentifierService()
    service.payload = {"index": {}, "songs": {}}
    service.ready = True
    silent = np.zeros(11025, dtype=np.float32)
    result = service.identify_signal(signal=silent, sr=11025, threshold=0.4)
    assert result.get("error_code") == "INVALID_QUERY", "Expected invalid-query error code for silence"
