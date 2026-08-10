"""Visualization helpers for the public notebook."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from problem import field_masks, field_value, make_field_config


def render_heatmap(
    cfg=None,
    resolution: int = 200,
    log_scale: bool = False,
    vmin: float | None = None,
    vmax: float | None = None,
    robust: bool = True,
    exclude: tuple[str, ...] = (),
):
    if cfg is None:
        cfg = make_field_config()
    xs = np.linspace(cfg.x_min, cfg.x_max, resolution)
    ys = np.linspace(cfg.y_min, cfg.y_max, resolution)
    grid = np.stack(np.meshgrid(xs, ys), axis=-1)
    vals = field_value(grid, cfg)
    if exclude:
        masks = field_masks(grid, cfg)
        vals = vals.copy()
        for name in exclude:
            if name in masks:
                vals[masks[name]] = 0.0

    plot_vals = np.sign(vals) * np.log1p(np.abs(vals)) if log_scale else vals
    if robust and vmin is None and vmax is None:
        nonzero = plot_vals[np.abs(plot_vals) > 0]
        if nonzero.size:
            lo, hi = np.percentile(nonzero, [2, 98])
            if np.isfinite(lo) and np.isfinite(hi) and lo != hi:
                vmin, vmax = float(lo), float(hi)

    plt.figure(figsize=(6, 4))
    plt.imshow(
        plot_vals,
        origin="lower",
        extent=[cfg.x_min, cfg.x_max, cfg.y_min, cfg.y_max],
        aspect="auto",
        vmin=vmin,
        vmax=vmax,
    )
    plt.colorbar(label="value (log1p)" if log_scale else "value")
    plt.title("Field Heatmap (log)" if log_scale else "Field Heatmap")
    plt.tight_layout()
    return vals


def render_masks(cfg=None, resolution: int = 200):
    if cfg is None:
        cfg = make_field_config()
    xs = np.linspace(cfg.x_min, cfg.x_max, resolution)
    ys = np.linspace(cfg.y_min, cfg.y_max, resolution)
    grid = np.stack(np.meshgrid(xs, ys), axis=-1)
    masks = field_masks(grid, cfg)

    plt.figure(figsize=(7, 3))
    for i, name in enumerate(("I", "O", "A", "I_entropy")):
        plt.subplot(1, 4, i + 1)
        plt.imshow(
            masks[name],
            origin="lower",
            extent=[cfg.x_min, cfg.x_max, cfg.y_min, cfg.y_max],
        )
        plt.title(name)
        plt.axis("off")
    plt.tight_layout()
    return masks


__all__ = ["render_heatmap", "render_masks"]
