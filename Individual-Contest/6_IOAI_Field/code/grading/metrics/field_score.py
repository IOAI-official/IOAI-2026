"""IOAI Field metric and evaluator.

Solutions return a trained model, or one model per field configuration. The
metric evaluates those model(s) against the field configuration(s) for the
selected split.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
import random
from typing import Any, Dict, List, Tuple

import numpy as np

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

from problem import field_masks, field_value, make_field_config, sample_points

REGIONS = ("I", "O", "A", "I_entropy", "bg")


@dataclass
class EvalConfig:
    n_per_region: int = 1024
    seed: int = 0
    oversample: int = 6
    range_mode: str = "p99"
    bg_scale: float = 0.1
    entropy_runs: int = 10
    entropy_mode: str = "std"
    entropy_bins: int = 10
    enforce_unit_interval: bool = True
    entropy_min: float = -2026.0
    entropy_max: float = 2026.0
    max_params: int = 20260
    param_penalty: float = 0.5
    ignore_torch_check: bool = False
    weights: Dict[str, float] | None = None


_NN_INTERNAL_ATTRS = {
    "training",
    "_parameters",
    "_buffers",
    "_non_persistent_buffers_set",
    "_backward_pre_hooks",
    "_backward_hooks",
    "_is_full_backward_hook",
    "_forward_hooks",
    "_forward_hooks_with_kwargs",
    "_forward_hooks_always_called",
    "_forward_pre_hooks",
    "_forward_pre_hooks_with_kwargs",
    "_state_dict_hooks",
    "_state_dict_pre_hooks",
    "_load_state_dict_pre_hooks",
    "_load_state_dict_post_hooks",
    "_modules",
}


def _is_simple_metadata(value) -> bool:
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    if torch is not None and isinstance(value, (torch.dtype, torch.device)):
        return True
    return False


def _check_module_value(value, path: str, seen: set[int]) -> None:
    obj_id = id(value)
    if obj_id in seen:
        return
    seen.add(obj_id)

    if _is_simple_metadata(value):
        return

    if torch is not None and isinstance(value, torch.nn.Parameter):
        return

    if torch is not None and isinstance(value, torch.nn.Module):
        return

    if torch is not None and isinstance(value, torch.Tensor):
        raise ValueError(
            f"Disallowed tensor at {path}. "
            "All persistent tensors must be registered as torch.nn.Parameter."
        )

    if isinstance(value, np.ndarray):
        raise ValueError(
            f"Disallowed NumPy array at {path}. "
            "Persistent numerical state must be stored as torch.nn.Parameter."
        )

    if isinstance(value, Mapping):
        for key, item in value.items():
            _check_module_value(item, f"{path}[{key!r}]", seen)
        return

    if isinstance(value, (list, tuple, set, frozenset)):
        for i, item in enumerate(value):
            _check_module_value(item, f"{path}[{i}]", seen)
        return

    raise ValueError(
        f"Disallowed object at {path}: {type(value).__name__}. "
        "Only registered nn.Module submodules, nn.Parameter objects, and simple metadata are allowed."
    )


def validate_model_for_evaluation(model) -> None:
    # TODO: should also check the solution didn't hide parameters in global variables
    if not isinstance(model, torch.nn.Module):
        raise TypeError(
            f"Submitted object must be a torch.nn.Module, got {type(model).__name__}."
        )

    # Buffers are not counted by model.parameters(), so disallow them.
    if list(model.buffers()):
        raise ValueError(
            "Registered buffers are not allowed. "
            "All persistent tensors must be torch.nn.Parameter."
        )

    seen: set[int] = set()

    for module_name, module in model.named_modules():
        module_path = "model" if module_name == "" else f"model.{module_name}"

        for attr_name, value in module.__dict__.items():
            if attr_name in _NN_INTERNAL_ATTRS:
                continue

            _check_module_value(value, f"{module_path}.{attr_name}", seen)


def count_params(model) -> int:
    validate_model_for_evaluation(model)
    return sum(p.numel() for p in model.parameters())


class _TrainMode:
    def __init__(self, model, train: bool):
        self.model = model
        self.train = train
        self.prev = None

    def __enter__(self):
        if self.model is None:
            return
        if hasattr(self.model, "training"):
            self.prev = self.model.training
            self.model.train(self.train)

    def __exit__(self, exc_type, exc, tb):
        if self.prev is not None:
            self.model.train(self.prev)


def _model_device(model):
    """Return the first parameter's device, or CPU for parameterless callables."""
    try:
        return next(model.parameters()).device
    except (AttributeError, StopIteration):
        return torch.device("cpu")


