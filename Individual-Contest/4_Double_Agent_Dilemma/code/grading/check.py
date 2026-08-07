"""Grade a Double Agent Dilemma notebook and submission inside Podman.

The participant notebook runs first and writes ``submission.zip``.  A second,
separate container loads the locked split, calls ``evaluate.build_preds`` and
``evaluate.compute_score``, and returns only the numeric result to this host
process.  Both containers are offline and receive data through bind mounts.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


CI_ROOT = Path(__file__).resolve().parent
GRADING_SPLIT = os.environ.get("TEST_SPLIT", "test_leaderboard_a")
TRAIN_SPLIT = os.environ.get("TRAIN_SPLIT", "train")
SUBMISSION_NAME = os.environ.get("SUBMISSION_NAME", "submission.zip")

WALL_CLOCK_BUDGET_SEC = int(os.environ.get("WALL_CLOCK_BUDGET_SEC", "600"))
SCORE_BUDGET_SEC = int(os.environ.get("SCORE_BUDGET_SEC", "600"))
MAX_NOTEBOOK_BYTES = int(os.environ.get("MAX_NOTEBOOK_BYTES", "1048576"))
LOG_TAIL_BYTES = 65536

NOTEBOOK_IMAGE = os.environ["NOTEBOOK_IMAGE"]
GPU_DEVICE = os.environ.get("GPU_DEVICE", "nvidia.com/gpu=all")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "solution-run")
PODMAN = os.environ.get("PODMAN", "podman")

# The solution notebook deliberately does not extract archives: the job image must
# provide already-extracted dataset/<split> directories.
DATASET_ROOT = Path(os.environ.get("DATASET_ROOT", str(CI_ROOT / "data"))).resolve()
MODELS_DIR = Path(os.environ.get("MODELS_ROOT", "/problem/models")).resolve()

REPO_NAME = os.environ.get("REPO_NAME", "submission")
REPO_DIR = Path(REPO_NAME).resolve()
NOTEBOOK_PATH = REPO_DIR / "solution.ipynb"

REPORT_PATH = Path("report.json")
EXECUTED_NB = Path("executed.ipynb")
STDOUT_LOG = Path("executed_stdout.log")
STDERR_LOG = Path("executed_stderr.log")
ERROR_PATH = Path("error.txt")
SCORE_RESULT = REPO_DIR / ".score_result.json"

C_WORK = "/work"
C_GRADER = "/grader"
# Match solution.ipynb's default relative paths while keeping the sources on the
# CI host at /problem/{dataset,models}. These read-only mounts are layered inside
# the participant's /work mount.
C_DATA = f"{C_WORK}/dataset"
C_MODELS = f"{C_WORK}/models"
_RUN_MS = 0


def write_report(*, score, verdict, message, include_error_artifact=False,
                 testset_name="tests"):
    test = {
        "testName": "final_score",
        "testsetName": testset_name,
        "verdict": verdict,
        "score": float(score),
        "runningTime": int(_RUN_MS),
    }
    encoded_score = json.dumps({GRADING_SPLIT[-1]: float(score)})
    report = {"report": {"result": {"message": encoded_score}, "tests": [test]}}
    if include_error_artifact:
        report["artifacts"] = [{
            "testName": "final_score",
            "testDataType": "ERROR",
            "path": str(ERROR_PATH),
        }]
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"[{verdict}] score={score} | {message} | {_RUN_MS} ms")


def fail(message, verdict, *, include_error_artifact=False, testset_name="tests"):
    write_report(score=0.0, verdict=verdict, message=message,
                 include_error_artifact=include_error_artifact,
                 testset_name=testset_name)
    sys.exit(0)


def fail_prerun(message, verdict):
    """Publish the full pretrain/pretest stderr as an ERROR artifact."""
    stderr = STDERR_LOG.read_text(errors="replace") if STDERR_LOG.exists() else ""
    content = message
    if stderr:
        content += "\n\n--- full pretrain/pretest stderr ---\n" + stderr
    else:
        content += "\n\n(no stderr was captured)\n"
    ERROR_PATH.write_text(content)
    fail(message, verdict, include_error_artifact=True, testset_name="samples")


def tail_file(path, nbytes=LOG_TAIL_BYTES):
    if not path.exists():
        return ""
    size = path.stat().st_size
    with path.open("rb") as fh:
        if size > nbytes:
            fh.seek(size - nbytes)
        return fh.read().decode(errors="replace")


def _podman_run(inner_cmd, *, timeout, stdout=None, stderr=None, name=CONTAINER_NAME):
    """Run the locked runtime with the participant workspace and grader mounted."""
    volumes = [
        "-v", f"{REPO_DIR}:{C_WORK}",
        "-v", f"{CI_ROOT / 'evaluate.py'}:{C_GRADER}/evaluate.py:ro",
        "-v", f"{DATASET_ROOT}:{C_DATA}:ro",
        "-v", f"{MODELS_DIR}:{C_MODELS}:ro",
    ]
    cmd = [
        PODMAN, "run", "--rm", "--name", name, "--network=none",
        "--device", GPU_DEVICE, *volumes,
        "-w", C_WORK,
        "-e", f"PYTHONPATH={C_GRADER}",
        "-e", f"TRAIN_SPLIT={TRAIN_SPLIT}",
        "-e", f"TEST_SPLIT={GRADING_SPLIT}",
        "-e", f"DATA_DIR={C_DATA}",
        "-e", "HF_HUB_OFFLINE=1",
        "-e", "TRANSFORMERS_OFFLINE=1",
        "-e", f"MODELS_DIR={C_MODELS}",
        NOTEBOOK_IMAGE, "bash", "-lc", inner_cmd,
    ]
    print("running:", " ".join(cmd))
    try:
        return subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run([PODMAN, "rm", "-f", name], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        raise
    
def _podman_run_on_presplits(inner_cmd, *, timeout, stdout=None, stderr=None, name=CONTAINER_NAME):
    """Run the locked runtime with the participant workspace and grader mounted."""
    volumes = [
        "-v", f"{REPO_DIR}:{C_WORK}",
        "-v", f"{CI_ROOT / 'evaluate.py'}:{C_GRADER}/evaluate.py:ro",
        "-v", f"{DATASET_ROOT}:{C_DATA}:ro",
        "-v", f"{MODELS_DIR}:{C_MODELS}:ro",
    ]
    cmd = [
        PODMAN, "run", "--rm", "--name", name, "--network=none",
        "--device", GPU_DEVICE, *volumes,
        "-w", C_WORK,
        "-e", f"PYTHONPATH={C_GRADER}",
        "-e", f"TRAIN_SPLIT=pretrain",
        "-e", f"TEST_SPLIT=pretest",
        "-e", f"DATA_DIR={C_DATA}",
        "-e", "HF_HUB_OFFLINE=1",
        "-e", "TRANSFORMERS_OFFLINE=1",
        "-e", f"MODELS_DIR={C_MODELS}",
        NOTEBOOK_IMAGE, "bash", "-lc", inner_cmd,
    ]
    print("running:", " ".join(cmd))
    try:
        return subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run([PODMAN, "rm", "-f", name], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        raise


def preflight_dataset():
    problems = []
    for split in (TRAIN_SPLIT, GRADING_SPLIT):
        split_dir = DATASET_ROOT / split
        labels = split_dir / "labels.json"
        images = split_dir / "images"
        if not split_dir.is_dir():
            problems.append(
                f"dataset split must be extracted before grading: {split_dir}"
            )
        elif not labels.is_file() or not images.is_dir():
            problems.append(f"split is missing labels.json or images/: {split_dir}")
    for filename in ("resnet18.pth", "vit_tiny_patch16_224.safetensors"):
        path = MODELS_DIR / filename
        if not path.is_file():
            problems.append(f"model weight missing: {path}")
    if problems:
        for problem in problems:
            print(f"FATAL: {problem}", file=sys.stderr)
        sys.exit(1)


def preflight_runtime():
    """Verify the pinned offline runtime before executing participant code."""
    check = """
