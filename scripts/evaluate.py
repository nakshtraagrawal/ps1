from __future__ import annotations

import random

import numpy as np
import soundfile as sf

import sys
from pathlib import Path

# Ensure `ps1/` is on PYTHONPATH so imports like `src.audioid.*` work.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audioid.config import DATASET_DIR, DEFAULT_CONFIDENCE_THRESHOLD, SAMPLE_RATE
from src.audioid.service import AudioIdentifierService


def add_white_noise(signal: np.ndarray, snr_db: float = 8.0) -> np.ndarray:
    signal_power = np.mean(signal**2) + 1e-8
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), size=signal.shape)
    return (signal + noise).astype(np.float32)


def random_clip(signal: np.ndarray, seconds: int = 10) -> np.ndarray:
    clip_len = seconds * SAMPLE_RATE
    if len(signal) <= clip_len:
        return signal
    start = random.randint(0, len(signal) - clip_len)
    return signal[start : start + clip_len]


def main() -> None:
    service = AudioIdentifierService()
    service.load_or_build()

    files = sorted(DATASET_DIR.glob("*/*.wav"))
    sample_files = random.sample(files, k=min(30, len(files)))
    tp_clean = 0
    tp_noisy = 0
    fp_noisy = 0
    fn_noisy = 0

    for wav_path in sample_files:
        signal, sr = sf.read(wav_path)
        if signal.ndim > 1:
            signal = np.mean(signal, axis=1)
        if sr != SAMPLE_RATE:
            import librosa

            signal = librosa.resample(signal.astype(np.float32), orig_sr=sr, target_sr=SAMPLE_RATE)
        clip = random_clip(signal.astype(np.float32), seconds=10)
        noisy = add_white_noise(clip, snr_db=6.0)

        clean_result = service.identify_signal(clip, SAMPLE_RATE, DEFAULT_CONFIDENCE_THRESHOLD)
        noisy_result = service.identify_signal(noisy, SAMPLE_RATE, DEFAULT_CONFIDENCE_THRESHOLD)
        truth = wav_path.stem
        if clean_result.get("song") == truth:
            tp_clean += 1
        if noisy_result.get("song") == truth and noisy_result.get("matched"):
            tp_noisy += 1
        elif noisy_result.get("matched") and noisy_result.get("song") != truth:
            fp_noisy += 1
        else:
            fn_noisy += 1

    total = len(sample_files)
    precision = tp_noisy / max(1, tp_noisy + fp_noisy)
    recall = tp_noisy / max(1, tp_noisy + fn_noisy)
    f1 = (2 * precision * recall) / max(1e-8, (precision + recall))
    print(f"Clean top-1 accuracy: {tp_clean}/{total} = {tp_clean / max(1, total):.2%}")
    print(f"Noisy precision: {precision:.2%}")
    print(f"Noisy recall: {recall:.2%}")
    print(f"Noisy F1: {f1:.2%}")


if __name__ == "__main__":
    main()

