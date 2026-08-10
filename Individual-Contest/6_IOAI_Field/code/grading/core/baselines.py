"""Simple models used to explain the scoring behavior."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


class ConstModel:
    def __init__(self, value: float = 0.0):
        self.value = float(value)

    def __call__(self, xy):
        return np.full((xy.shape[0],), self.value, dtype=np.float32)


class RandomMaskModel:
    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)

    def __call__(self, xy):
        return self.rng.random(xy.shape[0]).astype(np.float32)


class TinyDropoutMLP(nn.Module):
    def __init__(self, hidden=(16, 16), p=0.2):
        super().__init__()
        layers = []
        in_dim = 2
        for h in hidden:
            layers.extend((nn.Linear(in_dim, h), nn.Tanh(), nn.Dropout(p)))
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def make_random_tiny_dropout(seed: int = 0, hidden=(16, 16), p=0.2):
    torch.manual_seed(seed)
    return TinyDropoutMLP(hidden=hidden, p=p)


__all__ = [
    "ConstModel",
    "RandomMaskModel",
    "TinyDropoutMLP",
    "make_random_tiny_dropout",
]