def _predict_model(model, xy: np.ndarray, train: bool = False) -> np.ndarray:
    if callable(model) and torch is None:
        return np.asarray(model(xy)).squeeze()

    if torch is None:
        raise RuntimeError("PyTorch not available for model evaluation.")

    with _TrainMode(model, train):
        with torch.no_grad():
            x = torch.tensor(xy, dtype=torch.float32, device=_model_device(model))
            y = model(x)
            if isinstance(y, (tuple, list)):
                y = y[0]
            if isinstance(y, np.ndarray):
                return y.squeeze()
            y = y.detach().cpu().numpy()

    return y.squeeze()


def _predict_model_random_batches(
    model,
    xy: np.ndarray,
    train: bool,
    seed: int,
) -> np.ndarray:
    """Predict on shuffled random-sized batches and restore original order.

    This avoids exposing the evaluator's region-block structure to the model.
    Batch sizes are deterministic for a fixed seed but intentionally irregular.
    """

    n = xy.shape[0]
    if n == 0:
        return np.empty((0,), dtype=np.float32)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)

    out: np.ndarray | None = None
    pos = 0

    while pos < n:
        # Irregular deterministic batch sizes
        batch_size = int(rng.integers(113, 389))
        idx = perm[pos : pos + batch_size]

        pred = np.asarray(_predict_model(model, xy[idx], train=train)).reshape(-1)

        if pred.shape[0] != idx.shape[0]:
            raise ValueError(
                f"Model returned {pred.shape[0]} predictions for batch of size {idx.shape[0]}."
            )

        if out is None:
            out = np.empty(n, dtype=pred.dtype)

        out[idx] = pred
        pos += batch_size

    assert out is not None
    return out


def _safe_log(x: np.ndarray) -> np.ndarray:
    return np.sign(x) * np.log1p(np.abs(x))


def _range_from_target(values: np.ndarray, mode: str = "p95") -> float:
    if values.size == 0:
        return 1.0
    if mode == "max":
        return float(np.max(values) - np.min(values))
    if mode == "p95":
        lo, hi = np.percentile(values, [5, 95])
        return float(hi - lo)
    if mode == "p99":
        lo, hi = np.percentile(values, [1, 99])
        return float(hi - lo)
    raise ValueError(f"Unknown range mode: {mode}")


def _score_from_mae(mae: float, scale: float) -> float:
    scale = float(scale)
    if scale <= 0.0:
        scale = 1.0
    return float(1.0 - min(mae / scale, 1.0))


@contextmanager
def _seeded_randomness(seed: int, device=None):
    """Seed stochastic model code for one run, then restore caller RNG state."""
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    torch_state = torch.default_generator.get_state() if torch is not None else None
    cuda_index = None
    cuda_state = None
    if torch is not None and device is not None and device.type == "cuda":
        cuda_index = device.index
        if cuda_index is None:
            cuda_index = torch.cuda.current_device()
        cuda_state = torch.cuda.get_rng_state(cuda_index)

    random.seed(seed)
    np.random.seed(seed % (2**32))
    if torch is not None:
        torch.default_generator.manual_seed(seed)
        if cuda_index is not None:
            with torch.cuda.device(cuda_index):
                torch.cuda.manual_seed(seed)

    try:
        yield
    finally:
        random.setstate(python_state)
        np.random.set_state(numpy_state)
        if torch_state is not None:
            torch.default_generator.set_state(torch_state)
        if cuda_state is not None:
            torch.cuda.set_rng_state(cuda_state, cuda_index)


