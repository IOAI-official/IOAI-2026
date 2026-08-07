"""Run a Potato Contact submission against an approximate public judge.

This utility intentionally uses only the vocabulary, public embeddings, and
120-word public test list provided to participants. It runs one solution
process for the complete suite, like the official grader. Its results are
useful for debugging the protocol and trying ideas, but they are not the
official private score.
"""

from __future__ import annotations

import argparse
import json
import os
import select
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import BinaryIO

import numpy as np


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dataset"
WORDS_PATH = DATA_DIR / "vocabulary.json"
EMBEDDINGS_PATH = DATA_DIR / "public_embeddings.npy"
TEST_PUBLIC_PATH = DATA_DIR / "test_public.json"

START_WORD_1 = "lamp"
START_WORD_2 = "potato"
MAX_TURNS = 30
FREE_TURNS = 10
PENALTY = 0.02
SAME_EPS = 1e-12
MAX_RESPONSE_BYTES = 4096
# The single official budget: start-up, preparation and every game together.
# There is no separate per-turn limit, matching the official judge.
TIME_LIMIT_SEC = 600.0


class ProtocolError(RuntimeError):
    """The submitted program did not follow the JSON protocol."""


class LineReader:
    """Read bounded newline-delimited responses without hanging on partial data."""

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
                    raise ProtocolError("Standard output is not valid UTF-8") from error

            if len(self.buffer) > MAX_RESPONSE_BYTES:
                raise ProtocolError("One response line is too long")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProtocolError("The solution response timed out")

            ready, _, _ = select.select([descriptor], [], [], remaining)
            if not ready:
                raise ProtocolError("The solution response timed out")

            chunk = os.read(descriptor, 1024)
            if not chunk:
                raise ProtocolError("The solution stopped before returning a response")
            self.buffer.extend(chunk)


with WORDS_PATH.open() as file:
    words = json.load(file)

embeddings = np.load(EMBEDDINGS_PATH).astype(np.float32, copy=False)
if embeddings.ndim != 2 or embeddings.shape[0] != len(words):
    raise ValueError("Public embeddings are not aligned with the vocabulary")

norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
if np.any(norms == 0):
    raise ValueError("Public embeddings contain a zero vector")

normalized = embeddings / norms
word_to_index = {word.casefold(): index for index, word in enumerate(words)}

with TEST_PUBLIC_PATH.open() as file:
    test_public_secrets = json.load(file)

if not isinstance(test_public_secrets, list) or not all(
    isinstance(secret, str) and secret for secret in test_public_secrets
):
    raise ValueError("test_public.json must be a JSON list of non-empty words")
if len(test_public_secrets) != 120:
    raise ValueError("test_public.json must contain exactly 120 words")
if len({secret.casefold() for secret in test_public_secrets}) != len(
    test_public_secrets
):
    raise ValueError("test_public.json contains duplicate words")
unknown_public = [
    secret for secret in test_public_secrets if secret.casefold() not in word_to_index
]
if unknown_public:
    raise ValueError(
        "test_public.json contains words outside vocabulary.json: "
        + ", ".join(unknown_public)
    )
test_public_secrets = [
    words[word_to_index[secret.casefold()]] for secret in test_public_secrets
]


def score_for_turn(turn: int) -> float:
    return 1.0 - PENALTY * max(0, turn - FREE_TURNS)


def normalized_score(total_score: float, game_count: int) -> float:
    """Convert a sum of per-game scores to the contest's 0--100 scale."""

    if game_count <= 0:
        return 0.0
    return 100.0 * total_score / game_count


def public_oracle(secret: str, word1: str, word2: str) -> tuple[str, str]:
    secret_vector = normalized[word_to_index[secret.casefold()]]
    first_similarity = float(
        secret_vector @ normalized[word_to_index[word1.casefold()]]
    )
    second_similarity = float(
        secret_vector @ normalized[word_to_index[word2.casefold()]]
    )
    difference = first_similarity - second_similarity

    if abs(difference) <= SAME_EPS:
        return word1, "same"
    if difference > 0:
        return word1, "first"
    return word2, "second"


