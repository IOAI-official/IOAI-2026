"""
Grader-owned scorer for IOAI Field — runs inside a podman sandbox.

It is mounted read-only at /grader/score_model.py, so the participant notebook (a
prior, separate container run) cannot tamper with it. It loads the model the
notebook produced (/work/model.pt) and scores it with `core.evaluate_model` against
the phase's selected config (/work/data/train_config, a read-only mount).

The runtime package (core/, problem.py, metrics/, _dist-linux-py313/) is mounted
into /work, so we add /work to sys.path to import it. Output is a single sentinel
line on stdout that the host grader (check.py) parses:

    GRADER_SCORE=<float>              scored OK (mean total_score over the config(s))
    GRADER_NO_MODEL                   model.pt missing            -> PresentationError
    GRADER_BAD_MODEL:<msg>            model.pt unloadable         -> PresentationError
    GRADER_COUNT_MISMATCH:<m> <c>     #models != #configs         -> PresentationError
    GRADER_SCORING_ERROR:<msg>        evaluate_model raised       -> RuntimeError
    GRADER_INTERNAL:<msg>             grader-side integrity fault -> non-zero exit
"""
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, "/work")  # core/ + problem.py + metrics/ + _dist-* are mounted here

TRAIN_DIR = Path("/work/data/train_config")  # selected phase config, mounted RO
MODEL_PATH = Path("/work/model.pt")


def emit(line: str) -> None:
    print(line, flush=True)


def main() -> int:
    if not MODEL_PATH.exists():
        emit("GRADER_NO_MODEL")
        return 0

    # config(s): field_configs.json (multi) or field_config.json (single) + eval_config.json
    multi = TRAIN_DIR / "field_configs.json"
    single = TRAIN_DIR / "field_config.json"
    try:
        if multi.exists():
            raw_cfgs = json.loads(multi.read_text())
        elif single.exists():
            raw_cfgs = [json.loads(single.read_text())]
        else:
            emit(f"GRADER_INTERNAL:no field config in {TRAIN_DIR}")
            return 3
        eval_path = TRAIN_DIR / "eval_config.json"
        raw_eval = json.loads(eval_path.read_text()) if eval_path.exists() else {}
    except Exception as exc:  # noqa: BLE001
        emit(f"GRADER_INTERNAL:config unreadable: {exc}")
        return 3

    import torch  # noqa: F401
    from core import evaluate_model, FieldConfig, EvalConfig

    try:
        loaded = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    except Exception as exc:  # noqa: BLE001
        emit(f"GRADER_BAD_MODEL:{exc}")
        return 0

    cfgs = [FieldConfig(**c) for c in raw_cfgs]
    ecfg = EvalConfig(**raw_eval) if raw_eval else EvalConfig()

    if isinstance(loaded, (list, tuple)):
        models = list(loaded)
        if len(models) != len(cfgs):
            emit(f"GRADER_COUNT_MISMATCH:{len(models)} {len(cfgs)}")
            return 0
    else:
        models = [loaded] * len(cfgs)

    try:
        scores = [float(evaluate_model(m, c, ecfg)["total_score"])
                  for m, c in zip(models, cfgs)]
    except Exception as exc:  # noqa: BLE001 - a bad participant model
        traceback.print_exc(file=sys.stderr)
        emit(f"GRADER_SCORING_ERROR:{type(exc).__name__}: {exc}")
        return 0

    emit(f"GRADER_SCORE={sum(scores) / len(scores):.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
