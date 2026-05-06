from __future__ import annotations

import numpy as np

from .config import MAX_QUERY_SECONDS, MIN_QUERY_SECONDS, SAMPLE_RATE, SILENCE_RMS_THRESHOLD


def validate_query(signal: np.ndarray, sr: int) -> tuple[bool, str]:
    if sr <= 0:
        return False, "Invalid sample rate"
    duration = len(signal) / sr
    if duration < MIN_QUERY_SECONDS:
        return False, "Query too short. Provide at least 1 second of audio."
    if duration > MAX_QUERY_SECONDS:
        return False, "Query too long. Provide at most 10 seconds."
    rms = float(np.sqrt(np.mean(np.square(signal.astype(np.float32)))))
    if rms < SILENCE_RMS_THRESHOLD:
        return False, "Query appears silent. Please upload audible audio."
    return True, ""

