"""Stable public facade for the protected field runtime."""

from problem import (
    entropy_from_model,
    field_masks,
    field_value,
    make_field_config,
)


def FieldConfig(**kwargs):
    """Create a field configuration.

    Kept as a constructor-shaped compatibility API for the public notebook.
    The concrete dataclass lives in the protected runtime.
    """

    return make_field_config(**kwargs)


__all__ = [
    "FieldConfig",
    "entropy_from_model",
    "field_masks",
    "field_value",
]