def compute_metrics(
    pred: np.ndarray,
    target: np.ndarray,
    xy: np.ndarray,
    cfg: Any | None = None,
    range_mode: str = "p95",
    log_regions: Tuple[str, ...] = (),
    bg_scale: float = 0.1,
    verbose: bool = False,
    verbose_text: bool = True,
) -> Dict[str, float]:
    if cfg is None:
        cfg = make_field_config()

    masks = field_masks(xy, cfg)
    scores: Dict[str, float] = {}

    def _explain(
        name: str,
        mae: float,
        scale: float,
        score: float,
        n: int,
        used_log: bool,
    ) -> str:
        log_note = " (log1p applied)" if used_log else ""
        if scale <= 0.0:
            return (
                f"{name}: n={n}, mae={mae:.6g}, scale={scale:.6g}{log_note}. "
                f"constant target => using scale=1.0. "
                f"score = 1 - min(mae/1.0, 1) = {score:.6g}"
            )
        return (
            f"{name}: n={n}, mae={mae:.6g}, scale={scale:.6g}{log_note}. "
            f"score = 1 - min(mae/scale, 1) = "
            f"1 - min({mae:.6g}/{scale:.6g}, 1) = {score:.6g}"
        )

    for name, mask in masks.items():
        if mask.sum() == 0:
            scores[f"{name}_score"] = 0.0
            continue

        p = pred[mask]
        t = target[mask]
        used_log = name in log_regions

        if used_log:
            p = _safe_log(p)
            t = _safe_log(t)

        mae = float(np.mean(np.abs(p - t)))
        scale = _range_from_target(t, mode=range_mode)
        scores[f"{name}_score"] = _score_from_mae(mae, scale)

        if verbose:
            scores[f"{name}_mae"] = mae
            scores[f"{name}_scale"] = float(scale)

        if verbose_text:
            scores[f"{name}_explain"] = _explain(
                name=name,
                mae=mae,
                scale=scale,
                score=float(scores[f"{name}_score"]),
                n=int(mask.sum()),
                used_log=used_log,
            )

    bg_mask = np.ones_like(target, dtype=bool)
    for m in masks.values():
        bg_mask &= ~m

    if bg_mask.sum() == 0:
        scores["bg_score"] = 0.0
    else:
        bg_mae = float(np.mean(np.abs(pred[bg_mask])))
        scores["bg_score"] = _score_from_mae(bg_mae, bg_scale)

        if verbose:
            scores["bg_mae"] = bg_mae
            scores["bg_scale"] = float(bg_scale)

        if verbose_text:
            scores["bg_explain"] = _explain(
                name="bg",
                mae=bg_mae,
                scale=float(bg_scale),
                score=float(scores["bg_score"]),
                n=int(bg_mask.sum()),
                used_log=False,
            )

    return scores