def send_message(process: subprocess.Popen, message: dict) -> None:
    if process.stdin is None:
        raise ProtocolError("The solution's standard input is unavailable")
    try:
        process.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        process.stdin.flush()
    except (BrokenPipeError, OSError) as error:
        raise ProtocolError("The solution stopped before the game ended") from error


def read_proposal(reader: LineReader, timeout: float) -> str:
    line = reader.readline(timeout)
    try:
        response = json.loads(line)
    except json.JSONDecodeError as error:
        raise ProtocolError(
            f"Expected one JSON object on stdout, received: {line.rstrip()!r}"
        ) from error

    if not isinstance(response, dict) or not isinstance(response.get("new_word"), str):
        raise ProtocolError('The response must look like {"new_word": "example"}')

    proposal = response["new_word"].casefold()
    if proposal not in word_to_index:
        raise ProtocolError(f"Word {response['new_word']!r} is not in vocabulary.json")
    return words[word_to_index[proposal]]


def stop_process(process: subprocess.Popen) -> None:
    if process.stdin is not None and not process.stdin.closed:
        process.stdin.close()
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            process.terminate()
        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            process.wait()


def notebook_to_script(notebook_path: Path, output_directory: Path) -> Path:
    """Convert a notebook to a runnable script, the way the official judge does.

    The judge runs `jupyter nbconvert --to python` and executes the result, so we
    use the same tool when it is available. The fallback simply concatenates the
    code cells, which matches nbconvert for ordinary notebooks but cannot rewrite
    IPython magics -- those are reported rather than silently dropped.
    """

    target = output_directory / "solution.py"
    try:
        completed = subprocess.run(
            [
                sys.executable, "-m", "jupyter", "nbconvert", "--to", "python",
                str(notebook_path), "--output", "solution",
                "--output-dir", str(output_directory),
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120, check=False,
        )
        if completed.returncode == 0 and target.is_file():
            return target
    except (OSError, subprocess.TimeoutExpired):
        pass

    notebook = json.loads(notebook_path.read_text())
    sources = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        body = "".join(cell.get("source", []))
        for line in body.splitlines():
            if line.lstrip().startswith(("%", "!")):
                raise ProtocolError(
                    "This notebook uses IPython magics (" + line.strip() + ") and "
                    "jupyter is not available to convert it. Install jupyter, or "
                    "remove the magic."
                )
        sources.append(body)
    target.write_text("\n\n".join(sources) + "\n")
    return target


def start_solution(solution_path: Path, show_stderr: bool) -> subprocess.Popen:
    environment = os.environ.copy()
    environment.update(
        {
            "POTATO_DATA_DIR": str(DATA_DIR),
            "POTATO_MODELS_DIR": str(BASE_DIR / "models"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )

    return subprocess.Popen(
        [sys.executable, str(solution_path)],
        cwd=BASE_DIR,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None if show_stderr else subprocess.DEVNULL,
        start_new_session=os.name == "posix",
    )


def play_game(
    process: subprocess.Popen,
    reader: LineReader,
    secret: str,
    deadline: float,
    verbose: bool,
) -> tuple[int | None, str | None]:
    word1 = START_WORD_1
    word2 = START_WORD_2

    try:
        send_message(process, {"event": "new_game"})
        for turn in range(1, MAX_TURNS + 1):
            winner_word, verdict = public_oracle(secret, word1, word2)
            request = {
                "turn": turn,
                "winner_word": winner_word,
                "verdict": verdict,
                "word1": word1,
                "word2": word2,
            }

            if verbose:
                print(
                    f"Turn {turn:2d}: {word1} vs {word2} -> "
                    f"{winner_word} ({verdict})"
                )

            send_message(process, request)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProtocolError(
                    f"The complete run exceeded {TIME_LIMIT_SEC:g} seconds"
                )
            proposal = read_proposal(reader, remaining)
            if verbose:
                print(f"         solution proposes: {proposal}")

            if proposal.casefold() == secret.casefold():
                send_message(process, {"status": "win"})
                return turn, None

            word1 = winner_word
            word2 = proposal

        send_message(process, {"status": "loss"})
        return None, None
    except ProtocolError as error:
        return None, str(error)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test a Python submission with the approximate public judge."
    )
    parser.add_argument(
        "solution",
        type=Path,
        help="solution.ipynb (converted automatically) or an exported .py",
    )
    parser.add_argument(
        "--secret",
        action="append",
        dest="secrets",
        help="public test word; repeat this option to run several games",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=TIME_LIMIT_SEC,
        help=(
            "total seconds for the whole run, matching the official single "
            f"limit (default: {TIME_LIMIT_SEC:g})"
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="run only the first N selected public games",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--verbose",
        action="store_true",
        help="show every comparison and the solution's diagnostic output",
    )
    output_group.add_argument(
        "--quiet",
        action="store_true",
        help="show only the final suite summary",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    solution_path = args.solution.expanduser().resolve()

    if not solution_path.is_file():
        print(f"Solution file not found: {solution_path}", file=sys.stderr)
        return 2
    if solution_path.suffix not in (".py", ".ipynb"):
        print("Pass solution.ipynb or an exported .py file.", file=sys.stderr)
        return 2
    if args.time_limit <= 0:
        print("--time-limit must be positive", file=sys.stderr)
        return 2
    if args.limit is not None and args.limit <= 0:
        print("--limit must be positive", file=sys.stderr)
        return 2

    secrets = args.secrets or list(test_public_secrets)
    if args.limit is not None:
        secrets = secrets[: args.limit]
    unknown = [secret for secret in secrets if secret.casefold() not in word_to_index]
    if unknown:
        print(
            "Unknown test word(s): " + ", ".join(repr(word) for word in unknown),
            file=sys.stderr,
        )
        return 2

    total_score = 0.0
    wins = 0
    protocol_errors = 0
    not_run = 0

    print(
        f"Local judge: {len(secrets)} public games in one solution process.\n"
        "It uses PUBLIC embeddings; official private results may differ.\n"
    )
    started = time.monotonic()
    deadline = started + args.time_limit

    # A notebook is converted first, exactly as the official judge does, so no
    # manual export step is needed.
    workspace = tempfile.TemporaryDirectory(prefix="potato-local-")
    try:
        if solution_path.suffix == ".ipynb":
            solution_path = notebook_to_script(solution_path, Path(workspace.name))
    except ProtocolError as error:
        print(error, file=sys.stderr)
        workspace.cleanup()
        return 2

    process = start_solution(solution_path, show_stderr=args.verbose)
    try:
        if process.stdout is None:
            print("The solution's standard output is unavailable", file=sys.stderr)
            return 1
        reader = LineReader(process.stdout)

        for index, requested_secret in enumerate(secrets):
            secret = words[word_to_index[requested_secret.casefold()]]
            if args.verbose:
                print(f"=== Hidden local test word: {secret} ===")

            turn, error = play_game(
                process,
                reader,
                secret,
                deadline,
                args.verbose,
            )
            if error is not None:
                protocol_errors = 1
                not_run = len(secrets) - index - 1
                print(f"{secret}: PROTOCOL ERROR — {error}")
                break
            if turn is None:
                if not args.quiet:
                    print(
                        f"{secret}: not found in {MAX_TURNS} turns, "
                        "game score 0.00/1.00"
                    )
            else:
                game_score = score_for_turn(turn)
                total_score += game_score
                wins += 1
                if not args.quiet:
                    print(
                        f"{secret}: found on turn {turn}, "
                        f"game score {game_score:.2f}/1.00"
                    )

        if not protocol_errors:
            try:
                send_message(process, {"event": "done"})
            except ProtocolError:
                pass
    finally:
        stop_process(process)
        workspace.cleanup()

    final_score = normalized_score(total_score, len(secrets))
    elapsed = time.monotonic() - started
    print(
        f"Local summary: {wins}/{len(secrets)} wins, "
        f"normalized score {final_score:.2f}/100, "
        f"elapsed {elapsed:.2f}s"
    )
    if protocol_errors:
        print(
            "The shared process failed; "
            f"the remaining {not_run} game(s) were not run and score zero."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
