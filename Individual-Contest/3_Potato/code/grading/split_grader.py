"""Split-aware wrapper around the Potato Yandex Contest grader.

The participant-facing leaderboard uses one hidden split at a time.  The
organizer-only ``both`` mode evaluates A and B independently and reports both
aggregate scores, without exposing per-secret results.

Split selection is driven by ``GRADE_SPLIT`` (declared in ``.gitlab-ci.yml``), so
switching the graded round needs no other edit.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path

import grader as core


SPLIT_FILES = {
    "test_leaderboard_a": "secrets_leaderboard_a.json",
    "test_leaderboard_b": "secrets_leaderboard_b.json",
}

TEST_NAMES = {
    "test_leaderboard_a": "leaderboard-a",
    "test_leaderboard_b": "leaderboard-b",
}

# Accepted shorthands, so an operator can set GRADE_SPLIT=a.
SPLIT_ALIASES = {
    "a": "test_leaderboard_a",
    "b": "test_leaderboard_b",
}

# Files published alongside the report, as (path, testDataType).  Both are written
# into the job's working directory and listed in `.gitlab-ci.yml` artifacts:paths.
STDERR_LOG = "solution_stderr.log"
STDERR_TAIL = "solution_output.log"
SOLUTION_PY = "solution.py"
ARTIFACT_FILES = (
    # The program that actually ran: nbconvert's output, this problem's analogue of
    # an executed notebook.
    (SOLUTION_PY, "OUTPUT"),
    # Everything the run printed -- nbconvert's merged streams, then the
    # participant's own stderr from the container.
    (STDERR_TAIL, "ERROR"),
)

# A failing submission can print a warning per turn across 120 games, so the log is
# trimmed before it is published.  The FULL log stays in the job artifacts.
LOG_TAIL_LINES = int(os.environ.get("LOG_TAIL_LINES", 300))


def write_log_tail() -> None:
    """Write the published, trimmed copy of the run log.

    The last lines are the useful ones -- a traceback, or the grader's reason for
    the verdict -- and what is dropped is said so, rather than silently cut.
    """

    source = Path(STDERR_LOG)
    if not source.is_file():
        return
    lines = source.read_text(errors="replace").splitlines(keepends=True)
    dropped = len(lines) - LOG_TAIL_LINES
    header = f"[{dropped} earlier lines omitted]\n" if dropped > 0 else ""
    Path(STDERR_TAIL).write_text(header + "".join(lines[-LOG_TAIL_LINES:]))


def report_artifacts(test_names: list[str]) -> list[dict]:
    """Reference the run's files from the report.

    ``artifacts`` is a top-level sibling of ``report``: each entry needs a
    ``testName`` matching a row in ``report.tests``, a ``testDataType`` from the
    schema's enum, and a ``path`` the publish job can read -- the file itself, not
    its contents.  Empty or absent files are skipped, so no entry ever dangles.
    """

    write_log_tail()
    entries = []
    for name, data_type in ARTIFACT_FILES:
        path = Path(name)
        if not path.is_file() or path.stat().st_size == 0:
            continue
        entries.extend(
            {"testName": test, "testDataType": data_type, "path": name}
            for test in test_names
        )
    return entries


def normalize_split(value: str) -> str:
    value = value.strip().casefold()
    if value == "both":
        return "both"
    value = SPLIT_ALIASES.get(value, value)
    if value not in SPLIT_FILES:
        raise ValueError(
            f"unknown GRADE_SPLIT {value!r}; expected one of "
            f"{', '.join(sorted(SPLIT_FILES))} or 'both'"
        )
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--private-data", type=Path, required=True)
    parser.add_argument("--public-data", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=Path("report.json"))
    parser.add_argument(
        "--split",
        default=os.environ.get("GRADE_SPLIT", "test_leaderboard_a"),
        help=(
            "hidden set to evaluate: test_leaderboard_a | test_leaderboard_b | "
            "both. 'both' is organizer/author only."
        ),
    )
    return parser.parse_args()


def split_keys(selection: str) -> tuple[str, ...]:
    if selection == "both":
        return ("test_leaderboard_a", "test_leaderboard_b")
    return (selection,)


def load_secrets(
    private_data: Path,
    split: str,
    word_to_index: dict[str, int],
) -> list[str]:
    path = private_data / SPLIT_FILES[split]
    if not path.is_file():
        raise ValueError(f"missing private split file: {path.name}")

    secrets = json.loads(path.read_text())
    if not isinstance(secrets, list) or not secrets:
        raise ValueError(f"{path.name} must contain a non-empty JSON list")
    if not all(isinstance(secret, str) and secret.strip() for secret in secrets):
        raise ValueError(f"{path.name} contains an invalid secret")

    normalized = [secret.casefold() for secret in secrets]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{path.name} contains duplicate secrets")

    missing = [secret for secret in secrets if secret.casefold() not in word_to_index]
    if missing:
        raise ValueError(f"{path.name} contains a secret outside the vocabulary")
    return secrets


def preflight_splits(private_data: Path, word_to_index: dict[str, int]) -> None:
    """Assert the split invariants before grading anything.

    Every submission re-checks the hidden rounds it is NOT grading: each one still
    parses, still lies inside the vocabulary, and is still disjoint from the others.
    A bad edit to one round therefore surfaces on the next submission instead of at
    the end of the contest.
    """

    loaded: dict[str, set[str]] = {}
    for split in SPLIT_FILES:
        secrets = load_secrets(private_data, split, word_to_index)
        loaded[split] = {secret.casefold() for secret in secrets}
        print(f"split {split}: {len(secrets)} secrets, all in vocabulary")

    names = sorted(loaded)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            overlap = loaded[first] & loaded[second]
            if overlap:
                raise ValueError(
                    f"{first} and {second} share {len(overlap)} secrets; hidden "
                    "rounds must be disjoint"
                )
    print(f"split disjointness verified across {len(names)} hidden rounds")


def suite_verdict(results: list[core.GameResult]) -> str:
    return next(
        (result.verdict for result in results if result.verdict != "OK"),
        "OK",
    )


def build_report(
    results_by_split: dict[str, list[core.GameResult]],
    artifacts: list[dict] | None = None,
) -> dict:
    tests = []
    for split, results in results_by_split.items():
        tests.append(
            {
                "testName": TEST_NAMES[split],
                "testsetName": "tests",
                "verdict": suite_verdict(results),
                # The test row is where the score lives; result carries only the
                # encoded message. Per-split, on the contest's 0--100 scale.
                "score": round(core.suite_score(results), 2),
                "runningTime": sum(
                    result.running_time_ms for result in results
                ),
            }
        )

    # Same shape as 02_animal_deduction and 03_customer_segments: `result` carries
    # a JSON-encoded message keyed by split letter -- {"a": score} -- and the
    # per-split scores are the test rows. `result` is {score} XOR {message} and
    # permits no other key, so there is no separate encoded_json field.
    encoded = {
        split[-1]: test["score"]
        for split, test in zip(results_by_split, tests)
    }
    report: dict = {
        "report": {
            "result": {"message": json.dumps(encoded)},
            "tests": tests,
        }
    }
    if artifacts:
        report["artifacts"] = artifacts
    return report


def main() -> int:
    args = parse_args()
    started = core.mark_run_started()
    # The selected hidden split is grader metadata.  Do not leak it into the
    # participant process created by grader.run_suite().
    os.environ.pop("GRADE_SPLIT", None)
    repository = args.repository.resolve()
    private_data = args.private_data.resolve()
    public_data = args.public_data.resolve()
    report_path = args.report.resolve()
    stderr_path = Path("solution_stderr.log").resolve()

    try:
        selection = normalize_split(args.split)
        if not repository.is_dir():
            raise core.SubmissionError(
                "PresentationError", "participant repository is missing"
            )
        core.validate_submission_tree(repository)
        core.protect_private_files(private_data)
        words, _legacy, embeddings, word_to_index = core.load_private_space(
            private_data
        )
        core.preflight_public_data(public_data, words)
        preflight_splits(private_data, word_to_index)

        selected_splits = split_keys(selection)
        secrets_by_split: dict[str, list[str]] = {
            split: load_secrets(private_data, split, word_to_index)
            for split in selected_splits
        }

        results_by_split: dict[str, list[core.GameResult]] = {}
        with tempfile.TemporaryDirectory(prefix="potato-solution-") as directory:
            solution_directory = Path(directory)
            solution = core.convert_notebook(
                repository, solution_directory, stderr_path
            )
            solution_directory.chmod(0o755)
            # The converted program is published as an artifact, so it has to
            # outlive the temporary directory it was written into.
            shutil.copyfile(solution, Path(SOLUTION_PY))

            # Each split gets a fresh container.  This prevents state learned on A
            # from changing the independent B measurement.
            for split, secrets in secrets_by_split.items():
                results_by_split[split] = core.run_suite(
                    solution,
                    public_data,
                    secrets,
                    words,
                    embeddings,
                    word_to_index,
                    stderr_path,
                )

        core.set_elapsed(started)
        artifacts = report_artifacts(
            [TEST_NAMES[split] for split in results_by_split]
        )
        report_path.write_text(
            json.dumps(build_report(results_by_split, artifacts), indent=2) + "\n"
        )

        for split, results in results_by_split.items():
            wins = sum(result.turn is not None for result in results)
            score = core.suite_score(results)
            print(
                f"{TEST_NAMES[split]}: {wins}/{len(results)} wins, "
                f"score {score:.2f}/100"
            )

        verdicts = {suite_verdict(results) for results in results_by_split.values()}
        if "RuntimeError" in verdicts:
            print(
                "--- participant stderr (tail) ---\n" + core.tail_file(stderr_path),
                file=core.sys.stderr,
            )
        return 0
    except core.SubmissionError as error:
        core.set_elapsed(started)
        # A pre-run rejection -- missing or oversized notebook, a conversion
        # failure -- never starts a container, so without this the log is empty or
        # absent and the submission is published with no artifact at all.
        with stderr_path.open("a") as handle:
            handle.write(f"grader: {error.verdict}: {error}\n")
        core.write_terminal_report(
            report_path,
            error.verdict,
            str(error),
            report_artifacts(["potato"]),
        )
        print(f"Submission rejected: {error}", file=core.sys.stderr)
        if error.verdict == "RuntimeError":
            print(
                "--- participant stderr (tail) ---\n" + core.tail_file(stderr_path),
                file=core.sys.stderr,
            )
        # A rejected submission is a normal outcome: exit 0 so the verdict report
        # is published by send_report instead of being replaced by a Crash.
        return 0
    except Exception as error:
        core.set_elapsed(started)
        core.write_terminal_report(report_path, "Crash")
        print(
            f"Internal grader error: {type(error).__name__}: {error}",
            file=core.sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