def format_metrics_explanation(
    scores: Dict[str, float],
    include: Tuple[str, ...] = ("I", "O", "A", "I_entropy", "bg", "total", "param"),
) -> str:
    lines = []

    for name in include:
        if name == "bg":
            key = "bg_explain"
        elif name == "total":
            key = "total_explain"
        elif name == "param":
            key = "param_explain"
        else:
            key = f"{name}_explain"

        if key in scores:
            title = "[param multiplier]" if name == "param" else f"[{name}]"
            body = scores[key]
            parts = [p.strip() for p in body.split(". ") if p.strip()]
            lines.append(title)
            for p in parts:
                if not p.endswith("."):
                    p += "."
                lines.append(f"  {p}")
            lines.append("")

    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def _sample_points_by_region(
    cfg: Any,
    n_per_region: int,
    seed: int,
    oversample: int,
) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    out: Dict[str, List[np.ndarray]] = {name: [] for name in REGIONS}
    need = {name: n_per_region for name in REGIONS}

    while any(v > 0 for v in need.values()):
        n_total = n_per_region * len(REGIONS) * oversample

        xy = sample_points(
            n_total,
            cfg,
            stratified=True,
            seed=int(rng.integers(0, 1_000_000)),
        )

        masks = field_masks(xy, cfg)

        bg_mask = np.ones(xy.shape[0], dtype=bool)
        for m in masks.values():
            bg_mask &= ~m
        masks["bg"] = bg_mask

        for name in REGIONS:
            if need[name] <= 0:
                continue

            idx = np.where(masks[name])[0]
            if idx.size == 0:
                continue

            take = min(need[name], idx.size)
            pick = rng.choice(idx, size=take, replace=False)
            out[name].append(xy[pick])
            need[name] -= take

    return {name: np.concatenate(chunks, axis=0) for name, chunks in out.items()}


def _entropy_score(samples: np.ndarray, bins: int = 10) -> float:
    vmin, vmax = float(samples.min()), float(samples.max())

    if vmax - vmin < 1e-8:
        return 0.0

    norm = (samples - vmin) / (vmax - vmin)
    idx = np.clip((norm * bins).astype(np.int32), 0, bins - 1)

    hist = np.bincount(idx, minlength=bins).astype(np.float32)
    p = hist / np.sum(hist)
    p = p[p > 0]

    return float(-np.sum(p * np.log(p + 1e-8)))


def _coerce_eval_config(eval_cfg: EvalConfig | dict[str, Any] | None) -> EvalConfig:
    if eval_cfg is None:
        return EvalConfig()
    if isinstance(eval_cfg, EvalConfig):
        return eval_cfg
    return EvalConfig(**eval_cfg)


