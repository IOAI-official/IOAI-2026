"""Public helpers for the IOAI Field notebook.

The pipeline modules (``problem`` and ``metrics.field_score``) are canonical.
This package provides the stable, participant-facing API used by
``IOAIField.ipynb`` without duplicating the task implementation.
"""

from .field_fn import FieldConfig, entropy_from_model, field_masks, field_value
from .data import SamplingConfig, make_batch, sample_points
from .models import TinyMLP, count_params
from .train import eval_loss, train_one_epoch
from .visualize import render_heatmap, render_masks
from .metrics import (
    compute_metrics,
    format_metrics_explanation,
    print_metrics_explanation,
)
from .eval import EvalConfig, evaluate_model
from .baselines import ConstModel, RandomMaskModel, make_random_tiny_dropout

__all__ = [
    "FieldConfig",
    "field_value",
    "field_masks",
    "entropy_from_model",
    "SamplingConfig",
    "sample_points",
    "make_batch",
    "TinyMLP",
    "count_params",
    "train_one_epoch",
    "eval_loss",
    "render_heatmap",
    "render_masks",
    "compute_metrics",
    "format_metrics_explanation",
    "print_metrics_explanation",
    "evaluate_model",
    "EvalConfig",
    "ConstModel",
    "RandomMaskModel",
    "make_random_tiny_dropout",
]
