"""Private CI grader for the Yandex Contest Potato Jupyter problem.

The grader converts the submitted notebook to a Python program, runs that program
ONCE inside a locked-down podman container, and plays every hidden game over the
container's standard input/output.  Hidden words and private embeddings are never
included in the report and never reachable from inside the container.

Isolation model
---------------
The participant program runs in ``RUNTIME_IMAGE`` with:

* ``--network=none``           -- no internet, no runner network;
* read-only mounts only        -- the converted solution, the grader's own copy of
                                  the public data, and the offline model bundle;
* ``--device`` for the GPU     -- when the runner exposes one (see preflight_gpu);
* a pid cap                    -- fork-bomb guard only; no memory ceiling is
                                  imposed, so judging matches the Jupyter
                                  workspace contestants develop in.

The private assets (``private_embeddings.npy``, the secret word lists) are never
mounted, so the container has no path to them at all.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import select
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import numpy as np


# --------------------------------------------------------------------------- #
# Game constants -- these define the published rules and must match statement.md
# --------------------------------------------------------------------------- #

START_WORD_1 = "lamp"
START_WORD_2 = "potato"
MAX_TURNS = 30
FREE_TURNS = 10
PENALTY = 0.02
SAME_EPS = 1e-12
MAX_RESPONSE_BYTES = 4096
# Non-protocol lines on stdout tolerated per response before giving up; see
# read_proposal().
MAX_NOISE_LINES = 200


def _env_float(name: str, default: float) -> float:
    value = float(os.environ.get(name, default))
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return value


def _env_int(name: str, default: int) -> int:
    value = int(os.environ.get(name, default))
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


# --------------------------------------------------------------------------- #
# Limits
# --------------------------------------------------------------------------- #

# Checked BEFORE the notebook is converted or executed -> PresentationError.
MAX_NOTEBOOK_BYTES = _env_int("MAX_NOTEBOOK_BYTES", 1024 * 1024)

# The ONE time limit: start-up, one-time preparation (including loading a model)
# and every game in the round, all together.  There is deliberately no separate
# per-turn or preparation budget -- a submission spends this however it likes.
# Enforced by the grader, OUTSIDE the container.
TIME_LIMIT_SEC = _env_float("TIME_LIMIT_SEC", 600.0)

# nbconvert is a cheap, bounded grader-side step; it is not part of the
# participant's budget.
NOTEBOOK_CONVERT_TIMEOUT_SEC = _env_float("NOTEBOOK_CONVERT_TIMEOUT_SEC", 120.0)


# --------------------------------------------------------------------------- #
# Container configuration
# --------------------------------------------------------------------------- #

PODMAN = os.environ.get("PODMAN", "podman")
RUNTIME_IMAGE = os.environ.get(
    "RUNTIME_IMAGE", "cr.yandex/crpe6hs3eavcafkcisb5/ioai-gitlab:20260725"
)
GPU_DEVICE = os.environ.get("GPU_DEVICE", "nvidia.com/gpu=all")
# No memory cap by default. The judged environment is meant to match the Jupyter
# workspace contestants develop in -- same image, same GPU, same machine -- so an
# invented ceiling here would fail solutions that work in their own notebook.
# Set CONTAINER_MEMORY (e.g. "8g") only if a runner needs protecting.
CONTAINER_MEMORY = os.environ.get("CONTAINER_MEMORY", "")
# Fork-bomb guard only. No legitimate solution comes near this.
CONTAINER_PIDS = _env_int("CONTAINER_PIDS", 256)

# Offline model bundle, baked into the CI job image (see Dockerfile).
MODELS_SRC = Path(os.environ.get("MODELS_SRC", "/problem/models"))

# Paths INSIDE the container. The layout mirrors what a participant has next to
# their notebook -- dataset/ and models/ as siblings of the solution, with the
# working directory set to their parent -- so relative paths like
# "dataset/vocabulary.json" resolve exactly as they do in Jupyter. Mounting the
# data somewhere else would silently break every solution that does not go
# through POTATO_DATA_DIR, which is most of them.
C_WORK = "/work"
C_DATA = "/work/dataset"
C_MODELS = "/work/models"

# Set once the run has started so failure reports can still carry runningTime.
_RUN_MS = 0
_GPU_AVAILABLE: bool | None = None
_NOISE_REPORTED = False
_RUNTIME_PYTHON: str | None = None


class SubmissionError(RuntimeError):
    """A participant program violated the execution or JSON protocol."""

    def __init__(self, verdict: str, message: str):
        super().__init__(message)
        self.verdict = verdict


@dataclass
class GameResult:
    turn: int | None
    verdict: str
    running_time_ms: int

    @property
    def score(self) -> float:
        if self.turn is None:
            return 0.0
        return 1.0 - PENALTY * max(0, self.turn - FREE_TURNS)


def suite_score(results: list[GameResult]) -> float:
    """Return the aggregate score on the contest's 0--100 scale."""

    if not results:
        return 0.0
    return 100.0 * sum(result.score for result in results) / len(results)