import sys
import torch
import torchvision
import timm
import evaluate


print("torch", torch.__version__, "torchvision", torchvision.__version__,
      "timm", timm.__version__)
print("CUDA available:", torch.cuda.is_available())

"""
    try:
        proc = _podman_run("python - <<'PY'\n" + check + "\nPY", timeout=120,
                           name=f"{CONTAINER_NAME}-preflight")
    except subprocess.TimeoutExpired:
        print("FATAL: runtime/model preflight exceeded 120s", file=sys.stderr)
        sys.exit(1)
    if proc.returncode != 0:
        print("FATAL: runtime is missing dependencies, CUDA, or compatible model weights",
              file=sys.stderr)
        sys.exit(1)


def run_notebook():
    if not NOTEBOOK_PATH.is_file():
        fail(f"solution.ipynb not found at {NOTEBOOK_PATH}", "PresentationError", testset_name="notebook_runtime")
    if NOTEBOOK_PATH.stat().st_size > MAX_NOTEBOOK_BYTES:
        fail(f"solution.ipynb exceeds the {MAX_NOTEBOOK_BYTES} byte limit",
             "PresentationError", testset_name="notebook_runtime")

    os.chmod(REPO_DIR, 0o777)
    inner = (
        "python -m nbconvert --to notebook --execute --output executed.ipynb "
        "--ExecutePreprocessor.timeout=-1 "
        "--ExecutePreprocessor.kernel_name=python3 solution.ipynb"
    )
    global _RUN_MS
    started = time.perf_counter()
    with STDOUT_LOG.open("wb") as out, STDERR_LOG.open("wb") as err:
        try:
            proc = _podman_run(inner, timeout=WALL_CLOCK_BUDGET_SEC,
                               stdout=out, stderr=err)
        except subprocess.TimeoutExpired:
            _RUN_MS = int((time.perf_counter() - started) * 1000)
            fail(f"solution.ipynb exceeded {WALL_CLOCK_BUDGET_SEC}s",
                 "TimeLimitExceeded", testset_name="time_limit_exceeded")
    _RUN_MS = int((time.perf_counter() - started) * 1000)
    executed = REPO_DIR / "executed.ipynb"
    if executed.exists():
        shutil.copy(executed, EXECUTED_NB)
    print("--- nbconvert stdout (tail) ---\n" + tail_file(STDOUT_LOG))
    print("--- nbconvert stderr (tail) ---\n" + tail_file(STDERR_LOG))
    if proc.returncode != 0:
        tail = "\n".join(tail_file(STDERR_LOG).splitlines()[-10:]) or "no stderr"
        fail(f"solution.ipynb failed (exit {proc.returncode}): {tail}", "RuntimeError", testset_name="notebook_runtime")

def prerun_notebook():
    """Run the notebook on the pretrain and pretest splits"""
    ERROR_PATH.unlink(missing_ok=True)
    if not NOTEBOOK_PATH.is_file():
        fail(f"solution.ipynb not found at {NOTEBOOK_PATH}", "PresentationError")
    if NOTEBOOK_PATH.stat().st_size > MAX_NOTEBOOK_BYTES:
        fail(f"solution.ipynb exceeds the {MAX_NOTEBOOK_BYTES} byte limit",
             "PresentationError")

    os.chmod(REPO_DIR, 0o777)
    inner = (
        "python -m nbconvert --to notebook --execute --output executed.ipynb "
        "--ExecutePreprocessor.timeout=-1 "
        "--ExecutePreprocessor.kernel_name=python3 solution.ipynb"
    )
    with STDOUT_LOG.open("wb") as out, STDERR_LOG.open("wb") as err:
        try:
            proc = _podman_run_on_presplits(inner, timeout=WALL_CLOCK_BUDGET_SEC,
                               stdout=out, stderr=err)
        except subprocess.TimeoutExpired:
            err.flush()
            fail_prerun(
                f"pretrain/pretest run exceeded {WALL_CLOCK_BUDGET_SEC}s",
                "TimeLimitExceeded",
            )
    executed = REPO_DIR / "executed.ipynb"
    if executed.exists():
        shutil.copy(executed, EXECUTED_NB)
    print("--- nbconvert stdout (tail) ---\n" + tail_file(STDOUT_LOG))
    print("--- nbconvert stderr (tail) ---\n" + tail_file(STDERR_LOG))
    if proc.returncode != 0:
        tail = "\n".join(tail_file(STDERR_LOG).splitlines()[-10:]) or "no stderr"
        fail_prerun(
            f"pretrain/pretest run failed (exit {proc.returncode}): {tail}",
            "RuntimeError",
        )


def locate_submission_zip():
    search_dirs = [REPO_DIR, CI_ROOT]
    explicit = os.environ.get("SUBMISSION_ZIP")
    if explicit:
        candidate = Path(explicit)
        if candidate.is_absolute() and candidate.is_file():
            return candidate.resolve()
        for directory in search_dirs:
            if (directory / explicit).is_file():
                return (directory / explicit).resolve()
    for name in (SUBMISSION_NAME, f"{GRADING_SPLIT}.zip"):
        for directory in search_dirs:
            if (directory / name).is_file():
                return (directory / name).resolve()
    filename = os.environ.get("FILENAME")
    if filename and filename.endswith(".zip"):
        for directory in search_dirs:
            if (directory / filename).is_file():
                return (directory / filename).resolve()
    zips = list(dict.fromkeys([*sorted(REPO_DIR.rglob("*.zip")),
                               *sorted(CI_ROOT.glob("*.zip"))]))
    if len(zips) == 1:
        return zips[0].resolve()
    if zips:
        fail(f"multiple submission zips found: {[str(p) for p in zips]}",
             "PresentationError")
    fail("no submission zip found", "PresentationError")


def score_submission(zip_path):
    """Run build_preds and compute_score in the same locked Podman image."""
    try:
        relative_zip = zip_path.relative_to(REPO_DIR)
    except ValueError:
        # The scorer only receives the participant RW mount. Copy a root-level
        # notebook output into it so the path is available inside the sandbox.
        copied = REPO_DIR / zip_path.name
        shutil.copy2(zip_path, copied)
        relative_zip = copied.relative_to(REPO_DIR)

    SCORE_RESULT.unlink(missing_ok=True)
    script = f"""
