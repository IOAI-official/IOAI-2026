"""Yandex Contest grader for IOAI Field.

The submission is executed twice in isolated podman workspaces. Its optional
``custom_model.py`` module is copied beside the notebook in each one:

1. A diagnostic prerun uses ``data/train_config``. The notebook and its saved
   model must execute and score successfully. Participant-caused failures are
   published with a bounded, sanitized traceback and hidden testing stops.
2. A fresh copy of the original notebook uses ``data/<GRADE_SPLIT>``. Only this
   second model is scored and published as the contest result.

Both containers run without network access and receive the field runtime and
selected configuration as read-only mounts.
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

NOTEBOOK_TIMEOUT_SEC = int(os.environ.get("NOTEBOOK_TIMEOUT_SEC", "2400"))
WALL_CLOCK_BUDGET_SEC = int(os.environ.get("WALL_CLOCK_BUDGET_SEC", "1800"))
PRERUN_NOTEBOOK_TIMEOUT_SEC = int(
    os.environ.get("PRERUN_NOTEBOOK_TIMEOUT_SEC", str(NOTEBOOK_TIMEOUT_SEC))
)
PRERUN_WALL_CLOCK_BUDGET_SEC = int(
    os.environ.get("PRERUN_WALL_CLOCK_BUDGET_SEC", str(WALL_CLOCK_BUDGET_SEC))
)
SCORE_BUDGET_SEC = int(os.environ.get("SCORE_BUDGET_SEC", "600"))
MAX_NOTEBOOK_BYTES = int(os.environ.get("MAX_NOTEBOOK_BYTES", "1048576"))
MAX_CUSTOM_MODEL_BYTES = int(os.environ.get("MAX_CUSTOM_MODEL_BYTES", "1048576"))
MAX_REPORT_MESSAGE_CHARS = int(os.environ.get("MAX_REPORT_MESSAGE_CHARS", "16384"))
LOG_TAIL_BYTES = 65536

# Podman sandbox knobs.
RUNTIME_IMAGE = os.environ.get(
    "RUNTIME_IMAGE", "cr.yandex/crpe6hs3eavcafkcisb5/ioai-gitlab:20260805"
)
GPU_DEVICE = os.environ.get("GPU_DEVICE", "nvidia.com/gpu=all")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "solution-run")
PODMAN = os.environ.get("PODMAN", "podman")

CI_ROOT = Path(__file__).resolve().parent
DATASET_ROOT = Path(os.environ.get("DATASET_ROOT", CI_ROOT / "data")).resolve()

PRERUN_SPLIT = os.environ.get("PRERUN_SPLIT", "train_config")
GRADE_SPLIT = os.environ.get("GRADE_SPLIT", "leaderboard_a_config")
CALCULATOR_KEYS = {
    "leaderboard_a_config": "a",
    "leaderboard_b_config": "b",
}
TRAIN_ALIAS = "train_config"
PRERUN_CONFIG_DIR = (DATASET_ROOT / PRERUN_SPLIT).resolve()
HIDDEN_SPLIT_DIR = (DATASET_ROOT / GRADE_SPLIT).resolve()

RUNTIME_ITEMS = ["core", "problem.py", "metrics", "_dist-linux-py313"]
SCORE_SCRIPT = CI_ROOT / "score_model.py"

REPO_NAME = os.environ.get("REPO_NAME", "submission")
REPO_DIR = (CI_ROOT / REPO_NAME).resolve()
SOURCE_NOTEBOOK = REPO_DIR / "solution.ipynb"
CUSTOM_MODEL_NAME = "custom_model.py"
SOURCE_CUSTOM_MODEL = REPO_DIR / CUSTOM_MODEL_NAME

C_WORK = "/work"

REPORT_PATH = Path("report.json")
ERROR_TRACE_PATH = Path("artifacts/field_score-error.txt")
PRERUN_EXECUTED_NB = Path("prerun_executed.ipynb")
PRERUN_STDOUT_LOG = Path("prerun_stdout.log")
PRERUN_STDERR_LOG = Path("prerun_stderr.log")
EXECUTED_NB = Path("executed.ipynb")
STDOUT_LOG = Path("executed_stdout.log")
STDERR_LOG = Path("executed_stderr.log")
TEST_NAME = "field_score"

_ANSI_ESCAPE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
_RUN_MS = None


# --------------------------------------------------------------------------- #
# Report and diagnostic helpers
# --------------------------------------------------------------------------- #
def sanitize_feedback(text: str) -> str:
    """Remove terminal noise and grader paths, then bound student feedback."""
    text = _ANSI_ESCAPE.sub("", text).replace("\x00", "")
    text = text.replace(str(CI_ROOT), "<grader>").replace(C_WORK, "<submission>")
    text = text.strip()
    if len(text) > MAX_REPORT_MESSAGE_CHARS:
        text = "...[traceback truncated]...\n" + text[-MAX_REPORT_MESSAGE_CHARS:]
    return text


def calculator_result(score) -> tuple[float, dict[str, str]]:
    """Build the Yandex CALCULATOR result for the active leaderboard split."""
    numeric_score = float(score)
    if not math.isfinite(numeric_score):
        raise ValueError(f"score must be finite, got {numeric_score!r}")
    try:
        calculator_key = CALCULATOR_KEYS[GRADE_SPLIT]
    except KeyError as exc:
        raise ValueError(
            f"GRADE_SPLIT={GRADE_SPLIT!r} has no CALCULATOR component key"
        ) from exc
    encoded_score = json.dumps(
        {calculator_key: numeric_score},
        allow_nan=False,
    )
    return numeric_score, {"message": encoded_score}


def write_report(*, score, verdict, message):
    """Write report.json.

    `report.result` is a oneOf in Contest's report schema: EITHER `score` (a plain
    number) OR `message` (a STRING holding encoded JSON) -- never both. A bare
    `score` publishes but does not render in the Contest interface; the monitor
    reads the encoded payload. The active split is explicitly mapped to its
    one-letter monitor key, so leaderboard_a_config reports {"a": 41.7} and
    leaderboard_b_config reports {"b": ...}, giving the live and final rounds
    their own monitor columns. Same convention as the other IOAI problems.
    """
    message = sanitize_feedback(str(message))
    numeric_score, result = calculator_result(score)
    test = {
        "testName": TEST_NAME,
        "testsetName": "tests",
        "verdict": verdict,
        "score": numeric_score,
    }
    if _RUN_MS is not None:
        test["runningTime"] = int(_RUN_MS)
    report = {"report": {"result": result, "tests": [test]}}

    if verdict != "OK" and message:
        ERROR_TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        ERROR_TRACE_PATH.write_text(message + "\n")
        report["artifacts"] = [
            {
                "testName": TEST_NAME,
                "testDataType": "ERROR",
                "path": ERROR_TRACE_PATH.as_posix(),
            }
        ]

    REPORT_PATH.write_text(json.dumps(report, indent=2, allow_nan=False))
    print(
        f"[{verdict}] score={score} | {message}"
        + (f" | {_RUN_MS} ms" if _RUN_MS is not None else "")
    )


def fail(message, verdict):
    write_report(score=0.0, verdict=verdict, message=message)
    # Participant failures are a successful grader run: send_report publishes
    # the structured verdict instead of send_crash replacing it with Crash.
    sys.exit(0)


def tail_file(path, nbytes=LOG_TAIL_BYTES):
    if not path.exists():
        return ""
    size = path.stat().st_size
    with path.open("rb") as fh:
        if size > nbytes:
            fh.seek(size - nbytes)
        return fh.read().decode(errors="replace")


def traceback_from_log(path: Path) -> str:
    """Return the useful tail of an nbconvert/scorer error log."""
    text = tail_file(path)
    for marker in (
        "An error occurred while executing the following cell:",
        "Traceback (most recent call last):",
    ):
        start = text.rfind(marker)
        if start >= 0:
            text = text[start:]
            break
    return sanitize_feedback(text) or "No traceback was produced."


def validate_submission() -> None:
    if not SOURCE_NOTEBOOK.exists():
        fail(
            f"solution.ipynb not found at {SOURCE_NOTEBOOK}",
            verdict="PresentationError",
        )
    nb_size = SOURCE_NOTEBOOK.stat().st_size
    if nb_size > MAX_NOTEBOOK_BYTES:
        fail(
            f"solution.ipynb is {nb_size / 1e6:.2f} MB, over the "
            f"{MAX_NOTEBOOK_BYTES / 1e6:.2f} MB limit "
            "(submit code only -- do not embed data, weights or outputs)",
            verdict="PresentationError",
        )
    _validate_custom_model()


def _validate_custom_model(source: Path | None = None) -> None:
    """Allow one small model module whose only imports come from torch."""
    source = SOURCE_CUSTOM_MODEL if source is None else source
    if not source.exists():
        return
    if source.is_symlink() or not source.is_file():
        fail(
            f"{CUSTOM_MODEL_NAME} must be a regular file",
            verdict="PresentationError",
        )
    size = source.stat().st_size
    if size > MAX_CUSTOM_MODEL_BYTES:
        fail(
            f"{CUSTOM_MODEL_NAME} is {size} bytes, over the "
            f"{MAX_CUSTOM_MODEL_BYTES}-byte limit",
            verdict="PresentationError",
        )

    try:
        source_text = source.read_text(encoding="utf-8")
        tree = ast.parse(source_text, filename=CUSTOM_MODEL_NAME)
    except (UnicodeDecodeError, SyntaxError) as exc:
        fail(
            f"{CUSTOM_MODEL_NAME} is not valid UTF-8 Python: {exc}",
            verdict="PresentationError",
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            valid = all(
                alias.name == "torch" or alias.name.startswith("torch.")
                for alias in node.names
            )
            if not valid:
                fail(
                    f"{CUSTOM_MODEL_NAME} may import only torch modules "
                    f"(line {node.lineno})",
                    verdict="PresentationError",
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            valid = (
                node.level == 0
                and (module == "torch" or module.startswith("torch."))
            )
            if not valid:
                fail(
                    f"{CUSTOM_MODEL_NAME} may import only torch modules "
                    f"(line {node.lineno})",
                    verdict="PresentationError",
                )

    class_count = 0
    for index, node in enumerate(tree.body):
        if (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
        ):
            if isinstance(node.value.value, str):
                continue  # module docstring
        if isinstance(node, ast.Import):
            continue
        if isinstance(node, ast.ImportFrom):
            continue
        if isinstance(node, ast.ClassDef):
            class_count += 1
            continue
        fail(
            f"{CUSTOM_MODEL_NAME} may contain only torch imports and model class "
            f"definitions; unsupported top-level {type(node).__name__} at line "
            f"{getattr(node, 'lineno', '?')}",
            verdict="PresentationError",
        )
    if class_count == 0:
        fail(
            f"{CUSTOM_MODEL_NAME} must define at least one model class",
            verdict="PresentationError",
        )


def _validate_grader_inputs() -> None:
    for item in RUNTIME_ITEMS:
        path = CI_ROOT / item
        if not path.exists():
            print(f"INTERNAL: runtime item missing: {path}", file=sys.stderr)
            sys.exit(1)
    if not SCORE_SCRIPT.exists():
        print(f"INTERNAL: scorer missing: {SCORE_SCRIPT}", file=sys.stderr)
        sys.exit(1)
    for label, config_dir in (
        ("prerun", PRERUN_CONFIG_DIR),
        ("hidden", HIDDEN_SPLIT_DIR),
    ):
        if not config_dir.exists():
            print(
                f"INTERNAL: {label} config missing at {config_dir}",
                file=sys.stderr,
            )
            sys.exit(1)
        single = config_dir / "field_config.json"
        multi = config_dir / "field_configs.json"
        if not single.exists() and not multi.exists():
            print(
                f"INTERNAL: {label} config has neither {single.name} nor {multi.name}",
                file=sys.stderr,
            )
            sys.exit(1)


# --------------------------------------------------------------------------- #
# Podman sandbox
# --------------------------------------------------------------------------- #
def _volume_args(work_dir: Path, config_dir: Path) -> list[str]:
    """Mount a disposable workspace RW and runtime/configuration inputs RO."""
    mounts = ["-v", f"{work_dir.resolve()}:{C_WORK}"]
    for item in RUNTIME_ITEMS:
        src = CI_ROOT / item
        mounts += ["-v", f"{src}:{C_WORK}/{item}:ro"]
    mounts += ["-v", f"{config_dir.resolve()}:{C_WORK}/data/{TRAIN_ALIAS}:ro"]
    return mounts


def _podman_cmd(
    inner: str,
    *,
    name: str,
    work_dir: Path,
    config_dir: Path,
    extra_volumes=(),
) -> list[str]:
    return [
        PODMAN,
        "run",
        "--rm",
        "--name",
        name,
        "--network=none",
        "--device",
        GPU_DEVICE,
        "--tmpfs",
        "/tmp:rw,exec,mode=1777,size=4g",
        *_volume_args(work_dir, config_dir),
        *extra_volumes,
        "-w",
        C_WORK,
        "-e",
        "MPLBACKEND=Agg",
        "-e",
        "TMPDIR=/tmp",
        "-e",
        "MPLCONFIGDIR=/tmp",
        RUNTIME_IMAGE,
        "bash",
        "-lc",
        inner,
    ]


def preflight() -> None:
    """Require CUDA and CPython 3.13 before either notebook run."""
    check = (
        "import sys, torch; v = sys.version_info[:2]; "
        "ok = torch.cuda.is_available(); "
        "print('python', '.'.join(map(str, v)), '| torch', "
        "torch.__version__, '| cuda', ok); "
        "sys.exit(0 if (ok and v == (3, 13)) else 1)"
    )
    cmd = [
        PODMAN,
        "run",
        "--rm",
        "--network=none",
        "--device",
        GPU_DEVICE,
        RUNTIME_IMAGE,
        "bash",
        "-lc",
        "python -c " + shlex.quote(check),
    ]
    print("=== preflight (GPU + CPython 3.13) ===")
    if subprocess.run(cmd).returncode != 0:
        print(
            "FATAL: sandbox lacks a CUDA GPU or is not CPython 3.13 "
            "(field runtime needs _dist-linux-py313)",
            file=sys.stderr,
        )
        sys.exit(1)


def _phase_label(phase: str) -> str:
    return "training prerun" if phase == "prerun" else "hidden test"


def _gating_note(phase: str) -> str:
    return " Hidden testing was not started." if phase == "prerun" else ""


def run_notebook(
    *,
    work_dir: Path,
    config_dir: Path,
    phase: str,
    stdout_log: Path,
    stderr_log: Path,
    executed_notebook: Path,
    wall_clock_budget: int,
    notebook_timeout: int,
) -> None:
    """Execute one clean notebook copy for either prerun or hidden testing."""
    notebook_path = work_dir / "solution.ipynb"
    executed_in_work = work_dir / "executed.ipynb"
    label = _phase_label(phase)

    subprocess.run(["chmod", "-R", "0777", str(work_dir)], check=False)

    inner = (
        "python -m nbconvert --to notebook --execute "
        "--output executed.ipynb "
        f"--ExecutePreprocessor.timeout={notebook_timeout} "
        "--ExecutePreprocessor.kernel_name=python3 "
        "solution.ipynb"
    )
    cmd = _podman_cmd(
        inner,
        name=f"{CONTAINER_NAME}-{phase}",
        work_dir=work_dir,
        config_dir=config_dir,
    )
    print(f"=== {label}: notebook ===")
    print("running:", " ".join(cmd))

    global _RUN_MS
    t0 = time.perf_counter()
    with stdout_log.open("wb") as out, stderr_log.open("wb") as err:
        try:
            proc = subprocess.run(
                cmd,
                stdout=out,
                stderr=err,
                timeout=wall_clock_budget,
            )
        except subprocess.TimeoutExpired:
            subprocess.run(
                [PODMAN, "rm", "-f", f"{CONTAINER_NAME}-{phase}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _RUN_MS = int((time.perf_counter() - t0) * 1000)
            fail(
                f"{label} exceeded its wall-clock budget of "
                f"{wall_clock_budget}s.{_gating_note(phase)}",
                verdict="TimeLimitExceeded",
            )
    _RUN_MS = int((time.perf_counter() - t0) * 1000)

    if executed_in_work.exists():
        shutil.copy2(executed_in_work, executed_notebook)
    print(f"--- {label} nbconvert stdout (tail) ---")
    print(tail_file(stdout_log))
    print(f"--- {label} nbconvert stderr (tail) ---")
    print(tail_file(stderr_log))

    if proc.returncode != 0:
        trace = traceback_from_log(stderr_log)
        fail(
            f"{label} failed to execute (exit {proc.returncode})."
            f"{_gating_note(phase)}\n\n{trace}",
            verdict="RuntimeError",
        )

    if not notebook_path.exists():
        # A notebook may delete itself, but that must not affect the pristine copy
        # used to prepare the next phase.
        print(f"WARN: {label} deleted its disposable solution.ipynb")


def score_submission(
    *,
    work_dir: Path,
    config_dir: Path,
    phase: str,
    split_name: str,
    publish_score: bool,
) -> float:
    """Validate/score a model; publish only the hidden phase's score."""
    label = _phase_label(phase)
    # Revalidate the copy used for unpickling. This also covers file-only
    # submissions that generate custom_model.py inside the notebook.
    _validate_custom_model(work_dir / CUSTOM_MODEL_NAME)
    model_path = work_dir / "model.pt"
    if not model_path.exists():
        fail(
            f"{label} did not produce model.pt "
            "(the notebook must torch.save(model, 'model.pt'))."
            f"{_gating_note(phase)}",
            verdict="PresentationError",
        )

    container_name = f"{CONTAINER_NAME}-{phase}-score"
    cmd = _podman_cmd(
        "python /grader/score_model.py",
        name=container_name,
        work_dir=work_dir,
        config_dir=config_dir,
        extra_volumes=["-v", f"{SCORE_SCRIPT}:/grader/score_model.py:ro"],
    )
    print(f"=== {label}: model validation/scoring ===")
    print("scoring:", " ".join(cmd))
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SCORE_BUDGET_SEC,
        )
    except subprocess.TimeoutExpired:
        subprocess.run(
            [PODMAN, "rm", "-f", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        fail(
            f"{label} model validation/scoring exceeded "
            f"{SCORE_BUDGET_SEC}s.{_gating_note(phase)}",
            verdict="RuntimeError",
        )

    print(f"--- {label} scorer stdout (tail) ---")
    print("\n".join(proc.stdout.splitlines()[-40:]))
    print(f"--- {label} scorer stderr (tail) ---")
    print("\n".join(proc.stderr.splitlines()[-20:]))

    sentinel = next(
        (
            line.strip()
            for line in reversed(proc.stdout.splitlines())
            if line.strip().startswith("GRADER_")
        ),
        "",
    )
    if sentinel.startswith("GRADER_SCORE="):
        score = float(sentinel.split("=", 1)[1])
        if publish_score:
            write_report(
                score=round(score, 12),
                verdict="OK",
                message=f"field_score={score:.4f} on {split_name}",
            )
        else:
            print(f"training prerun passed (diagnostic score={score:.4f})")
        return score

    suffix = _gating_note(phase)
    if sentinel == "GRADER_NO_MODEL":
        fail(
            f"{label}: model.pt was not found by the scorer.{suffix}",
            "PresentationError",
        )
    if sentinel.startswith("GRADER_BAD_MODEL:"):
        detail = sentinel.split(":", 1)[1].strip()
        fail(
            f"{label}: could not load model.pt: {detail}.{suffix}",
            "PresentationError",
        )
    if sentinel.startswith("GRADER_COUNT_MISMATCH:"):
        detail = sentinel.split(":", 1)[1].strip()
        fail(
            f"{label}: model.pt has a different number of models than configs "
            f"({detail}).{suffix}",
            "PresentationError",
        )
    if sentinel.startswith("GRADER_SCORING_ERROR:"):
        detail = sentinel.split(":", 1)[1].strip()
        trace = sanitize_feedback(proc.stderr)
        trace_note = f"\n\n{trace}" if trace else ""
        fail(
            f"{label} scoring failed: {detail}.{suffix}{trace_note}",
            "RuntimeError",
        )

    print(
        f"INTERNAL: {label} scorer produced no valid result "
        f"(rc={proc.returncode}, sentinel={sentinel!r})",
        file=sys.stderr,
    )
    sys.exit(1)


def _prepare_workspace(temp_path: str) -> Path:
    work_dir = Path(temp_path).resolve()
    shutil.copy2(SOURCE_NOTEBOOK, work_dir / "solution.ipynb")
    if SOURCE_CUSTOM_MODEL.exists():
        shutil.copy2(SOURCE_CUSTOM_MODEL, work_dir / CUSTOM_MODEL_NAME)
    return work_dir


def main() -> None:
    validate_submission()
    _validate_grader_inputs()
    preflight()

    # Phase 1: public diagnostic run. Nothing from this workspace survives into
    # hidden testing, including model.pt, generated modules, or modified notebooks.
    with tempfile.TemporaryDirectory(prefix=".grader-prerun-", dir=CI_ROOT) as temp_path:
        work_dir = _prepare_workspace(temp_path)
        run_notebook(
            work_dir=work_dir,
            config_dir=PRERUN_CONFIG_DIR,
            phase="prerun",
            stdout_log=PRERUN_STDOUT_LOG,
            stderr_log=PRERUN_STDERR_LOG,
            executed_notebook=PRERUN_EXECUTED_NB,
            wall_clock_budget=PRERUN_WALL_CLOCK_BUDGET_SEC,
            notebook_timeout=PRERUN_NOTEBOOK_TIMEOUT_SEC,
        )
        score_submission(
            work_dir=work_dir,
            config_dir=PRERUN_CONFIG_DIR,
            phase="prerun",
            split_name=PRERUN_SPLIT,
            publish_score=False,
        )

    # Phase 2: start from the pristine submission and mount the hidden split only
    # after the complete diagnostic path succeeds.
    with tempfile.TemporaryDirectory(prefix=".grader-test-", dir=CI_ROOT) as temp_path:
        work_dir = _prepare_workspace(temp_path)
        run_notebook(
            work_dir=work_dir,
            config_dir=HIDDEN_SPLIT_DIR,
            phase="test",
            stdout_log=STDOUT_LOG,
            stderr_log=STDERR_LOG,
            executed_notebook=EXECUTED_NB,
            wall_clock_budget=WALL_CLOCK_BUDGET_SEC,
            notebook_timeout=NOTEBOOK_TIMEOUT_SEC,
        )
        score_submission(
            work_dir=work_dir,
            config_dir=HIDDEN_SPLIT_DIR,
            phase="test",
            split_name=GRADE_SPLIT,
            publish_score=True,
        )


if __name__ == "__main__":
    main()