class LineReader:
    """Read bounded newline-delimited responses without blocking on partial data."""

    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.buffer = bytearray()

    def readline(self, timeout: float) -> str:
        deadline = time.monotonic() + timeout
        descriptor = self.stream.fileno()

        while True:
            newline = self.buffer.find(b"\n")
            if newline >= 0:
                line = bytes(self.buffer[:newline])
                del self.buffer[: newline + 1]
                try:
                    return line.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise SubmissionError(
                        "PresentationError", "stdout is not valid UTF-8"
                    ) from error

            if len(self.buffer) > MAX_RESPONSE_BYTES:
                raise SubmissionError(
                    "OutputLimitExceeded", "one response line is too long"
                )

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise SubmissionError(
                    "TimeLimitExceeded", "exceeded the total time limit"
                )

            ready, _, _ = select.select([descriptor], [], [], remaining)
            if not ready:
                raise SubmissionError(
                    "TimeLimitExceeded", "exceeded the total time limit"
                )

            chunk = os.read(descriptor, 1024)
            if not chunk:
                raise SubmissionError(
                    "RuntimeError", "solution stopped before returning a response"
                )
            self.buffer.extend(chunk)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--private-data", type=Path, required=True)
    parser.add_argument("--public-data", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("report.json"))
    return parser.parse_args()


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


def mark_run_started() -> float:
    """Start the checking-time clock and return the monotonic origin."""

    return time.monotonic()


def set_elapsed(started: float) -> None:
    """Record checking time so far, so failure reports can still publish it."""

    global _RUN_MS
    _RUN_MS = int((time.monotonic() - started) * 1000)


def write_terminal_report(
    report_path: Path,
    verdict: str,
    message: str = "",
    artifacts: list[dict] | None = None,
) -> None:
    """Publish a rejection in the shape Contest's schema accepts.

    Matches 03_customer_segments: ``result`` carries a JSON-encoded ``message``
    and the real verdict lives on the test row.  Two constraints the schema
    enforces, both of which this used to violate:

    * report-level ``verdict`` accepts only CompilationError /
      PrecompileCheckFailed / Crash, so a PresentationError or TimeLimitExceeded
      belongs on ``tests[]``, not at report level;
    * ``result`` is ``{score}`` XOR ``{message}`` and no other key -- there is no
      ``encoded_json`` property. The encoding goes *inside* ``message``.

    ``tests[]`` rows also reject extra properties, so the human-readable reason is
    printed to the job log rather than attached here.

    ``artifacts`` sits beside ``report``, not inside it, and every entry must name a
    row in ``report.tests`` -- so a Crash, whose test list is empty, can carry none.
    """

    if verdict == "Crash":
        # The only report-level verdict this grader emits, and one of the three
        # the schema allows.
        report = {"report": {"verdict": "Crash", "tests": []}}
    else:
        report = {
            "report": {
                "result": {"message": json.dumps({"score": 0.0})},
                "tests": [
                    {
                        "testName": "potato",
                        "testsetName": "tests",
                        "verdict": verdict,
                        "score": 0.0,
                        "runningTime": _RUN_MS,
                    }
                ],
            }
        }
        if artifacts:
            report["artifacts"] = artifacts
    if message:
        print(f"{verdict}: {message}", file=sys.stderr)
    report_path.write_text(json.dumps(report, indent=2) + "\n")


