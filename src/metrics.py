"""Metrics helpers for latency and evaluation calculations."""

from __future__ import annotations


def precision(tp: int, fp: int) -> float:
    """Compute precision metric from true/false positives."""
    return tp / max(1, tp + fp)


def recall(tp: int, fn: int) -> float:
    """Compute recall metric from true positives/false negatives."""
    return tp / max(1, tp + fn)


def f1_score(metric_precision: float, metric_recall: float) -> float:
    """Compute harmonic mean for precision and recall."""
    return (2 * metric_precision * metric_recall) / max(1e-8, (metric_precision + metric_recall))
