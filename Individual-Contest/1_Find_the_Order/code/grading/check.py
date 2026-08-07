"""
Yandex Contest grader — Find the Order.

Flow (run by CI, on the default git+podman image):
  1. run_notebook(): execute $REPO_NAME/solution.ipynb INSIDE a podman container
     built from the pytorch runtime image (all deps baked in at build time).
     The container runs with `--network=none`; the GPU is handed in with
     `--device`. Data crosses the sandbox boundary through volumes only:
       - dataset  -> read-only  volumes (train + graded split, answers withheld)
       - models   -> read-only  volume
       - $REPO    -> read-write volume (holds solution.ipynb; the notebook writes
                     its inferred answers.json + executed.ipynb back here)
     The notebook sees the same paths as before (dataset/test_public, models),
     so nothing in the participant solution.ipynb has to change.
  2. score_submission(): load $REPO_NAME/answers.json (produced in the RW volume),
     score against the hidden ground truth dataset/<GRADE_SPLIT>_answers.json, write
     report.json.

Answer files live at the dataset ROOT (dataset/train_answers.json,
dataset/<GRADE_SPLIT>_answers.json), NOT inside the split folders -- so a graded
split directory contains only audio + prefix.json and can be mounted whole without
ever exposing the ground truth.

GRADE_SPLIT is 'test_leaderboard_a' (live) or 'test_leaderboard_b' (final).

Metric: pairwise ordering accuracy. Per dialogue with n chunks,
    score = 1 - inversions / C(n, 2)   (n < 2 -> 1.0)
macro-averaged across dialogues, reported on a 0-100 scale.

Per the statement, a per-dialogue prediction that is missing or not a valid
permutation of 0..n-1 scores 0 for that dialogue (NOT a hard failure). Only a
missing or non-JSON submission file is a PresentationError.

This grader never reads the dataset audio or the model bundle -- it only hands
their directories to podman as volumes. The only dataset file it opens is the
tiny hidden ground-truth answers.json, which is unavoidable for scoring.

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

# The ONLY time limit is the wall clock, enforced on the host around `podman run`.
# There is deliberately no per-cell timeout: a per-cell limit can only ever produce
# the wrong verdict. If it fired first, nbconvert would raise CellExecutionError and
# exit non-zero, and the grader would report RuntimeError -- blaming the
# participant's code for what is actually a timeout. Disabled explicitly with -1
# rather than by omission, because nbconvert's default has changed across versions.
# The default here MATCHES the CI variable, so a missing variable cannot silently
# hand out a longer limit than the contest advertises.
WALL_CLOCK_BUDGET_SEC = int(os.environ.get("WALL_CLOCK_BUDGET_SEC", "900"))
MAX_NOTEBOOK_BYTES = int(os.environ.get("MAX_NOTEBOOK_BYTES", "1048576"))  # 1 MB: code only,
# so nobody can smuggle weights or precomputed answers inside the notebook itself.
LOG_TAIL_BYTES = 65536

# podman sandbox knobs
NOTEBOOK_IMAGE = os.environ["NOTEBOOK_IMAGE"]
GPU_DEVICE = os.environ.get("GPU_DEVICE", "nvidia.com/gpu=all")   # CDI device handed to --device
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "solution-run")
PODMAN = os.environ.get("PODMAN", "podman")

CI_ROOT = Path(__file__).resolve().parent
# Roots of the locked dataset + model bundle. These are provisioned on the grading
# host at /problem/{dataset,models} (bind-mounted into the job) rather than shipped
# in the repo via LFS, so a submission never carries the ~5 GB of assets. Overridable
# via env for local testing.
DATASET_ROOT = Path(os.environ.get("DATASET_ROOT", "/problem/dataset")).resolve()
HIDDEN_MODELS_DIR = Path(os.environ.get("MODELS_ROOT", "/problem/models")).resolve()

# Which split is graded: pretest (dry runs) | test_leaderboard_a (live) |
# test_leaderboard_b (final). Switching rounds is this variable and nothing else.
GRADE_SPLIT = os.environ.get("GRADE_SPLIT", "test_leaderboard_a")
# Which split is mounted as the notebook's dataset/train. Pair TRAIN_SPLIT=pretrain
# with GRADE_SPLIT=pretest for a fast end-to-end dry run on 20 dialogues.
TRAIN_SPLIT = os.environ.get("TRAIN_SPLIT", "train")
PUBLIC_ALIAS = "test_public"          # the fixed folder name every notebook reads

# Answer files live at the dataset ROOT (outside the split folders), so a split dir
# holds only audio + prefix.json -- the graded ground truth is never inside the tree
# the notebook can see.
HIDDEN_TRAIN_DIR = DATASET_ROOT / TRAIN_SPLIT                # audio + prefix.json
HIDDEN_GRADED_DIR = DATASET_ROOT / GRADE_SPLIT               # audio + prefix.json (no answers)
HIDDEN_TRAIN_ANSWERS = DATASET_ROOT / f"{TRAIN_SPLIT}_answers.json"  # public train ground truth
HIDDEN_ANSWERS = DATASET_ROOT / f"{GRADE_SPLIT}_answers.json"  # hidden graded ground truth {did: rank_list}

REPO_NAME = os.environ.get("REPO_NAME", "submission")
REPO_DIR = (CI_ROOT / REPO_NAME).resolve()                  # RW work volume for the container
NOTEBOOK_PATH = REPO_DIR / "solution.ipynb"
SUBMISSION_PATH = REPO_DIR / "answers.json"                 # written by the notebook, in the RW volume
EXECUTED_IN_REPO = REPO_DIR / "executed.ipynb"             # nbconvert output, in the RW volume

# container-side mount points (what the notebook sees)
C_WORK = "/work"
C_DATASET = f"{C_WORK}/dataset"
C_MODELS = f"{C_WORK}/models"

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
TEST_NAME = "pairwise_accuracy"


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

    A notebook is JSON, so this needs no nbconvert run and no jupyter on the job
    image -- the second conversion would have to happen here, outside the container
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
    """Files published beside the report: the executed notebook and the run log.

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

    `report.result` is a oneOf in Contest's report schema: EITHER `score` (a plain
    number) OR `message` (a STRING holding encoded JSON) -- never both. Sending both
    fails schema validation in `publish`, which fails send_report, which makes
    Contest record a Crash for a submission that graded fine.

    We send `message`. A bare `score` number does publish, but it does not render in
    the Contest interface -- the monitor reads the encoded payload. The key is the
    last character of GRADE_SPLIT, so test_leaderboard_a reports {"a": 80.97} and
    test_leaderboard_b reports {"b": ...}, giving the live and final rounds their own
    monitor columns. Same convention as the other IOAI problems.

    `details` is not published: the schema forbids extra properties, on tests[] as
    well, so anything beyond this goes to the job log only.
    """
    if verdict != "OK":
        # The verdict alone does not say why. Contest's schema has nowhere to carry
        # a message beside a score, so the reason goes into the published log.
        with RUN_LOG.open("a") as fh:
            fh.write(f"grader: {verdict}: {message}\n")
    test = {"testName": TEST_NAME, "testsetName": "tests",
            "verdict": verdict, "score": float(score),
            "runningTime": int(_RUN_MS)}
    encoded_score = json.dumps({GRADE_SPLIT[-1]: float(score)})
    report = {"report": {"result": {"message": encoded_score}, "tests": [test]}}
    artifacts = report_artifacts()
    if artifacts:
        report["artifacts"] = artifacts
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"[{verdict}] score={score} | {message} | {_RUN_MS} ms"
          + (f" | {json.dumps(details)}" if details else ""))


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


# --------------------------------------------------------------------------- #
# metric (self-contained port of metrics/pairwise_accuracy.py)
# --------------------------------------------------------------------------- #
def validate_permutation(perm, n) -> bool:
    """True iff perm is a permutation of 0..n-1 (0-indexed, each exactly once)."""
    if not isinstance(perm, list) or len(perm) != n:
        return False
    seen = [False] * n
    for x in perm:
        if not isinstance(x, int) or isinstance(x, bool):
            return False
        if x < 0 or x >= n or seen[x]:
            return False
        seen[x] = True
    return True


def score_one(pred, target) -> float:
    """Pairwise ordering accuracy for RANK-convention permutations.

    Both `pred` and `target` are rank arrays: value[i] = chronological position
    of chunk i. A pair (i, j) is correct iff pred and target agree on the sign of
    (value[i] - value[j]). Ranks are distinct, so signs are never zero. O(n^2),
    which is trivial for n <= 20 and avoids the order-vs-rank convention trap of a
    generic inversion counter.
    """
    n = len(target)
    if n < 2:
        return 1.0
    if not validate_permutation(pred, n):
        return 0.0
    discordant = 0
    total = n * (n - 1) // 2
    for i in range(n):
        for j in range(i + 1, n):
            if (target[i] > target[j]) != (pred[i] > pred[j]):
                discordant += 1
    return 1.0 - discordant / total


# --------------------------------------------------------------------------- #
# podman sandbox
# --------------------------------------------------------------------------- #
def _volume_args() -> list[str]:
    """Bind mounts that cross the sandbox boundary, matching the statement's layout.

    Dataset + models are read-only; $REPO is read-write (the notebook writes its
    inferred answers.json + executed.ipynb there). The notebook reads exactly what a
    participant sees locally:

      dataset/train/               -> audio + prefix.json ...
      dataset/train/answers.json   -> ... plus the public train ground truth
      dataset/test_public/         -> the hidden eval set: audio + prefix.json, with
                                      answers.json genuinely ABSENT (per the statement)
      models/                      -> offline model bundle

    Because the answer files now live OUTSIDE the split folders, test_public mounts
    as one clean whole-dir volume with no ground truth inside it, and train's public
    answers.json is re-attached with a single nested file mount.
    """
    return [
        # RW: solution.ipynb in, answers.json + executed.ipynb out
        "-v", f"{REPO_DIR}:{C_WORK}",
        # RO: train audio + prefix, with its public answers.json layered back in
        "-v", f"{HIDDEN_TRAIN_DIR}:{C_DATASET}/train:ro",
        "-v", f"{HIDDEN_TRAIN_ANSWERS}:{C_DATASET}/train/answers.json:ro",
        # RO: hidden eval set at the fixed public name (no answers.json in the folder)
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
        "-e", "HF_HUB_OFFLINE=1",
        "-e", "TRANSFORMERS_OFFLINE=1",
        "-e", f"MODELS_DIR={C_MODELS}",
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
    graded split still carries its answers.json INSIDE the split directory. That
    directory is bind-mounted whole into the notebook's container, so ground truth
    sitting in it would be handed straight to the participant's code.
    """
    print("=== dataset preflight ===")
    print(f"  DATASET_ROOT={DATASET_ROOT}  TRAIN_SPLIT={TRAIN_SPLIT}  GRADE_SPLIT={GRADE_SPLIT}")
    problems = []
    for label, path in (("train split", HIDDEN_TRAIN_DIR),
                        ("graded split", HIDDEN_GRADED_DIR),
                        ("models", HIDDEN_MODELS_DIR)):
        if not path.is_dir():
            problems.append(f"{label} directory missing: {path}")
    for label, path in (("train answers", HIDDEN_TRAIN_ANSWERS),
                        ("graded ground truth", HIDDEN_ANSWERS)):
        if not path.is_file():
            problems.append(f"{label} file missing: {path}")
    # The graded split is mounted whole and read-only into the sandbox: nothing that
    # reveals the ordering may live inside it.
    leaked = HIDDEN_GRADED_DIR / "answers.json"
    if leaked.exists():
        problems.append(
            f"ground truth is INSIDE the graded split ({leaked}) -- it would be "
            f"mounted into the participant container. Answers belong at the dataset "
            f"root as {GRADE_SPLIT}_answers.json")
    if problems:
        for p in problems:
            print(f"FATAL: {p}", file=sys.stderr)
        sys.exit(1)
    n_graded = sum(1 for p in HIDDEN_GRADED_DIR.iterdir() if p.is_dir())
    n_truth = len(json.loads(HIDDEN_ANSWERS.read_text()))
    print(f"  ok: {n_graded} dialogue dirs in {GRADE_SPLIT}, {n_truth} ground-truth entries")
    if n_graded != n_truth:
        print(f"FATAL: {GRADE_SPLIT} has {n_graded} dialogues but its ground truth has "
              f"{n_truth} entries", file=sys.stderr)
        sys.exit(1)
    audit_other_rounds()