import json, math, zipfile
from pathlib import Path
import evaluate

def load_split(split):
    split_dir = Path({C_DATA!r}) / split
    labels = json.loads((split_dir / "labels.json").read_text())
    images_dir = split_dir / "images"
    return [
        {{"idx": int(idx),
          "image_path": images_dir / f"{{int(idx):04d}}.png",
          "label": label}}
        for idx, label in sorted(labels.items(), key=lambda pair: int(pair[0]))
    ]

result_path = Path({str(C_WORK + '/.score_result.json')!r})
try:
    targets = load_split({GRADING_SPLIT!r})
    print(f"loaded {{len(targets)}} items from locked split {GRADING_SPLIT!r}")
    preds = evaluate.build_preds(Path({str(Path(C_WORK) / relative_zip)!r}), targets)
    score = float(evaluate.compute_score(preds, targets, verbose=True))
    if not math.isfinite(score):
        raise ValueError(f"evaluator returned non-finite score: {{score}}")
    result = {{"status": "ok", "score": score}}
except zipfile.BadZipFile as exc:
    result = {{"status": "presentation_error", "message": str(exc)}}
result_path.write_text(json.dumps(result))
"""
    try:
        proc = _podman_run("python - <<'PY'\n" + script + "\nPY", timeout=SCORE_BUDGET_SEC,
                           name=f"{CONTAINER_NAME}-score")
    except subprocess.TimeoutExpired:
        print(f"FATAL: evaluator exceeded {SCORE_BUDGET_SEC}s", file=sys.stderr)
        sys.exit(1)
    if proc.returncode != 0 or not SCORE_RESULT.is_file():
        print(f"FATAL: evaluator container failed with exit {proc.returncode}", file=sys.stderr)
        sys.exit(1)

    result = json.loads(SCORE_RESULT.read_text())
    SCORE_RESULT.unlink(missing_ok=True)
    if result["status"] == "presentation_error":
        fail(f"submission is not a valid zip: {result['message']}", "PresentationError")
    final_score = float(result["score"])
    score = 100.0 * final_score
    write_report(score=score, verdict="OK",
                 message=f"final_score={final_score:.4f} on split '{GRADING_SPLIT}'")


def main():
    preflight_dataset()
    print(f"[preflight] dataset and models verified, grading split={GRADING_SPLIT}")
    preflight_runtime()
    print(f"[preflight] runtime verified")
    
    ### TODO: Run the notebook on pretrain and pretest splits
    # prerun_notebook()
    
    run_notebook()
    print(f"[notebook] executed solution.ipynb in {_RUN_MS} ms")
    zip_path = locate_submission_zip()
    print(f"=== scoring submission from {zip_path} ===")
    score_submission(zip_path)


if __name__ == "__main__":
    main()
