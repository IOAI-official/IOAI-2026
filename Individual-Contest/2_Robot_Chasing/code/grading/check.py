"""
Yandex Contest grader — Catch the Robot.

Flow (run by CI, on the job image, which carries the dataset at /problem/dataset):
  1. run_notebook(): execute $REPO_NAME/solution.ipynb INSIDE a podman container
     built from NOTEBOOK_IMAGE (the shared IOAI runtime -- every statement library
     is already present, so nothing is pip-installed at grade time). The container
     runs with `--network=none`; the GPU is handed in with `--device`. Data crosses
     the sandbox boundary through volumes only:
       - dataset -> read-only volumes (train + the graded split, answers withheld)
       - $REPO   -> read-write volume (holds solution.ipynb; the notebook writes its
                    predictions.json + executed.ipynb back here)
     The notebook sees the same paths as a participant does locally
     (dataset/train, dataset/test_public), so nothing in solution.ipynb has to change.
  2. score_submission(): load $REPO_NAME/predictions.json (a JSON list of ints 0-5)
     from the RW volume, score against the hidden ground truth
     dataset/<GRADE_SPLIT>_answers.json, write report.json. Pure Python -> runs on
     the host image, no numpy/torch needed outside the container.

Answer files live at the dataset ROOT (dataset/train_answers.json,
dataset/<GRADE_SPLIT>_answers.json), NOT inside the split folders -- so a graded
split directory contains only observations.json and can be mounted whole without
ever exposing the ground truth.

GRADE_SPLIT is 'pretest' (dry runs), 'test_leaderboard_a' (live) or
'test_leaderboard_b' (final).

Metric: mean over the 6 robots of (fraction of that robot's moves predicted
correctly), reported on a 0-100 scale. Every robot counts equally.

Verdicts: OK / RuntimeError / TimeLimitExceeded / PresentationError / (crash).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

NOTEBOOK_TIMEOUT_SEC = int(os.environ.get("NOTEBOOK_TIMEOUT_SEC", "1200"))
WALL_CLOCK_BUDGET_SEC = int(os.environ.get("WALL_CLOCK_BUDGET_SEC", "900"))
MAX_NOTEBOOK_BYTES = int(os.environ.get("MAX_NOTEBOOK_BYTES", "1048576"))  # 1 MB: code only,
# so nobody can smuggle weights or precomputed answers inside the notebook itself.
LOG_TAIL_BYTES = 65536
NUM_ROBOTS = 6
NUM_ACTIONS = 6

# podman sandbox knobs
NOTEBOOK_IMAGE = os.environ["NOTEBOOK_IMAGE"]
GPU_DEVICE = os.environ.get("GPU_DEVICE", "nvidia.com/gpu=all")   # CDI device handed to --device
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "solution-run")
PODMAN = os.environ.get("PODMAN", "podman")

CI_ROOT = Path(__file__).resolve().parent
# Root of the locked dataset. Provisioned on the grading host at /problem/dataset
# (baked into the job image) rather than shipped in the repo via LFS, so a
# submission never drags the ~120 MB train split behind it. Overridable via env
# for local testing.
DATASET_ROOT = Path(os.environ.get("DATASET_ROOT", "/problem/dataset")).resolve()

# Which split is graded: pretest (dry runs) | test_leaderboard_a (live) |
# test_leaderboard_b (final). Switching rounds is this variable and nothing else.
GRADE_SPLIT = os.environ.get("GRADE_SPLIT", "test_leaderboard_a")
# Which split is mounted as the notebook's dataset/train. Pair TRAIN_SPLIT=pretrain
# with GRADE_SPLIT=pretest for a fast end-to-end dry run on 3000/600 rows.
TRAIN_SPLIT = os.environ.get("TRAIN_SPLIT", "train")
PUBLIC_ALIAS = "test_public"          # the fixed folder name every notebook reads

# Answer files live at the dataset ROOT (outside the split folders), so a split dir
# holds only observations.json -- the graded ground truth is never inside the tree
# the notebook can see.
HIDDEN_TRAIN_DIR = DATASET_ROOT / TRAIN_SPLIT                  # observations.json
HIDDEN_GRADED_DIR = DATASET_ROOT / GRADE_SPLIT                 # observations.json (no labels)
HIDDEN_TRAIN_ANSWERS = DATASET_ROOT / f"{TRAIN_SPLIT}_answers.json"   # public train labels
HIDDEN_ANSWERS = DATASET_ROOT / f"{GRADE_SPLIT}_answers.json"  # hidden graded ground truth
HIDDEN_OBS = HIDDEN_GRADED_DIR / "observations.json"           # graded observations

REPO_NAME = os.environ.get("REPO_NAME", "submission")
REPO_DIR = (CI_ROOT / REPO_NAME).resolve()                     # RW work volume for the container
NOTEBOOK_PATH = REPO_DIR / "solution.ipynb"
SUBMISSION_PATH = REPO_DIR / "predictions.json"                # written by the notebook
EXECUTED_IN_REPO = REPO_DIR / "executed.ipynb"                 # nbconvert output, in the RW volume

# container-side mount points (what the notebook sees)
C_WORK = "/work"
C_DATASET = f"{C_WORK}/dataset"

REPORT_PATH = Path("report.json")
EXECUTED_NB = Path("executed.ipynb")
# nbconvert's two streams are merged (2>&1) into ONE log, so warnings and the
# traceback that follows them stay in the order they were produced. Safe here
# because nothing parses this notebook's stdout -- it is captured, not a protocol.
RUN_LOG = Path("executed_output.log")
# The trimmed copy published back to the participant; RUN_LOG stays untrimmed in
# the job artifacts for us.
RUN_LOG_TAIL = Path("executed_tail.log")
LOG_TAIL_LINES = int(os.environ.get("LOG_TAIL_LINES", "300"))
# The code cells of the executed notebook, as plain text. Published INSTEAD of
# executed.ipynb: that file carries every cell output inline and runs to tens of
# megabytes of JSON, which does not render as a report artifact. Nothing is lost --
# the outputs and the traceback are in the run log. The full notebook stays in the
# job artifacts for us.
EXECUTED_PY = Path("executed.py")

# Files referenced from report.json artifacts[], as (path, testDataType). The
# schema's enum is INPUT / OUTPUT / ANSWER / CHECKER_ERROR / ERROR.
ARTIFACT_FILES = (
    (EXECUTED_PY, "OUTPUT"),
    (RUN_LOG_TAIL, "ERROR"),
)
TEST_NAME = "per_robot_accuracy"


# --------------------------------------------------------------------------- #
# report helpers
# --------------------------------------------------------------------------- #
# Notebook execution time in ms, set by run_notebook(). Starts at 0 rather than None
# so that EVERY report carries runningTime -- including failures that happen before
# the notebook ever runs (missing / misnamed / oversized submission), where 0 ms is
# the honest answer. Contest must never receive a report without a checking time.
_RUN_MS = 0


def write_log_tail():
    """Write the published, trimmed copy of the run log.

    The last lines are the useful ones -- the traceback, or the grader's reason for
    the verdict -- and whatever is dropped is said so rather than silently cut.
    """
    if not RUN_LOG.is_file():
        return
    lines = RUN_LOG.read_text(errors="replace").splitlines(keepends=True)
    dropped = len(lines) - LOG_TAIL_LINES
    header = f"[{dropped} earlier lines omitted]\n" if dropped > 0 else ""
    RUN_LOG_TAIL.write_text(header + "".join(lines[-LOG_TAIL_LINES:]))


def write_executed_script():
    """Extract the executed notebook's code cells into a plain-text script.

    A notebook is JSON, so this needs no second nbconvert run and no jupyter on the
    job image -- that conversion would have to happen here, outside the container
    where jupyter actually lives. Best effort: a notebook we cannot parse simply
    yields no OUTPUT artifact rather than failing the grading.
    """
    if not EXECUTED_NB.is_file():
        return
    try:
        cells = json.loads(EXECUTED_NB.read_text(errors="replace"))["cells"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"WARN: cannot read {EXECUTED_NB} for the OUTPUT artifact: {exc}",
              file=sys.stderr)
        return
    chunks = []
    for n, cell in enumerate(cells, 1):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source") or [])
        if source.strip():
            chunks.append(f"# --- cell {n} ---\n{source}")
    EXECUTED_PY.write_text("\n\n".join(chunks) + "\n" if chunks else "")


def report_artifacts():
    """Files published beside the report: the executed code and the run log.

    `artifacts` is a top-level sibling of `report`; every entry needs a `testName`
    naming a row in report.tests, a `testDataType` from the schema's enum, and a
    `path` the publish job can read -- the file itself, not its contents. Missing or
    empty files are skipped, so an entry never dangles.
    """
    write_log_tail()
    write_executed_script()
    return [
        {"testName": TEST_NAME, "testDataType": data_type, "path": str(path)}
        for path, data_type in ARTIFACT_FILES
        if path.is_file() and path.stat().st_size > 0
    ]


def write_report(*, score, verdict, message, details=None):
    """Write report.json.

    The CALCULATOR monitor used by the live leaderboard reads the score from a
    JSON-serialized mapping in ``message``.  Human-readable diagnostics stay in
    the CI log -- and, for a failure, in the published run log, since the schema
    has nowhere to carry a reason beside a score.
    """
    if verdict != "OK":
        with RUN_LOG.open("a") as fh:
            fh.write(f"grader: {verdict}: {message}\n")
    test = {"testName": TEST_NAME, "testsetName": "tests",
            "verdict": verdict, "score": float(score),
            "runningTime": int(_RUN_MS)}
    # Keyed by the graded round's letter, so the live and final rounds get their own
    # monitor columns -- same convention as the other IOAI problems. A hardcoded key
    # would publish round B's results into round A's column.
    result = {
        "message": json.dumps({GRADE_SPLIT[-1]: float(score)},
                              separators=(",", ":")),
    }
    report = {"report": {"result": result, "tests": [test]}}
    artifacts = report_artifacts()
    if artifacts:
        report["artifacts"] = artifacts
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"[{verdict}] score={score} | {message} | {_RUN_MS} ms")


def fail(message, verdict):
    write_report(score=0.0, verdict=verdict, message=message)
    sys.exit(0)


def tail_file(path, nbytes=LOG_TAIL_BYTES):
    if not path.exists():
        return ""
    size = path.stat().st_size
    with path.open("rb") as fh:
        if size > nbytes:
            fh.seek(size - nbytes)
        return fh.read().decode(errors="replace")


def _flatten_ints(x):
    """Flatten an arbitrarily-nested list into a flat list (mirrors numpy .ravel()),
    so a participant writing a column vector is graded rather than rejected.
    Non-int leaves are returned as-is, for validation to reject."""
    out = []
    stack = [x]
    while stack:
        v = stack.pop()
        if isinstance(v, list):
            stack.extend(reversed(v))
        else:
            out.append(v)
    return out


# --------------------------------------------------------------------------- #
# podman sandbox
# --------------------------------------------------------------------------- #
def _volume_args() -> list[str]:
    """Bind mounts that cross the sandbox boundary, matching the statement's layout.

    The dataset is read-only; $REPO is read-write (the notebook writes its
    predictions.json + executed.ipynb there). The notebook reads exactly what a
    participant sees locally:

      dataset/train/observations.json  -> the training observations ...
      dataset/train/labels.json        -> ... plus their public labels
      dataset/test_public/             -> the hidden eval set: observations.json only,
                                          with labels.json genuinely ABSENT

    Because the answer files live OUTSIDE the split folders, the graded split mounts
    as one clean whole-dir volume with no ground truth inside it, and train's public
    labels are re-attached with a single nested file mount under the name the
    statement documents.
    """
    return [
        # RW: solution.ipynb in, predictions.json + executed.ipynb out
        "-v", f"{REPO_DIR}:{C_WORK}",
        # RO: train observations, with the public labels layered back in
        "-v", f"{HIDDEN_TRAIN_DIR}:{C_DATASET}/train:ro",
        "-v", f"{HIDDEN_TRAIN_ANSWERS}:{C_DATASET}/train/labels.json:ro",
        # RO: hidden eval set at the fixed public name (no labels.json in the folder)
        "-v", f"{HIDDEN_GRADED_DIR}:{C_DATASET}/{PUBLIC_ALIAS}:ro",
    ]


def _podman_run(inner_cmd, *, timeout, stdout, stderr):
    """`podman run` the runtime image: no network, GPU via --device, volumes only."""
    cmd = [
        PODMAN, "run", "--rm", "--name", CONTAINER_NAME,
        "--network=none",
        "--device", GPU_DEVICE,
        *_volume_args(),
        "-w", C_WORK,
        NOTEBOOK_IMAGE,
        "bash", "-lc", inner_cmd,
    ]
    print("running:", " ".join(cmd))
    try:
        return subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=timeout)
    except subprocess.TimeoutExpired:
        # `podman run` was killed on the host; force-remove the container so it does
        # not keep the GPU busy for the next retry.
        subprocess.run([PODMAN, "rm", "-f", CONTAINER_NAME],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raise


def preflight_dataset():
    """Fail fast if the baked dataset does not match what this grader expects.

    Every path below is required for the selected round. Checking them up front
    turns a provisioning mistake into an immediate Crash instead of one discovered
    only after a full notebook run -- and, critically, it catches the case where a
    graded split still carries its labels INSIDE the split directory. That directory
    is bind-mounted whole into the notebook's container, so ground truth sitting in
    it would be handed straight to the participant's code.
    """
    print("=== dataset preflight ===")
    print(f"  DATASET_ROOT={DATASET_ROOT}  TRAIN_SPLIT={TRAIN_SPLIT}  GRADE_SPLIT={GRADE_SPLIT}")
    problems = []
    for label, path in (("train split", HIDDEN_TRAIN_DIR),
                        ("graded split", HIDDEN_GRADED_DIR)):
        if not path.is_dir():
            problems.append(f"{label} directory missing: {path}")
    for label, path in (("train observations", HIDDEN_TRAIN_DIR / "observations.json"),
                        ("graded observations", HIDDEN_OBS),
                        ("train labels", HIDDEN_TRAIN_ANSWERS),
                        ("graded ground truth", HIDDEN_ANSWERS)):
        if not path.is_file():
            problems.append(f"{label} file missing: {path}")
    # The graded split is mounted whole and read-only into the sandbox: nothing that
    # reveals the moves may live inside it.
    for leaked in ("labels.json", "answers.json"):
        p = HIDDEN_GRADED_DIR / leaked
        if p.exists():
            problems.append(
                f"ground truth is INSIDE the graded split ({p}) -- it would be "
                f"mounted into the participant container. Answers belong at the "
                f"dataset root as {GRADE_SPLIT}_answers.json")
    if problems:
        for p in problems:
            print(f"FATAL: {p}", file=sys.stderr)
        sys.exit(1)

    n_graded = len(json.loads(HIDDEN_OBS.read_text()))
    n_truth = len(_flatten_ints(json.loads(HIDDEN_ANSWERS.read_text())))
    print(f"  ok: {n_graded} observations in {GRADE_SPLIT}, {n_truth} ground-truth moves")
    if n_graded != n_truth:
        print(f"FATAL: {GRADE_SPLIT} has {n_graded} observations but its ground truth "
              f"has {n_truth} entries", file=sys.stderr)
        sys.exit(1)


def preflight_gpu():
    """Fail fast (before executing the notebook) if the sandbox sees no CUDA GPU.
    A missing GPU is an infra fault -> non-zero exit -> send_crash -> Crash, rather
    than silently grading on CPU or dying confusingly deep in the notebook."""
    check = ("import sys, torch; ok = torch.cuda.is_available(); "
             "print('torch', torch.__version__, 'cuda', ok, 'devices', torch.cuda.device_count()); "
             "sys.exit(0 if ok else 1)")
    cmd = [
        PODMAN, "run", "--rm", "--network=none", "--device", GPU_DEVICE,
        NOTEBOOK_IMAGE, "python", "-c", check,
    ]
    print("=== GPU preflight ===")
    if subprocess.run(cmd).returncode != 0:
        print("FATAL: no CUDA GPU visible inside the sandbox", file=sys.stderr)
        sys.exit(1)


def run_notebook():
    if not NOTEBOOK_PATH.exists():
        fail(f"solution.ipynb not found at {NOTEBOOK_PATH}", verdict="PresentationError")
    nb_size = NOTEBOOK_PATH.stat().st_size
    if nb_size > MAX_NOTEBOOK_BYTES:
        fail(f"solution.ipynb is {nb_size/1e6:.2f} MB, over the {MAX_NOTEBOOK_BYTES/1e6:.2f} MB limit "
             f"(submit code only -- do not embed data, weights or outputs)",
             verdict="PresentationError")

    # The CI job (and thus REPO_DIR) is owned by root, but the notebook runs inside
    # podman as an unprivileged user (uid 1000). Make the RW work volume world-writable
    # so that user can write predictions.json + executed.ipynb back to /work; otherwise
    # the notebook's final `json.dump(..., open("predictions.json", "w"))` dies with
    # PermissionError (EACCES).
    os.chmod(REPO_DIR, 0o777)

    # nbconvert runs INSIDE the container, in /work (the RW volume). Output paths are
    # relative, so they land back on the host under $REPO.
    inner = (
        "python -m nbconvert --to notebook --execute "
        "--output executed.ipynb "
        f"--ExecutePreprocessor.timeout={NOTEBOOK_TIMEOUT_SEC} "
        "--ExecutePreprocessor.kernel_name=python3 "
        "solution.ipynb"
    )

    global _RUN_MS
    t0 = time.perf_counter()
    with RUN_LOG.open("wb") as out:
        try:
            proc = _podman_run(inner, timeout=WALL_CLOCK_BUDGET_SEC,
                               stdout=out, stderr=subprocess.STDOUT)
        except subprocess.TimeoutExpired:
            _RUN_MS = int((time.perf_counter() - t0) * 1000)
            fail(f"solution.ipynb exceeded wall-clock budget of {WALL_CLOCK_BUDGET_SEC}s",
                 verdict="TimeLimitExceeded")
    _RUN_MS = int((time.perf_counter() - t0) * 1000)

    if EXECUTED_IN_REPO.exists():   # surface it as a top-level artifact
        shutil.copy(EXECUTED_IN_REPO, EXECUTED_NB)
    print("--- notebook output (tail) ---")
    print(tail_file(RUN_LOG))
    if proc.returncode != 0:
        tail = "\n".join(tail_file(RUN_LOG).splitlines()[-10:]).strip() or "no output"
        fail(f"solution.ipynb failed to execute (exit {proc.returncode}). last error: {tail}",
             verdict="RuntimeError")


def score_submission():
    if not SUBMISSION_PATH.exists():
        fail(f"predictions.json not found at {SUBMISSION_PATH} after notebook executed",
             verdict="PresentationError")
    try:
        raw = json.loads(SUBMISSION_PATH.read_text())
    except Exception as exc:  # noqa: BLE001
        fail(f"predictions.json is not valid JSON: {exc}", verdict="PresentationError")
    if not isinstance(raw, list):
        fail("predictions.json must be a JSON list of ints (0-5)", verdict="PresentationError")

    try:
        answers = _flatten_ints(json.loads(HIDDEN_ANSWERS.read_text()))
        obs = json.loads(HIDDEN_OBS.read_text())
    except Exception as exc:  # noqa: BLE001 - internal integrity
        print(f"INTERNAL: ground truth unreadable: {exc}", file=sys.stderr)
        sys.exit(1)

    if any(isinstance(a, bool) or not isinstance(a, int) or not 0 <= a < NUM_ACTIONS
           for a in answers):
        print("INTERNAL: ground truth must contain only integer actions 0-5",
              file=sys.stderr)
        sys.exit(1)

    preds = _flatten_ints(raw)
    if len(preds) != len(answers):
        fail(f"expected {len(answers)} predictions, got {len(preds)}", verdict="PresentationError")
    clean = []
    for x in preds:
        if isinstance(x, bool) or not isinstance(x, int):
            fail("predictions must be integers 0-5", verdict="PresentationError")
        if not 0 <= x < NUM_ACTIONS:
            fail("predictions must be in {0,1,2,3,4,5}", verdict="PresentationError")
        clean.append(x)

    correct = [0] * NUM_ROBOTS
    total = [0] * NUM_ROBOTS
    for p, a, o in zip(clean, answers, obs):
        r = int(o["robot_id"])
        if not 0 <= r < NUM_ROBOTS:
            print(f"INTERNAL: robot_id {r} is outside 0-{NUM_ROBOTS - 1}",
                  file=sys.stderr)
            sys.exit(1)
        total[r] += 1
        if p == a:
            correct[r] += 1

    per_robot = [correct[r] / total[r] for r in range(NUM_ROBOTS) if total[r] > 0]
    if not per_robot:
        print("INTERNAL: no robots found in observations", file=sys.stderr)
        sys.exit(1)
    mean = sum(per_robot) / len(per_robot)
    write_report(
        score=round(100.0 * mean, 4),
        verdict="OK",
        message=f"per_robot_accuracy={mean:.4f} over {len(per_robot)} robots",
        details={"per_robot_accuracy": round(mean, 6),
                 "robots": len(per_robot),
                 "per_robot": [round(a, 6) for a in per_robot],
                 "predictions": len(clean)},
    )


def main():
    preflight_dataset()
    preflight_gpu()
    run_notebook()
    score_submission()


if __name__ == "__main__":
    main()
