"""
Yandex Contest grader — Text Boundary Detection (podman sandbox).

Flow (run by CI, on the default git+podman image):
  1. run_notebook(): execute $REPO_NAME/solution.ipynb INSIDE a podman container
     built from the pytorch runtime image (deps baked in at build time). The
     container runs `--network=none`; the GPU is handed in with `--device`, and the
     offline model bundle + data cross the boundary as read-only bind mounts:
       - dataset/<TRAIN_SPLIT>/  -> mounted at dataset/train, with its public
         answers.jsonl layered back in from the dataset root
       - dataset/<GRADE_SPLIT>/  -> the hidden graded rows, mounted whole at the
         fixed public name dataset/test_public (ground truth is NOT in this folder)
       - models/                 -> offline bge-base-en-v1.5 bundle (HF_*_OFFLINE set)
     $REPO is the read-write /work volume: solution.ipynb in, answers.jsonl +
     executed.ipynb out.
  2. score_submission(): read $REPO/answers.jsonl, score against the hidden
     dataset/<GRADE_SPLIT>_answers.jsonl, write report.json. Pure Python -> runs on
     the host default image (no torch/transformers needed outside the container).

Answer files live at the dataset ROOT (dataset/train_answers.jsonl,
dataset/<GRADE_SPLIT>_answers.jsonl), NOT inside the split folders -- so a graded
split can be bind-mounted whole with no ground truth inside it.

GRADE_SPLIT is 'test_leaderboard_a' (live), 'test_leaderboard_b' (final), or
'pretest' (dry run, paired with TRAIN_SPLIT=pretrain).
Scoring (per sample): score_i = exp(-|pred_i - true_i| / TAU), TAU = 100;
total = 100 * mean(score_i), reported at full precision.

Verdicts: OK / RuntimeError / TimeLimitExceeded / PresentationError / (crash).
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

TAU = 100.0

# Per-round time budget, derived from the split so the two can never drift apart.
#
#   test_leaderboard_a (live)  -> 600s, the 10 minutes the statement promises.
#   test_leaderboard_b (final) -> 1200s, double that.
#
# Why b differs: identical submissions were measured at 485s on one runner and
# 611s on another -- 1.26x variance for the same work. At a 600s limit that makes
# a full-budget solution a coin flip depending on which VM it lands on, which is
# not something to decide a final ranking on. Doubling covers that variance with
# room to spare (600 x 1.26 = 756s) without turning the final round into a
# different competition from the one contestants prepared for.
#
# NOTEBOOK_TIMEOUT (per cell, inside nbconvert) is always kept ABOVE the wall
# clock so a slow run reports TimeLimitExceeded rather than RuntimeError.
_GRADE_SPLIT_FOR_BUDGET = os.environ.get("GRADE_SPLIT", "test_leaderboard_a")
if _GRADE_SPLIT_FOR_BUDGET == "test_leaderboard_b":
    _WALL_DEFAULT, _CELL_DEFAULT = "1200", "1350"
else:
    _WALL_DEFAULT, _CELL_DEFAULT = "600", "720"

NOTEBOOK_TIMEOUT_SEC = int(os.environ.get("NOTEBOOK_TIMEOUT_SEC", _CELL_DEFAULT))
WALL_CLOCK_BUDGET_SEC = int(os.environ.get("WALL_CLOCK_BUDGET_SEC", _WALL_DEFAULT))
if NOTEBOOK_TIMEOUT_SEC <= WALL_CLOCK_BUDGET_SEC:
    print(f"WARNING: NOTEBOOK_TIMEOUT_SEC ({NOTEBOOK_TIMEOUT_SEC}) is not above "
          f"WALL_CLOCK_BUDGET_SEC ({WALL_CLOCK_BUDGET_SEC}); a slow run will report "
          f"RuntimeError instead of TimeLimitExceeded", file=sys.stderr)
MAX_NOTEBOOK_BYTES = int(os.environ.get("MAX_NOTEBOOK_BYTES", "1048576"))  # code only
LOG_TAIL_BYTES = 65536

# podman sandbox knobs (shared across problems -- copy verbatim, edit only volumes)
RUNTIME_IMAGE = os.environ.get("RUNTIME_IMAGE",
                               "cr.yandex/crpe6hs3eavcafkcisb5/ioai-gitlab:20260725")
GPU_DEVICE = os.environ.get("GPU_DEVICE", "nvidia.com/gpu=all")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "solution-run")
PODMAN = os.environ.get("PODMAN", "podman")

CI_ROOT = Path(__file__).resolve().parent
DATASET_ROOT = Path(os.environ.get("DATASET_ROOT", "/problem/dataset")).resolve()
HIDDEN_MODELS_DIR = Path(os.environ.get("MODELS_ROOT", "/problem/models")).resolve()

GRADE_SPLIT = os.environ.get("GRADE_SPLIT", "test_leaderboard_a")
# Which split is mounted as the notebook's dataset/train. Pair TRAIN_SPLIT=pretrain
# with GRADE_SPLIT=pretest for a fast end-to-end dry run on 200/60 passages.
TRAIN_SPLIT = os.environ.get("TRAIN_SPLIT", "train")
PUBLIC_ALIAS = "test_public"                                 # fixed name every notebook reads

# Answer files live at the dataset ROOT as <split>_answers.jsonl, NOT inside the
# split folders -- so a graded split directory can be bind-mounted whole into the
# participant container with no ground truth inside it.
HIDDEN_TRAIN_DIR = DATASET_ROOT / TRAIN_SPLIT                # data.jsonl only
HIDDEN_GRADED_DIR = DATASET_ROOT / GRADE_SPLIT               # data.jsonl only (no answers)
HIDDEN_TRAIN_ANSWERS = DATASET_ROOT / f"{TRAIN_SPLIT}_answers.jsonl"   # public ground truth
HIDDEN_ANSWERS = DATASET_ROOT / f"{GRADE_SPLIT}_answers.jsonl"         # hidden ground truth

REPO_NAME = os.environ.get("REPO_NAME", "submission")
REPO_DIR = (CI_ROOT / REPO_NAME).resolve()                   # RW work volume
NOTEBOOK_PATH = REPO_DIR / "solution.ipynb"
SUBMISSION_PATH = REPO_DIR / "answers.jsonl"                 # written by the notebook
EXECUTED_IN_REPO = REPO_DIR / "executed.ipynb"

# container-side mount points (what the notebook sees)
C_WORK = "/work"
C_DATASET = f"{C_WORK}/dataset"
C_MODELS = f"{C_WORK}/models"

REPORT_PATH = Path("report.json")
EXECUTED_NB = Path("executed.ipynb")

# Published BACK to the participant as an ERROR artifact. Contest's report schema
# has nowhere to put a human-readable reason beside a score, so without this a
# RuntimeError reaches the contestant as a bare verdict with no traceback -- the
# reason exists only in our job log, which they cannot see.
RUN_LOG = Path("executed_output.log")          # full stdout+stderr, job artifact
RUN_LOG_TAIL = Path("executed_tail.log")       # trimmed copy, published
LOG_TAIL_LINES = int(os.environ.get("LOG_TAIL_LINES", "300"))
TEST_NAME = "mean_score"
ARTIFACT_FILES = ((RUN_LOG_TAIL, "ERROR"),)

# 0, not None: a submission rejected BEFORE execution (missing/oversized notebook)
# must still report a checking time, so runningTime is always present.
_RUN_MS = 0


# --------------------------------------------------------------------------- #
# report helpers
# --------------------------------------------------------------------------- #
def write_report(*, score: float, verdict: str, message: str) -> None:
    """Write report.json.

    `report.result` is a oneOf in Contest's report schema: EITHER `score` (a plain
    number) OR `message` (a STRING holding encoded JSON) -- never both. Sending both
    fails schema validation in `publish`, which fails send_report, which makes
    Contest record a Crash for a submission that graded fine.

    We send `message`. A bare `score` number does publish, but it does not render in
    the Contest interface -- the monitor reads the encoded payload. The key is the
    last character of GRADE_SPLIT, so test_leaderboard_a reports {"a": 41.7} and
    test_leaderboard_b reports {"b": ...}, giving the live and final rounds their
    own monitor columns. Same convention as the other IOAI problems.
    """
    if verdict != "OK":
        # The verdict alone does not say why, and the schema has nowhere to carry a
        # message beside a score -- so the reason goes into the log we publish.
        with RUN_LOG.open("a") as fh:
            fh.write(f"\ngrader: {verdict}: {message}\n")

    test = {"testName": TEST_NAME, "testsetName": "tests",
            "verdict": verdict, "score": float(score),
            "runningTime": int(_RUN_MS)}
    encoded_score = json.dumps({GRADE_SPLIT[-1]: float(score)})
    report = {"report": {"result": {"message": encoded_score}, "tests": [test]}}
    artifacts = report_artifacts()
    if artifacts:
        report["artifacts"] = artifacts
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    # Raw repr, not a fixed number of decimals: the published score is unrounded,
    # so the log must show the same value or the artifact is the only way to read it.
    print(f"[{verdict}] score={score!r} | {message} | {_RUN_MS} ms")


def write_log_tail() -> None:
    """Trim the run log to its last lines for publication back to the participant."""
    if not RUN_LOG.is_file():
        return
    lines = RUN_LOG.read_text(errors="replace").splitlines(keepends=True)
    dropped = len(lines) - LOG_TAIL_LINES
    header = f"[{dropped} earlier lines omitted]\n" if dropped > 0 else ""
    RUN_LOG_TAIL.write_text(header + "".join(lines[-LOG_TAIL_LINES:]))


def report_artifacts() -> list[dict]:
    """Files published beside the report.

    `artifacts` is a top-level sibling of `report`; each entry needs a `testName`
    naming a row in report.tests, a `testDataType` from the schema's enum
    (INPUT / OUTPUT / ANSWER / CHECKER_ERROR / ERROR), and a readable `path`.
    Missing or empty files are skipped so an entry never dangles.
    """
    write_log_tail()
    return [{"testName": TEST_NAME, "testDataType": kind, "path": str(path)}
            for path, kind in ARTIFACT_FILES
            if path.is_file() and path.stat().st_size > 0]


def fail(message: str, verdict: str) -> None:
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


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name} line {ln}: invalid JSON ({exc})")
    return records


# --------------------------------------------------------------------------- #
# podman sandbox
# --------------------------------------------------------------------------- #
def _volume_args() -> list[str]:
    """Bind mounts crossing the sandbox boundary.

      $REPO                        -> /work                  (RW: notebook + outputs)
      dataset/<TRAIN_SPLIT>/       -> /work/dataset/train     (RO) + its public answers
      dataset/<GRADE_SPLIT>/       -> /work/dataset/test_public (RO), answers ABSENT
      models/                      -> /work/models            (RO: offline bge bundle)

    Because the answer files live OUTSIDE the split folders, the graded split mounts
    as one clean whole-dir volume with no ground truth inside it, and train's public
    answers are re-attached with a single nested file mount. The notebook therefore
    sees exactly the layout it saw in Jupyter: dataset/train/{data,answers}.jsonl and
    dataset/test_public/data.jsonl.
    """
    return [
        # RW: solution.ipynb in, answers.jsonl + executed.ipynb out
        "-v", f"{REPO_DIR}:{C_WORK}",
        # RO: train data, with its public answers layered back in
        "-v", f"{HIDDEN_TRAIN_DIR}:{C_DATASET}/train:ro",
        "-v", f"{HIDDEN_TRAIN_ANSWERS}:{C_DATASET}/train/answers.jsonl:ro",
        # RO: hidden eval set at the fixed public name (no answers.jsonl in the folder)
        "-v", f"{HIDDEN_GRADED_DIR}:{C_DATASET}/{PUBLIC_ALIAS}:ro",
        # RO: offline model bundle
        "-v", f"{HIDDEN_MODELS_DIR}:{C_MODELS}:ro",
    ]


def _podman_run(inner_cmd, *, timeout, stdout, stderr):
    """`podman run` the runtime image: no network, GPU via --device, volumes only."""
    cmd = [
        PODMAN, "run", "--rm", "--name", CONTAINER_NAME,
        "--network=none",
        "--device", GPU_DEVICE,
        *_volume_args(),
        "-w", C_WORK,
        # The IOAI runtime runs the notebook as a NON-ROOT user, and it has no
        # writable /tmp of its own. Without these, nbconvert dies with "No usable
        # temporary directory found" and matplotlib/HF cache writes fail.
        "--tmpfs", "/tmp:rw,exec,mode=1777,size=4g",
        "-e", "TMPDIR=/tmp",
        "-e", "MPLCONFIGDIR=/tmp",
        "-e", "HF_HOME=/tmp/hf",
        "-e", "HF_HUB_OFFLINE=1",
        "-e", "TRANSFORMERS_OFFLINE=1",
        "-e", f"MODELS_DIR={C_MODELS}",
        RUNTIME_IMAGE,
        "bash", "-lc", inner_cmd,
    ]
    print("running:", " ".join(cmd))
    try:
        return subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run([PODMAN, "rm", "-f", CONTAINER_NAME],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raise


def preflight_dataset():
    """Fail fast if the dataset does not match what this grader expects.

    Checking these up front turns a provisioning mistake into an immediate Crash
    instead of one discovered only after a full notebook run -- and, critically, it
    catches the case where a graded split still carries its answers.jsonl INSIDE the
    split directory. That directory is bind-mounted whole into the notebook's
    container, so ground truth sitting in it would be handed straight to the
    participant's code.
    """
    print("=== dataset preflight ===")
    print(f"  DATASET_ROOT={DATASET_ROOT}  TRAIN_SPLIT={TRAIN_SPLIT}  GRADE_SPLIT={GRADE_SPLIT}")
    problems = []
    for label, path in (("train split", HIDDEN_TRAIN_DIR),
                        ("graded split", HIDDEN_GRADED_DIR),
                        ("models", HIDDEN_MODELS_DIR)):
        if not path.is_dir():
            problems.append(f"{label} directory missing: {path}")
    for label, path in (("train data", HIDDEN_TRAIN_DIR / "data.jsonl"),
                        ("graded data", HIDDEN_GRADED_DIR / "data.jsonl"),
                        ("train answers", HIDDEN_TRAIN_ANSWERS),
                        ("graded ground truth", HIDDEN_ANSWERS)):
        if not path.is_file():
            problems.append(f"{label} file missing: {path}")
    # The graded split is mounted whole and read-only into the sandbox: nothing that
    # reveals the boundary may live inside it.
    leaked = HIDDEN_GRADED_DIR / "answers.jsonl"
    if leaked.exists():
        problems.append(
            f"ground truth is INSIDE the graded split ({leaked}) -- it would be "
            f"mounted into the participant container. Answers belong at the dataset "
            f"root as {GRADE_SPLIT}_answers.jsonl")
    if problems:
        for p in problems:
            print(f"FATAL: {p}", file=sys.stderr)
        sys.exit(1)
    n_graded = sum(1 for _ in (HIDDEN_GRADED_DIR / "data.jsonl").open(encoding="utf-8"))
    n_truth = len(read_jsonl(HIDDEN_ANSWERS))
    print(f"  ok: {n_graded} rows in {GRADE_SPLIT}, {n_truth} ground-truth entries")
    if n_graded != n_truth:
        print(f"FATAL: {GRADE_SPLIT} has {n_graded} rows but its ground truth has "
              f"{n_truth} entries", file=sys.stderr)
        sys.exit(1)
    audit_other_rounds()


def audit_other_rounds():
    """Report the state of the rounds we are NOT grading. Informational only.

    Switching GRADE_SPLIT must never be the moment we discover the next split is
    misprovisioned -- by then it is the final ranking and there is no time to fix it.
    Every ordinary submission audits the other rounds for free, so the log says
    whether test_leaderboard_b is ready long before it is needed.
    """
    print("  --- other rounds (informational, not graded now) ---")
    for split in ("pretrain", "pretest", "train",
                  "test_leaderboard_a", "test_leaderboard_b"):
        if split in (GRADE_SPLIT, TRAIN_SPLIT):
            continue
        d = DATASET_ROOT / split
        truth = DATASET_ROOT / f"{split}_answers.jsonl"
        if not (d / "data.jsonl").is_file():
            print(f"    {split}: ABSENT")
            continue
        n = sum(1 for _ in (d / "data.jsonl").open(encoding="utf-8"))
        bits = [f"{n} rows"]
        bits.append(f"{len(read_jsonl(truth))} ground-truth entries" if truth.is_file()
                    else f"ROOT ANSWERS MISSING -- grading this round would Crash "
                         f"(expected {truth.name})")
        if (d / "answers.jsonl").exists():
            bits.append("!! answers.jsonl INSIDE the split -- grading this round would "
                        "expose ground truth to the participant notebook")
        print(f"    {split}: " + "; ".join(bits))


def preflight_gpu():
    """Fail fast (before the notebook) if the sandbox sees no CUDA GPU."""
    check = ("import sys, torch; ok = torch.cuda.is_available(); "
             "print('torch', torch.__version__, 'cuda', ok, 'devices', torch.cuda.device_count()); "
             "sys.exit(0 if ok else 1)")
    # bash -lc, not a bare `python`: in the IOAI runtime image python reaches PATH
    # only through the login profile (same lesson as ioai_field's exit-127).
    cmd = [PODMAN, "run", "--rm", "--network=none", "--device", GPU_DEVICE,
           RUNTIME_IMAGE, "bash", "-lc", f"python -c {check!r}"]
    print("=== GPU preflight ===")
    if subprocess.run(cmd).returncode != 0:
        print("FATAL: no CUDA GPU visible inside the sandbox", file=sys.stderr)
        sys.exit(1)


def run_notebook() -> None:
    if not NOTEBOOK_PATH.exists():
        fail(f"solution.ipynb not found at {NOTEBOOK_PATH}", verdict="PresentationError")
    nb_size = NOTEBOOK_PATH.stat().st_size
    if nb_size > MAX_NOTEBOOK_BYTES:
        fail(f"solution.ipynb is {nb_size/1e6:.2f} MB, over the {MAX_NOTEBOOK_BYTES/1e6:.2f} MB limit "
             f"(submit code only -- do not embed data, weights or outputs)",
             verdict="PresentationError")

    # $REPO is bind-mounted as the container's RW /work, but it is owned by the CI
    # user on the host while the IOAI runtime executes the notebook as a non-root
    # user. Without this the notebook cannot write its answers file: the first real
    # pipeline run died on `PermissionError: 'answers.jsonl'` after successfully
    # reading train. World-writable is safe -- the directory holds only the
    # submission and its outputs, and the container has no network.
    subprocess.run(["chmod", "-R", "0777", str(REPO_DIR)], check=False)

    inner = (
        "python -m nbconvert --to notebook --execute "
        "--output executed.ipynb "
        f"--ExecutePreprocessor.timeout={NOTEBOOK_TIMEOUT_SEC} "
        "--ExecutePreprocessor.kernel_name=python3 "
        "solution.ipynb"
    )

    global _RUN_MS
    t0 = time.perf_counter()
    # stdout and stderr are interleaved into ONE log so the participant sees their
    # prints and the traceback in the order they happened. A TLE still leaves
    # whatever the notebook managed to print, because the file is written as the
    # process runs -- so `fail()` below can publish it.
    with RUN_LOG.open("wb") as out:
        try:
            proc = _podman_run(inner, timeout=WALL_CLOCK_BUDGET_SEC,
                               stdout=out, stderr=subprocess.STDOUT)
        except subprocess.TimeoutExpired:
            _RUN_MS = int((time.perf_counter() - t0) * 1000)
            fail(f"solution.ipynb exceeded the wall-clock budget of {WALL_CLOCK_BUDGET_SEC}s",
                 verdict="TimeLimitExceeded")
    _RUN_MS = int((time.perf_counter() - t0) * 1000)

    if EXECUTED_IN_REPO.exists():
        shutil.copy(EXECUTED_IN_REPO, EXECUTED_NB)
    print("--- notebook output (tail) ---")
    print(tail_file(RUN_LOG))
    if proc.returncode != 0:
        tail = "\n".join(tail_file(RUN_LOG).splitlines()[-10:]).strip() or "no output"
        fail(f"solution.ipynb failed to execute (exit {proc.returncode}). last error: {tail}",
             verdict="RuntimeError")


def score_submission() -> None:
    if not SUBMISSION_PATH.exists():
        fail(f"answers.jsonl not found at {SUBMISSION_PATH} after notebook executed",
             verdict="PresentationError")
    try:
        pred_records = read_jsonl(SUBMISSION_PATH)
    except ValueError as exc:
        fail(str(exc), verdict="PresentationError")

    try:
        true_records = read_jsonl(HIDDEN_ANSWERS)
    except ValueError as exc:
        print(f"INTERNAL: ground truth parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    true_by_id: dict[str, int] = {}
    for rec in true_records:
        if "id" not in rec or "boundary_char_index" not in rec:
            print(f"INTERNAL: ground truth record missing fields: {rec}", file=sys.stderr)
            sys.exit(1)
        true_by_id[rec["id"]] = int(rec["boundary_char_index"])

    if not true_by_id:
        print("INTERNAL: ground truth is empty", file=sys.stderr)
        sys.exit(1)

    seen_ids: set[str] = set()
    scores: list[float] = []
    for i, rec in enumerate(pred_records):
        if "id" not in rec or "boundary_char_index" not in rec:
            fail(f"submission record {i} missing 'id' or 'boundary_char_index': {rec}",
                 verdict="PresentationError")
        rec_id = rec["id"]
        if rec_id in seen_ids:
            fail(f"submission has duplicate id: {rec_id!r}", verdict="PresentationError")
        seen_ids.add(rec_id)
        if rec_id not in true_by_id:
            fail(f"submission has unknown id: {rec_id!r}", verdict="PresentationError")
        try:
            pred = int(rec["boundary_char_index"])
        except (TypeError, ValueError):
            fail(f"id {rec_id!r}: boundary_char_index must be integer, got {rec['boundary_char_index']!r}",
                 verdict="PresentationError")
        true = true_by_id[rec_id]
        scores.append(math.exp(-abs(pred - true) / TAU))

    missing_ids = set(true_by_id) - seen_ids
    if missing_ids:
        fail(f"submission missing {len(missing_ids)} id(s); first: {sorted(missing_ids)[:3]}",
             verdict="PresentationError")

    mean_score = sum(scores) / len(scores)
    # Full precision, not rounded. With 380 samples one whole sample is worth
    # 0.26 points, but a prediction landing one character closer moves the score
    # by only 0.0026 -- rounding to 2 decimals made those improvements invisible
    # and could tie teams that are not actually tied.
    write_report(score=100 * mean_score, verdict="OK",
                 message=f"mean={mean_score!r} over {len(scores)} samples")


def main() -> None:
    preflight_dataset()
    preflight_gpu()
    run_notebook()
    score_submission()


if __name__ == "__main__":
    main()
