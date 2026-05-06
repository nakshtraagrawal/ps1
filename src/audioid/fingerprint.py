from __future__ import annotations

from dataclasses import dataclass

import librosa
import numpy as np
from scipy.ndimage import maximum_filter

from .config import (
    FAN_OUT,
    HOP_LENGTH,
    N_FFT,
    PEAK_MIN_DB,
    PEAK_NEIGHBORHOOD,
    TARGET_FREQ_BINS,
    TARGET_TIME_BINS,
    WINDOW,
)


@dataclass(frozen=True)
class Peak:
    f_bin: int
    t_bin: int


def log_spectrogram(signal: np.ndarray) -> np.ndarray:
    stft = librosa.stft(signal, n_fft=N_FFT, hop_length=HOP_LENGTH, window=WINDOW)
    mag = np.abs(stft)
    return librosa.amplitude_to_db(mag, ref=np.max)


def constellation_peaks(log_spec: np.ndarray) -> list[Peak]:
    local_max = maximum_filter(log_spec, size=PEAK_NEIGHBORHOOD) == log_spec
    strong = log_spec >= PEAK_MIN_DB
    mask = local_max & strong
    freq_bins, time_bins = np.where(mask)
    return [Peak(int(f), int(t)) for f, t in zip(freq_bins, time_bins, strict=False)]


def generate_hashes(peaks: list[Peak]) -> list[tuple[int, int]]:
    """Return list of (hash, anchor_time_bin)."""
    if not peaks:
        return []
    ordered = sorted(peaks, key=lambda p: p.t_bin)
    result: list[tuple[int, int]] = []
    for i, anchor in enumerate(ordered):
        used = 0
        for target in ordered[i + 1 :]:
            delta_t = target.t_bin - anchor.t_bin
            delta_f = abs(target.f_bin - anchor.f_bin)
            if not (0 < delta_t <= TARGET_TIME_BINS and delta_f <= TARGET_FREQ_BINS):
                continue
            packed = ((anchor.f_bin & 0x3FF) << 22) | ((target.f_bin & 0x3FF) << 12) | (delta_t & 0xFFF)
            result.append((packed, anchor.t_bin))
            used += 1
            if used >= FAN_OUT:
                break
    return result


def fingerprint(signal: np.ndarray) -> tuple[np.ndarray, list[Peak], list[tuple[int, int]]]:
    spec = log_spectrogram(signal)
    peaks = constellation_peaks(spec)
    hashes = generate_hashes(peaks)
    return spec, peaks, hashes


def hashes_only(signal: np.ndarray) -> list[tuple[int, int]]:
    return fingerprint(signal)[2]