def tail_file(path: Path, limit: int = 4000) -> str:
    """Return the last ``limit`` characters of a log, for RuntimeError surfacing."""

    try:
        text = path.read_text(errors="replace")
    except OSError:
        return ""
    return text[-limit:]


# --------------------------------------------------------------------------- #
# Submission handling
# --------------------------------------------------------------------------- #


def validate_submission_tree(repository: Path) -> None:
    """Reject links and special files before touching the untrusted checkout."""

    for path in repository.rglob("*"):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise SubmissionError(
                "PresentationError", "symbolic links are not allowed"
            )
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise SubmissionError(
                "PresentationError", "special files are not allowed"
            )


def convert_notebook(
    repository: Path, output_directory: Path, log_path: Path | None = None
) -> Path:
    """Size-check then convert ``solution.ipynb`` to a Python program.

    The size gate runs BEFORE conversion or execution, so an oversized notebook is a
    PresentationError rather than a downstream conversion failure.

    nbconvert's two streams are merged (``2>&1``) so warnings and errors stay in the
    order they were produced, and the result is appended to ``log_path`` -- the same
    file the participant's own stderr goes to, so one artifact carries the whole
    story.  The merge is safe HERE and nowhere else: the participant container's
    stdout is the protocol channel, so merging its streams would break every game.
    """

    notebook = repository / "solution.ipynb"
    if not notebook.is_file():
        raise SubmissionError(
            "PresentationError", "solution.ipynb is missing from the submission"
        )

    size = notebook.stat().st_size
    if size > MAX_NOTEBOOK_BYTES:
        raise SubmissionError(
            "PresentationError",
            f"solution.ipynb is {size} bytes, over the "
            f"{MAX_NOTEBOOK_BYTES}-byte limit",
        )

    jupyter = shutil.which("jupyter")
    if jupyter is None:
        raise RuntimeError("jupyter executable is missing from the grader image")

    output_stem = "solution"
    try:
        completed = subprocess.run(
            [
                jupyter,
                "nbconvert",
                "--to",
                "python",
                str(notebook),
                "--output",
                output_stem,
                "--output-dir",
                str(output_directory),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=NOTEBOOK_CONVERT_TIMEOUT_SEC,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise SubmissionError(
            "PresentationError", "solution.ipynb conversion timed out"
        ) from error

    output = completed.stdout or b""
    if log_path is not None and output.strip():
        with log_path.open("ab") as handle:
            handle.write(b"=== nbconvert ===\n" + output)

    solution = output_directory / f"{output_stem}.py"
    if completed.returncode != 0 or not solution.is_file():
        detail = output.decode(errors="replace").strip()
        raise SubmissionError(
            "PresentationError",
            "solution.ipynb could not be converted to Python"
            + (f": {detail[-500:]}" if detail else ""),
        )
    solution.chmod(0o644)
    return solution


def load_private_space(private_data: Path):
    vocabulary_path = private_data / "vocabulary.json"
    embeddings_path = private_data / "private_embeddings.npy"
    secrets_path = private_data / "secrets.json"

    words = json.loads(vocabulary_path.read_text())
    secrets = json.loads(secrets_path.read_text()) if secrets_path.is_file() else []
    embeddings = np.load(embeddings_path).astype(np.float32, copy=False)

    if len(words) != len({word.casefold() for word in words}):
        raise ValueError("private vocabulary contains duplicates")
    if embeddings.ndim != 2 or embeddings.shape[0] != len(words):
        raise ValueError("private embeddings are not aligned with the vocabulary")
    if not np.isfinite(embeddings).all():
        raise ValueError("private embeddings contain non-finite values")

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("private embeddings contain a zero row")

    normalized = embeddings / norms
    word_to_index = {word.casefold(): index for index, word in enumerate(words)}
    missing = [secret for secret in secrets if secret.casefold() not in word_to_index]
    if missing:
        raise ValueError("a private secret is missing from the vocabulary")
    if START_WORD_1 not in word_to_index or START_WORD_2 not in word_to_index:
        raise ValueError("fixed starting words are missing from the vocabulary")

    return words, secrets, normalized, word_to_index


def preflight_public_data(public_data: Path, words: list[str]) -> None:
    """Verify the grader's OWN copy of the public data before running anything.

    The participant checkout is never used as a data source: a submission must not be
    able to change what the judge serves it.  This also keeps the single-file
    (``$RUN_URL``) submission path working, where no ``data/`` directory is uploaded.
    """

    vocabulary_path = public_data / "vocabulary.json"
    embeddings_path = public_data / "public_embeddings.npy"
    if not vocabulary_path.is_file() or not embeddings_path.is_file():
        raise RuntimeError(
            f"grader public data is incomplete under {public_data} -- expected "
            "vocabulary.json and public_embeddings.npy"
        )

    public_words = json.loads(vocabulary_path.read_text())
    if public_words != words:
        raise RuntimeError(
            "public vocabulary differs from the private vocabulary; the participant "
            "and the judge would disagree on the word set"
        )

    embeddings = np.load(embeddings_path, mmap_mode="r")
    if embeddings.ndim != 2 or embeddings.shape[0] != len(words):
        raise RuntimeError("public embeddings are not aligned with the vocabulary")


def protect_private_files(private_data: Path) -> None:
    """Make private assets unreadable to anything but the grader process.

    The container never mounts ``private_data``, so this is defence in depth against
    a misconfigured runner rather than the primary control.
    """

    if os.name != "posix":
        return
    private_data.chmod(0o700)
    for path in private_data.iterdir():
        if path.is_file():
            path.chmod(0o600)


# --------------------------------------------------------------------------- #
# Container execution
# --------------------------------------------------------------------------- #


def preflight_gpu() -> bool:
    """Report whether the runner can hand a GPU to a container.

    Potato grades correctly on CPU, so an absent GPU degrades speed rather than
    correctness.  The probe result is logged so a silently CPU-only run is visible in
    the job output instead of being mistaken for a GPU run.
    """

    global _GPU_AVAILABLE
    if _GPU_AVAILABLE is not None:
        return _GPU_AVAILABLE
    if not GPU_DEVICE:
        _GPU_AVAILABLE = False
        return False

    try:
        completed = subprocess.run(
            [
                PODMAN,
                "run",
                "--rm",
                "--network=none",
                f"--device={GPU_DEVICE}",
                RUNTIME_IMAGE,
                "true",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"GPU preflight failed to run: {error}", file=sys.stderr)
        _GPU_AVAILABLE = False
        return False

    _GPU_AVAILABLE = completed.returncode == 0
    if not _GPU_AVAILABLE:
        detail = (completed.stderr or b"").decode(errors="replace").strip()
        print(
            f"GPU unavailable, grading on CPU: {detail[-300:]}",
            file=sys.stderr,
        )
    return _GPU_AVAILABLE


def runtime_python() -> str | None:
    """Absolute path to the interpreter inside RUNTIME_IMAGE, resolved once.

    The submission must NOT be launched through a login shell. `bash -lc` sources
    /etc/profile and the user profile first, and anything those print lands on
    stdout -- which is the protocol channel. One banner line and every game in the
    round fails as a PresentationError. So the shell is used only here, to look the
    interpreter up; the submission is then exec'd directly.
    """

    global _RUNTIME_PYTHON
    if _RUNTIME_PYTHON is not None:
        return _RUNTIME_PYTHON or None

    try:
        completed = subprocess.run(
            [
                PODMAN, "run", "--rm", "--network=none", RUNTIME_IMAGE,
                "bash", "-lc", "command -v python3 || command -v python",
            ],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=180, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"interpreter probe failed to run: {error}", file=sys.stderr)
        _RUNTIME_PYTHON = ""
        return None

    # Take the LAST absolute path printed: profile noise may precede it.
    candidates = [
        line.strip()
        for line in (completed.stdout or b"").decode(errors="replace").splitlines()
        if line.strip().startswith("/")
    ]
    _RUNTIME_PYTHON = candidates[-1] if candidates else ""
    if not _RUNTIME_PYTHON:
        print(
            "could not resolve an interpreter in the runtime image; falling back "
            "to a login shell, which risks protocol pollution",
            file=sys.stderr,
        )
        return None
    print(f"runtime interpreter: {_RUNTIME_PYTHON}", file=sys.stderr)
    return _RUNTIME_PYTHON


def _volume_args(solution_directory: Path, public_data: Path) -> list[str]:
    """Read-only mounts only. Private assets are deliberately absent.

    dataset/ and models/ are mounted *inside* the solution directory so the
    container reproduces the participant's own layout. The mount points have to
    exist in the source tree first, because the parent is bind-mounted read-only.
    """

    (solution_directory / "dataset").mkdir(exist_ok=True)
    (solution_directory / "models").mkdir(exist_ok=True)

    mounts = [
        "-v",
        f"{solution_directory}:{C_WORK}:ro",
        "-v",
        f"{public_data}:{C_DATA}:ro",
    ]
    if MODELS_SRC.is_dir():
        mounts += ["-v", f"{MODELS_SRC}:{C_MODELS}:ro"]
    return mounts


def _podman_command(
    container_name: str, solution_directory: Path, public_data: Path
) -> list[str]:
    command = [
        PODMAN,
        "run",
        "--rm",
        "-i",
        "--name",
        container_name,
        "--network=none",
        f"--pids-limit={CONTAINER_PIDS}",
        # The runtime image runs as a non-root user with no writable filesystem;
        # give it a real /tmp so nbconvert-exported code and HF caches can write.
        "--tmpfs",
        "/tmp:rw,exec,mode=1777,size=2g",
        "-w",
        C_WORK,
    ]
    if CONTAINER_MEMORY:
        command += [f"--memory={CONTAINER_MEMORY}"]
    if preflight_gpu():
        command += [f"--device={GPU_DEVICE}"]
    command += _volume_args(solution_directory, public_data)
    command += [
        "-e",
        f"POTATO_DATA_DIR={C_DATA}",
        "-e",
        f"POTATO_MODELS_DIR={C_MODELS}",
        "-e",
        "HF_HUB_OFFLINE=1",
        # Progress bars and telemetry write to the participant's streams and can
        # land on stdout, which is the protocol channel. Silence them at source.
        "-e",
        "HF_HUB_DISABLE_PROGRESS_BARS=1",
        "-e",
        "HF_HUB_DISABLE_TELEMETRY=1",
        "-e",
        "TRANSFORMERS_NO_ADVISORY_WARNINGS=1",
        "-e",
        "TRANSFORMERS_VERBOSITY=error",
        "-e",
        "TQDM_DISABLE=1",
        "-e",
        "TRANSFORMERS_OFFLINE=1",
        "-e",
        "HF_HOME=/tmp/hf",
        "-e",
        "TMPDIR=/tmp",
        "-e",
        "MPLCONFIGDIR=/tmp",
        "-e",
        "PYTHONDONTWRITEBYTECODE=1",
        "-e",
        "PYTHONUNBUFFERED=1",
        RUNTIME_IMAGE,
    ]
    interpreter = runtime_python()
    if interpreter:
        # Exec the interpreter directly: no shell, so nothing but the submission
        # can ever write to the protocol stream.
        command += [interpreter, f"{C_WORK}/solution.py"]
    else:
        command += ["bash", "-lc", f"exec python {C_WORK}/solution.py"]
    return command


def remove_container(container_name: str) -> None:
    subprocess.run(
        [PODMAN, "rm", "-f", container_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def send_message(process: subprocess.Popen, message: dict) -> None:
    if process.stdin is None:
        raise SubmissionError("RuntimeError", "solution stdin is unavailable")
    try:
        process.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        process.stdin.flush()
    except (BrokenPipeError, OSError) as error:
        raise SubmissionError(
            "RuntimeError", "solution stopped before the game ended"
        ) from error


def stop_process(process: subprocess.Popen, container_name: str) -> None:
    if process.stdin is not None and not process.stdin.closed:
        try:
            process.stdin.close()
        except OSError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        # Killing podman's client does not stop the container; remove it explicitly
        # so a hung submission cannot hold the GPU for the next job.
        remove_container(container_name)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def read_proposal(
    reader: LineReader,
    word_to_index: dict[str, int],
    words: list[str],
    timeout: float,
) -> str:
    # The protocol shares stdout with whatever the runtime image prints on
    # start-up -- shell banners, wrapper scripts, progress bars. None of that is
    # the contestant's doing, and failing a round on it means failing everyone.
    # So skip lines that are not JSON at all, log them once so the source can be
    # found and removed, and keep a bound so a submission that never emits a
    # proposal still fails instead of hanging.
    global _NOISE_REPORTED
    response = None
    for _ in range(MAX_NOISE_LINES):
        line = reader.readline(timeout)
        if not line.strip():
            continue
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            if not _NOISE_REPORTED:
                print(
                    "ignoring non-protocol output on stdout: "
                    + repr(line[:200])
                    + " (further noise is not logged)",
                    file=sys.stderr,
                )
                _NOISE_REPORTED = True
            continue
        break
    else:
        raise SubmissionError(
            "PresentationError",
            f"no protocol JSON within {MAX_NOISE_LINES} lines of output",
        )

    if not isinstance(response, dict) or not isinstance(response.get("new_word"), str):
        raise SubmissionError(
            "PresentationError", 'response must contain a string field "new_word"'
        )

    normalized = response["new_word"].casefold()
    if normalized not in word_to_index:
        raise SubmissionError(
            "PresentationError", "proposed word is not in the public vocabulary"
        )
    return words[word_to_index[normalized]]


def play_single_game(
    process: subprocess.Popen,
    reader: LineReader,
    secret: str,
    words: list[str],
    normalized_embeddings: np.ndarray,
    word_to_index: dict[str, int],
    deadline: float,
) -> GameResult:
    """Play ONE game over an already-running participant process.

    The process is started once (and prepares once) by run_suite(); here we only
    exchange protocol messages for a single secret. A ``{"event": "new_game"}``
    message tells the participant to reset its per-game state before the first turn.
    Raises SubmissionError on a protocol/process failure, which run_suite() treats as
    terminal for the whole suite (the one shared stream cannot be trusted after that).

    Every read is bounded by whatever is left of the single time limit, so there is
    no per-turn budget to trip over: a submission may spend its whole allowance on
    one-time preparation, or spread it across turns, as it prefers.
    """
    started = time.monotonic()
    secret_index = word_to_index[secret.casefold()]
    secret_vector = normalized_embeddings[secret_index]

    send_message(process, {"event": "new_game"})

    word1 = START_WORD_1
    word2 = START_WORD_2

    for turn in range(1, MAX_TURNS + 1):
        first_index = word_to_index[word1.casefold()]
        second_index = word_to_index[word2.casefold()]
        first_similarity = float(secret_vector @ normalized_embeddings[first_index])
        second_similarity = float(secret_vector @ normalized_embeddings[second_index])
        difference = first_similarity - second_similarity

        if abs(difference) <= SAME_EPS:
            winner_word, verdict = word1, "same"
        elif difference > 0:
            winner_word, verdict = word1, "first"
        else:
            winner_word, verdict = word2, "second"

        send_message(
            process,
            {
                "turn": turn,
                "winner_word": winner_word,
                "verdict": verdict,
                "word1": word1,
                "word2": word2,
            },
        )
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SubmissionError("TimeLimitExceeded", "exceeded the total time limit")

        proposal = read_proposal(reader, word_to_index, words, remaining)

        if proposal.casefold() == secret.casefold():
            send_message(process, {"status": "win"})
            return GameResult(turn, "OK", int((time.monotonic() - started) * 1000))

        word1 = winner_word
        word2 = proposal

    send_message(process, {"status": "loss"})
    return GameResult(None, "OK", int((time.monotonic() - started) * 1000))


def run_suite(
    solution: Path,
    public_data: Path,
    secrets: list[str],
    words: list[str],
    normalized_embeddings: np.ndarray,
    word_to_index: dict[str, int],
    stderr_path: Path,
) -> list[GameResult]:
    """Start the participant program ONCE inside a container, then play EVERY game.

    The submission prepares once -- loading a model or precomputing embeddings -- and
    reuses that across all games in the split.  Preparation is not budgeted
    separately: it simply consumes part of the single time limit.

    A protocol/process failure is terminal: the shared stdin/stdout stream cannot be
    trusted afterwards, so the failing game AND all remaining games get that verdict
    (score 0) and the suite stops.
    """
    container_name = f"potato-{uuid.uuid4().hex[:12]}"
    command = _podman_command(container_name, solution.parent, public_data)

    started_suite = time.monotonic()
    with stderr_path.open("ab") as stderr_file:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr_file,
        )

        try:
            if process.stdout is None:
                return [GameResult(None, "RuntimeError", 0) for _ in secrets]
            reader = LineReader(process.stdout)

            deadline = started_suite + TIME_LIMIT_SEC
            results: list[GameResult] = []
            for index, secret in enumerate(secrets):
                if time.monotonic() >= deadline:
                    left = len(secrets) - index
                    results.extend(
                        GameResult(None, "TimeLimitExceeded", 0) for _ in range(left)
                    )
                    return results
                game_started = time.monotonic()
                try:
                    results.append(
                        play_single_game(
                            process,
                            reader,
                            secret,
                            words,
                            normalized_embeddings,
                            word_to_index,
                            deadline,
                        )
                    )
                except SubmissionError as error:
                    # Say WHY, in the job log. A mid-round failure is reported to
                    # Contest as a verdict plus score 0, and the schema has nowhere
                    # to carry a message alongside a score -- so without this line
                    # a polluted stdout and a broken solution look identical.
                    reason = (
                        f"round failed at game {index + 1}/{len(secrets)}: "
                        f"{error.verdict}: {error}"
                    )
                    print(reason, file=sys.stderr)
                    # Also into the participant's log, which is the only one they
                    # see: a verdict alone does not say WHICH game broke or why.
                    stderr_file.write(f"grader: {reason}\n".encode())
                    stderr_file.flush()
                    # Keep the time the failing game actually consumed -- start-up
                    # and a blown per-turn budget both land here, and reporting them
                    # as 0 ms would understate checking time for every rejected
                    # submission. Games never reached stay at 0.
                    spent = int((time.monotonic() - game_started) * 1000)
                    results.append(GameResult(None, error.verdict, spent))
                    left = len(secrets) - index - 1
                    results.extend(
                        GameResult(None, error.verdict, 0) for _ in range(left)
                    )
                    return results

            # Every game finished -> tell the participant to exit its loop cleanly.
            try:
                send_message(process, {"event": "done"})
            except SubmissionError:
                pass
            return results
        finally:
            stop_process(process, container_name)
            remove_container(container_name)


def build_report(results: list[GameResult]) -> dict:
    total_score = round(suite_score(results), 2)
    verdict = next(
        (result.verdict for result in results if result.verdict != "OK"), "OK"
    )
    return {
        "report": {
            "result": {"score": total_score},
            # Only the aggregate is published. Per-secret scores would allow
            # participants to probe the fixed hidden set across submissions.
            "tests": [
                {
                    "testName": "private-suite",
                    "testsetName": "tests",
                    "verdict": verdict,
                    "score": total_score,
                    "runningTime": sum(
                        result.running_time_ms for result in results
                    ),
                }
            ],
        }
    }


def main() -> int:
    args = parse_args()
    started = mark_run_started()
    repository = args.repository.resolve()
    private_data = args.private_data.resolve()
    public_data = args.public_data.resolve()
    report_path = args.report.resolve()

    try:
        if not repository.is_dir():
            raise SubmissionError(
                "PresentationError", "participant repository is missing"
            )
        validate_submission_tree(repository)
        protect_private_files(private_data)
        words, secrets, embeddings, word_to_index = load_private_space(private_data)
        preflight_public_data(public_data, words)

        with tempfile.TemporaryDirectory(prefix="potato-solution-") as directory:
            solution_directory = Path(directory)
            solution = convert_notebook(repository, solution_directory)
            solution_directory.chmod(0o755)
            stderr_path = Path("solution_stderr.log").resolve()

            results = run_suite(
                solution,
                public_data,
                secrets,
                words,
                embeddings,
                word_to_index,
                stderr_path,
            )
        set_elapsed(started)
        report_path.write_text(json.dumps(build_report(results), indent=2) + "\n")

        wins = sum(result.turn is not None for result in results)
        score = suite_score(results)
        print(
            f"Grading complete: {wins}/{len(results)} wins, "
            f"score {score:.2f}/100"
        )
        return 0
    except SubmissionError as error:
        set_elapsed(started)
        write_terminal_report(report_path, error.verdict, str(error))
        print(f"Submission rejected: {error}", file=sys.stderr)
        return 0
    except Exception as error:
        set_elapsed(started)
        write_terminal_report(report_path, "Crash")
        print(f"Internal grader error: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
