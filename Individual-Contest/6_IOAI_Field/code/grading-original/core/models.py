"""Small public models used by the baseline notebook."""

from __future__ import annotations

from typing import Callable, List

import torch
import torch.nn as nn

from metrics.field_score import count_params


class Sine(nn.Module):
    def forward(self, x):
        return torch.sin(x)


def _get_activation(act) -> Callable[[], nn.Module]:
    if isinstance(act, nn.Module):
        return act.__class__
    if callable(act) and act not in {str}:
        return act
    name = str(act).lower()
    if name in {"tanh", "t"}:
        return nn.Tanh
    if name in {"relu", "r"}:
        return nn.ReLU
    if name in {"sine", "sin"}:
        return Sine
    if name == "gelu":
        return nn.GELU
    raise ValueError(f"Unknown activation: {act}")


class TinyMLP(nn.Module):
    def __init__(self, hidden: List[int], activation="tanh", dropout: float = 0.0):
        super().__init__()
        layers = []
        in_dim = 2
        act = _get_activation(activation)
        for h in hidden:
            layers.append(nn.Linear(in_dim, h))
            layers.append(act())
            if dropout > 0.0:
                layers.append(nn.Dropout(dropout))
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


__all__ = ["Sine", "TinyMLP", "count_params"]