def audit_other_rounds():
    """Report the state of the rounds we are NOT grading. Informational only.

    Switching GRADE_SPLIT must never be the moment we discover the next split is
    misprovisioned -- by then it is the final ranking and there is no time to
    rebuild the image. Every ordinary submission audits the other rounds for free,
    so the log says whether test_leaderboard_b is ready long before it is needed.

    Non-fatal by design: a round that is simply not baked into the current image
    (pretest, before the next rebuild) must not fail a live submission.
    """
    print("  --- other rounds (informational, not graded now) ---")
    for split in ("pretrain", "pretest", "train", "test_leaderboard_a", "test_leaderboard_b"):
        if split in (GRADE_SPLIT, TRAIN_SPLIT):
            continue
        d, truth = DATASET_ROOT / split, DATASET_ROOT / f"{split}_answers.json"
        if not d.is_dir():
            print(f"    {split}: ABSENT (not baked into this image)")
            continue
        n = sum(1 for p in d.iterdir() if p.is_dir())
        bits = [f"{n} dialogue dirs"]
        bits.append(f"{len(json.loads(truth.read_text()))} ground-truth entries"
                    if truth.is_file() else "ROOT ANSWERS MISSING -- grading this "
                    f"round would Crash (expected {truth.name})")
        if (d / "answers.json").exists():
            bits.append("!! answers.json INSIDE the split -- grading this round would "
                        "expose ground truth to the participant notebook")
        print(f"    {split}: " + "; ".join(bits))


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
    # so that user can write answers.json + executed.ipynb back to /work; otherwise the
    # notebook's final `open("answers.json", "w")` dies with PermissionError (EACCES).
    os.chmod(REPO_DIR, 0o777)

    # nbconvert runs INSIDE the container, in /work (the RW volume). Output paths are
    # relative, so they land back on the host under $REPO.
    inner = (
        "python -m nbconvert --to notebook --execute "
        "--output executed.ipynb "
        "--ExecutePreprocessor.timeout=-1 "          # no per-cell limit; see above
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
        fail(f"answers.json not found at {SUBMISSION_PATH} after notebook executed",
             verdict="PresentationError")
    try:
        preds = json.loads(SUBMISSION_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"answers.json is not valid JSON: {exc}", verdict="PresentationError")
    if not isinstance(preds, dict):
        fail("answers.json must be a JSON object {dialogue_id: permutation}",
             verdict="PresentationError")

    try:
        targets = json.loads(HIDDEN_ANSWERS.read_text())
    except Exception as exc:  # noqa: BLE001 - internal integrity
        print(f"INTERNAL: ground truth unreadable: {exc}", file=sys.stderr)
        sys.exit(1)
    if not targets:
        print("INTERNAL: ground truth is empty", file=sys.stderr)
        sys.exit(1)

    scores = []
    n_valid = 0
    for did, target in targets.items():
        pred = preds.get(did)
        s = score_one(pred, target)
        if pred is not None and validate_permutation(pred, len(target)):
            n_valid += 1
        scores.append(s)

    mean = sum(scores) / len(scores)
    write_report(
        score=round(100.0 * mean, 4),
        verdict="OK",
        message=f"pairwise_accuracy={mean:.4f} over {len(scores)} dialogues "
                f"({n_valid} valid predictions)",
        details={"pairwise_accuracy": round(mean, 6),
                 "dialogues": len(scores),
                 "valid_predictions": n_valid},
    )


def main():
    preflight_dataset()
    preflight_gpu()
    run_notebook()
    score_submission()


if __name__ == "__main__":
    main()
