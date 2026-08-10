"""Problem definition and data-generation helpers for IOAI Field.

Each split is procedural: `load_split(split)` reads field and evaluation
configuration from `data/<split>/`, and `make_batch` generates samples from a
field configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import json
from pathlib import Path
import platform
import sys
from typing import Any

import numpy as np

PROBLEM_DIR = Path(__file__).resolve().parent
DATA_DIR = PROBLEM_DIR / "data"
_FIELD_RUNTIME = None


def _runtime():
    """Load the bundled platform-specific field runtime."""
    global _FIELD_RUNTIME
    if _FIELD_RUNTIME is not None:
        return _FIELD_RUNTIME

    system = platform.system()
    machine = platform.machine()

    if system == "Windows" and machine in {"AMD64", "x86_64"}:
        dist_base = "_dist-windows"
    elif system == "Linux" and machine in {"AMD64", "x86_64"}:
        dist_base = "_dist-linux"
    elif system == "Darwin" and machine in {"arm64", "aarch64"}:
        dist_base = "_dist-macos-arm"
    else:
        raise OSError(
            f"Unsupported platform: {system} {machine}. "
            "See RUNTIME.md for the supported runtime matrix."
        )

    python_tag = f"py{sys.version_info.major}{sys.version_info.minor}"
    candidates = [PROBLEM_DIR / f"{dist_base}-{python_tag}"]
    # The first published artifacts predate versioned runtime directories.
    if sys.version_info[:2] == (3, 10):
        candidates.append(PROBLEM_DIR / dist_base)

    dist_dir = next((path for path in candidates if path.is_dir()), None)
    if dist_dir is None:
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise ImportError(
            f"No protected IOAI Field runtime is bundled for "
            f"{system} {machine} on CPython {py_version}. See RUNTIME.md."
        )

    dist_path = str(dist_dir)
    if dist_path not in sys.path:
        sys.path.insert(0, dist_path)

    try:
        _FIELD_RUNTIME = importlib.import_module("field_fn")
    except ImportError as exc:
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise ImportError(
            f"Could not load the protected IOAI Field runtime for "
            f"{system} {machine} on CPython {py_version}. "
            "See RUNTIME.md for the supported runtime matrix."
        ) from exc
    return _FIELD_RUNTIME


def field_value(xy, cfg):
    return _runtime().field_value(xy, cfg)


def field_masks(xy, cfg):
    return _runtime().field_masks(xy, cfg)


def entropy_from_model(*args, **kwargs):
    return _runtime().entropy_from_model(*args, **kwargs)


def make_field_config(**kwargs):
    return _runtime().FieldConfig(**kwargs)


@dataclass
class FieldSplit:
    split: str
    field_configs: list[Any]
    eval_config: dict[str, Any]

    @property
    def field_config(self) -> Any:
        """First field config, for solutions that train/evaluate one config."""
        return self.field_configs[0]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _config_dicts_for_split(split: str) -> list[dict[str, Any]]:
    split_dir = DATA_DIR / split
    if not split_dir.exists():
        raise FileNotFoundError(f"Split '{split}' not found at {split_dir}")

    if split == "private":
        multi_path = split_dir / "field_configs.json"
        if multi_path.exists():
            return _read_json(multi_path)

    single_path = split_dir / "field_config.json"
    if single_path.exists():
        return [_read_json(single_path)]

    raise FileNotFoundError(
        f"Expected {single_path}"
        + (f" or {split_dir / 'field_configs.json'}" if split == "private" else "")
    )


def _eval_config_for_split(split: str) -> dict[str, Any]:
    path = DATA_DIR / split / "eval_config.json"
    if path.exists():
        return _read_json(path)
    return {}


def load_split(split: str) -> FieldSplit:
    """Load a dataset split: 'public', 'validation', or 'private'."""
    if split not in {"public", "validation", "private"}:
        raise ValueError(f"Unknown split: {split}")

    field_configs = [make_field_config(**cfg) for cfg in _config_dicts_for_split(split)]
    eval_config = _eval_config_for_split(split)

    return FieldSplit(
        split=split,
        field_configs=field_configs,
        eval_config=eval_config,
    )


@dataclass
class SamplingConfig:
    n_points: int = 4096
    stratified: bool = True


def sample_points(
    n: int,
    cfg: Any,
    stratified: bool = True,
    seed: int | None = None,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    if rng is None:
        rng = np.random.default_rng(seed)
    if stratified:
        k = int(np.sqrt(n))
        k = max(k, 1)
        xs = np.linspace(cfg.x_min, cfg.x_max, k + 1)
        ys = np.linspace(cfg.y_min, cfg.y_max, k + 1)
        pts = []
        for i in range(k):
            for j in range(k):
                x0, x1 = xs[i], xs[i + 1]
                y0, y1 = ys[j], ys[j + 1]
                x = rng.uniform(x0, x1)
                y = rng.uniform(y0, y1)
                pts.append([x, y])
        pts = np.array(pts, dtype=np.float32)
        if pts.shape[0] < n:
            extra = rng.uniform(
                [cfg.x_min, cfg.y_min],
                [cfg.x_max, cfg.y_max],
                size=(n - pts.shape[0], 2),
            )
            pts = np.concatenate([pts, extra.astype(np.float32)], axis=0)
        return pts[:n]
    return rng.uniform(
        [cfg.x_min, cfg.y_min],
        [cfg.x_max, cfg.y_max],
        size=(n, 2),
    ).astype(np.float32)


def make_batch(
    n: int,
    cfg: Any,
    stratified: bool = True,
    seed: int | None = None,
    exclude_regions: tuple[str, ...] = (),
    include_regions: tuple[str, ...] | None = None,
    oversample: int = 6,
    max_iter: int = 20,
):
    rng = np.random.default_rng(seed)
    if include_regions is None:
        include = {"I", "O", "A", "I_entropy", "bg"} - set(exclude_regions)
    else:
        include = set(include_regions)

    collected = []
    remaining = n
    for _ in range(max_iter):
        if remaining <= 0:
            break
        xy = sample_points(
            n * oversample,
            cfg,
            stratified=stratified,
            rng=rng,
        )
        masks = field_masks(xy, cfg)
        bg = np.ones(xy.shape[0], dtype=bool)
        for m in masks.values():
            bg &= ~m
        masks["bg"] = bg

        keep = np.zeros(xy.shape[0], dtype=bool)
        for name in include:
            if name in masks:
                keep |= masks[name]

        idx = np.where(keep)[0]
        if idx.size == 0:
            continue
        idx = rng.permutation(idx)
        take = min(remaining, idx.size)
        collected.append(xy[idx[:take]])
        remaining -= take

    if collected:
        xy = np.concatenate(collected, axis=0)
    else:
        xy = sample_points(n, cfg, stratified=stratified, rng=rng)

    if xy.shape[0] > n:
        xy = xy[:n]
    y = field_value(xy, cfg)
    return xy, y


__all__ = [
    "FieldSplit",
    "SamplingConfig",
    "entropy_from_model",
    "field_masks",
    "field_value",
    "load_split",
    "make_batch",
    "make_field_config",
    "sample_points",
]
