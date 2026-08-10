"""Public evaluation API backed by the canonical metric."""

from metrics.field_score import EvalConfig, evaluate_model

__all__ = ["EvalConfig", "evaluate_model"]
