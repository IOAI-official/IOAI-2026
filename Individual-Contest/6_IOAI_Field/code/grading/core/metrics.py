"""Public metric helpers backed by the canonical metric."""

from metrics.field_score import compute_metrics, format_metrics_explanation


def print_metrics_explanation(scores) -> None:
    print(format_metrics_explanation(scores))


__all__ = [
    "compute_metrics",
    "format_metrics_explanation",
    "print_metrics_explanation",
]
