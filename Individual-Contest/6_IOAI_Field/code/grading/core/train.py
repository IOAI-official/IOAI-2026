"""Small training helpers for notebook experiments."""

from __future__ import annotations

from typing import Dict

import torch


def mse_loss(pred, target):
    return ((pred - target) ** 2).mean()


def train_one_epoch(model, optimizer, xy, y, device="cpu") -> Dict[str, float]:
    model.train()
    xy_t = torch.tensor(xy, dtype=torch.float32, device=device)
    y_t = torch.tensor(y, dtype=torch.float32, device=device).unsqueeze(-1)
    optimizer.zero_grad()
    pred = model(xy_t)
    loss = mse_loss(pred, y_t)
    loss.backward()
    optimizer.step()
    return {"loss": float(loss.detach().cpu().item())}


def eval_loss(model, xy, y, device="cpu") -> float:
    model.eval()
    with torch.no_grad():
        xy_t = torch.tensor(xy, dtype=torch.float32, device=device)
        y_t = torch.tensor(y, dtype=torch.float32, device=device).unsqueeze(-1)
        loss = mse_loss(model(xy_t), y_t)
    return float(loss.detach().cpu().item())


__all__ = ["eval_loss", "mse_loss", "train_one_epoch"]
