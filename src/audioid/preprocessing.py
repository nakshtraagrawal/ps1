from pathlib import Path
from typing import Tuple

import numpy as np
import soundfile as sf

from .config import SAMPLE_RATE


def load_audio_standard(path: Path | str, target_sr: int = SAMPLE_RATE) -> Tuple[np.ndarray, int]:
    """Decode audio and force mono PCM at target sample rate."""
    try:
        signal, sr = sf.read(str(path), always_2d=False)
    except Exception as e:
        raise RuntimeError(f"Failed to decode audio: {path}") from e

    if isinstance(signal, np.ndarray) and signal.ndim > 1:
        signal = np.mean(signal, axis=1)
    signal = np.asarray(signal, dtype=np.float32)

    if sr != target_sr:
        import librosa

        signal = librosa.resample(signal, orig_sr=sr, target_sr=target_sr).astype(np.float32)
        sr = target_sr

    return signal, sr


def load_audio_mono_22k(path: Path | str) -> Tuple[np.ndarray, int]:
    """Backward-compatible alias used by older modules."""
    return load_audio_standard(path, target_sr=SAMPLE_RATE)