def evaluate_model(
    model,
    cfg: Any | None = None,
    eval_cfg: EvalConfig | dict[str, Any] | None = None,
    verbose_text: bool = True,
) -> Dict[str, float]:
    if cfg is None:
        cfg = make_field_config()

    eval_cfg = _coerce_eval_config(eval_cfg)

    pts = _sample_points_by_region(
        cfg,
        eval_cfg.n_per_region,
        eval_cfg.seed,
        eval_cfg.oversample,
    )

    xy_all = np.concatenate(
        [pts["I"], pts["O"], pts["A"], pts["I_entropy"], pts["bg"]],
        axis=0,
    )

    # Predictions are made through shuffled, random-sized batches.
    # The returned predictions are restored to match xy_all order.
    pred_all = _predict_model_random_batches(
        model,
        xy_all,
        train=False,
        seed=eval_cfg.seed + 10_003,
    )

    target_all = field_value(xy_all, cfg)

    scores = compute_metrics(
        pred_all,
        target_all,
        xy_all,
        cfg,
        range_mode=eval_cfg.range_mode,
        bg_scale=eval_cfg.bg_scale,
        verbose_text=verbose_text,
    )

    xy_entropy = pts["I_entropy"]
    runs = eval_cfg.entropy_runs
    samples = []
    model_device = _model_device(model) if torch is not None else None

    for run_idx in range(runs):
        batch_seed = eval_cfg.seed + 20_003 + run_idx
        model_seed = eval_cfg.seed + 30_003 + run_idx

        # Make stochastic layers such as dropout reproducible without changing
        # the caller's RNG state outside this entropy run.
        with _seeded_randomness(model_seed, device=model_device):
            pred = _predict_model_random_batches(
                model,
                xy_entropy,
                train=True,
                seed=batch_seed,
            )
        samples.append(pred)

    values = np.stack(samples, axis=0)

    if eval_cfg.enforce_unit_interval:
        in_range = (values >= eval_cfg.entropy_min) & (values <= eval_cfg.entropy_max)
        valid = np.all(in_range, axis=0)
    else:
        valid = np.ones(values.shape[1], dtype=bool)

    std_max = np.sqrt(1.0 / 12.0)
    per_point_scores = []

    for i in range(values.shape[1]):
        if not valid[i]:
            per_point_scores.append(0.0)
            continue

        v = values[:, i]

        if eval_cfg.entropy_mode == "std":
            s = float(np.std(v)) / std_max
        else:
            s = _entropy_score(v, bins=eval_cfg.entropy_bins)
            s = s / np.log(eval_cfg.entropy_bins)

        per_point_scores.append(float(np.clip(s, 0.0, 1.0)))

    i_entropy_score = float(np.mean(per_point_scores)) if per_point_scores else 0.0
    scores["I_entropy_score"] = i_entropy_score

    if verbose_text:
        scores["I_entropy_explain"] = (
            f"I_entropy: n={xy_entropy.shape[0]}, runs={runs}, mode={eval_cfg.entropy_mode}. "
            f"Rule: if any run is outside [{eval_cfg.entropy_min},{eval_cfg.entropy_max}], point score=0. "
            f"Final score = mean(point scores) = {i_entropy_score:.6g}"
        )

    weights = eval_cfg.weights or {
        "I": 1.0,
        "O": 1.0,
        "A": 1.0,
        "I_entropy": 1.0,
        "bg": 1.0,
    }

    num = 0.0
    den = 0.0

    for name in REGIONS:
        key = f"{name}_score" if name != "bg" else "bg_score"
        if key in scores:
            w = float(weights.get(name, 0.0))
            num += w * float(scores[key])
            den += w

    total = 0.0 if den == 0 else (num / den) * 100.0
    scores["total_score"] = float(total)

    if verbose_text:
        scores["total_explain"] = f"Total: weighted mean of region scores * 100 = {total:.4f}"

    if torch is None or not hasattr(model, "parameters"):
        if eval_cfg.ignore_torch_check:
            if verbose_text:
                scores["param_explain"] = "Params: skipped (non-torch model)"
        else:
            raise RuntimeError("Model must be a torch.nn.Module to compute parameter penalty.")

        scores["__explain__"] = format_metrics_explanation(
            scores,
            include=("I", "O", "A", "I_entropy", "bg", "param", "total"),
        )
        return scores

    param_count = count_params(model)
    scores["param_count"] = int(param_count)

    if param_count >= eval_cfg.max_params:
        scores["total_score"] = float(scores["total_score"] * eval_cfg.param_penalty)
        if verbose_text:
            scores["param_explain"] = (
                f"Params: {param_count} >= {eval_cfg.max_params} => total_score halved"
            )
            scores["total_explain"] = (
                f"Total: weighted mean * 100, then halved = {scores['total_score']:.4f}"
            )
    else:
        if verbose_text:
            scores["param_explain"] = (
                f"Params: {param_count} < {eval_cfg.max_params} => no penalty"
            )

    scores["__explain__"] = format_metrics_explanation(
        scores,
        include=("I", "O", "A", "I_entropy", "bg", "param", "total"),
    )

    return scores


class Metric:
    name = "field_score"

    def __call__(self, models, data) -> float:
        field_configs = getattr(data, "field_configs", [data.field_config])
        eval_config = getattr(data, "eval_config", None)

        if isinstance(models, Sequence) and not isinstance(models, (str, bytes)):
            if len(models) != len(field_configs):
                raise ValueError(
                    f"Got {len(models)} models for {len(field_configs)} field configs."
                )
            pairs = list(zip(models, field_configs))
        else:
            pairs = [(models, cfg) for cfg in field_configs]

        scores = []

        for idx, (model, cfg) in enumerate(pairs, start=1):
            validate_model_for_evaluation(model)
            result = evaluate_model(model, cfg, eval_config)

            if "__explain__" in result:
                print(f"[field config {idx}]\n{result['__explain__']}")

            scores.append(float(result["total_score"]))

        return sum(scores) / len(scores)


def compute(models, data) -> float:
    return Metric()(models, data)
