"""Build the private registry dataset from an organizer split archive.

The output matches check.py's /problem/dataset contract.  Ground-truth files are
kept at the dataset root; every split directory contains observations.json only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import zipfile
from collections import Counter
from pathlib import Path


TRAIN_ROWS = 60_000
EVAL_ROWS = 3_600
PRETRAIN_PER_ROBOT = 500
PRETEST_PER_ROBOT = 100
PRETRAIN_SEED = 20_260_803
PRETEST_SEED = 20_260_804
NUM_ROBOTS = 6
NUM_ACTIONS = 6


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(archive: zipfile.ZipFile, name: str):
    try:
        return json.loads(archive.read(name))
    except KeyError as error:
        raise ValueError(f"organizer archive is missing {name}") from error


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"
    )


def validate_split(
    name: str,
    observations: list,
    answers: list,
    *,
    expected_rows: int,
    expected_per_robot: int,
) -> None:
    if len(observations) != expected_rows or len(answers) != expected_rows:
        raise ValueError(
            f"{name}: expected {expected_rows} aligned rows, got "
            f"{len(observations)} observations and {len(answers)} answers"
        )

    counts = Counter()
    for index, (observation, answer) in enumerate(zip(observations, answers)):
        if isinstance(answer, bool) or not isinstance(answer, int) or not 0 <= answer < NUM_ACTIONS:
            raise ValueError(f"{name}[{index}]: invalid action {answer!r}")
        if not isinstance(observation, dict):
            raise ValueError(f"{name}[{index}]: observation must be an object")

        robot_id = observation.get("robot_id")
        if isinstance(robot_id, bool) or not isinstance(robot_id, int) or not 0 <= robot_id < NUM_ROBOTS:
            raise ValueError(f"{name}[{index}]: invalid robot_id {robot_id!r}")
        counts[robot_id] += 1

        image = observation.get("image")
        if not (
            isinstance(image, list)
            and len(image) == 8
            and all(isinstance(row, list) and len(row) == 8 for row in image)
            and all(isinstance(cell, list) and len(cell) == 2 for row in image for cell in row)
        ):
            raise ValueError(f"{name}[{index}]: image must have shape 8x8x2")
        if observation.get("direction") not in range(4):
            raise ValueError(f"{name}[{index}]: direction must be in 0..3")
        if not isinstance(observation.get("mission"), str) or not observation["mission"]:
            raise ValueError(f"{name}[{index}]: mission must be a non-empty string")
        carrying = observation.get("carrying")
        if carrying is not None and not (
            isinstance(carrying, list)
            and len(carrying) == 2
            and all(isinstance(value, int) and not isinstance(value, bool) for value in carrying)
        ):
            raise ValueError(f"{name}[{index}]: invalid carrying value {carrying!r}")

    expected_counts = {robot_id: expected_per_robot for robot_id in range(NUM_ROBOTS)}
    if dict(counts) != expected_counts:
        raise ValueError(f"{name}: robot balance {dict(counts)} != {expected_counts}")


def stratified_slice(
    observations: list,
    answers: list,
    *,
    per_robot: int,
    seed: int,
) -> tuple[list, list]:
    by_robot = {robot_id: [] for robot_id in range(NUM_ROBOTS)}
    for index, observation in enumerate(observations):
        by_robot[int(observation["robot_id"])].append(index)

    rng = random.Random(seed)
    selected = []
    for robot_id in range(NUM_ROBOTS):
        candidates = by_robot[robot_id]
        if len(candidates) < per_robot:
            raise ValueError(
                f"robot {robot_id}: need {per_robot} rows, found {len(candidates)}"
            )
        selected.extend(rng.sample(candidates, per_robot))
    selected.sort()
    return (
        [observations[index] for index in selected],
        [answers[index] for index in selected],
    )


def build(archive_path: Path, output: Path, *, force: bool) -> Path:
    archive_path = archive_path.resolve()
    output = output.resolve()
    if output.exists() and not force:
        raise FileExistsError(f"{output} already exists; pass --force to replace it")

    with zipfile.ZipFile(archive_path) as archive:
        train_observations = load_json(archive, "dataset/train/observations.json")
        train_answers = load_json(archive, "dataset/train/labels.json")
        public_observations = load_json(archive, "dataset/test_public/observations.json")
        public_answers = load_json(archive, "dataset/test_public/labels.json")
        leaderboard_a_observations = load_json(
            archive, "grader_data/test_leaderboard_a/observations.json"
        )
        leaderboard_a_answers = load_json(
            archive, "grader_data/test_leaderboard_a/answers.json"
        )
        leaderboard_b_observations = load_json(
            archive, "grader_data/test_leaderboard_b/observations.json"
        )
        leaderboard_b_answers = load_json(
            archive, "grader_data/test_leaderboard_b/answers.json"
        )

    validate_split(
        "train", train_observations, train_answers,
        expected_rows=TRAIN_ROWS, expected_per_robot=10_000,
    )
    for name, observations, answers in (
        ("test_public", public_observations, public_answers),
        ("test_leaderboard_a", leaderboard_a_observations, leaderboard_a_answers),
        ("test_leaderboard_b", leaderboard_b_observations, leaderboard_b_answers),
    ):
        validate_split(
            name, observations, answers,
            expected_rows=EVAL_ROWS, expected_per_robot=600,
        )

    pretrain_observations, pretrain_answers = stratified_slice(
        train_observations,
        train_answers,
        per_robot=PRETRAIN_PER_ROBOT,
        seed=PRETRAIN_SEED,
    )
    pretest_observations, pretest_answers = stratified_slice(
        public_observations,
        public_answers,
        per_robot=PRETEST_PER_ROBOT,
        seed=PRETEST_SEED,
    )
    validate_split(
        "pretrain", pretrain_observations, pretrain_answers,
        expected_rows=3_000, expected_per_robot=PRETRAIN_PER_ROBOT,
    )
    validate_split(
        "pretest", pretest_observations, pretest_answers,
        expected_rows=600, expected_per_robot=PRETEST_PER_ROBOT,
    )

    staging = output.with_name(output.name + ".staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    files = {
        "train/observations.json": train_observations,
        "train_answers.json": train_answers,
        "pretrain/observations.json": pretrain_observations,
        "pretrain_answers.json": pretrain_answers,
        "pretest/observations.json": pretest_observations,
        "pretest_answers.json": pretest_answers,
        "test_leaderboard_a/observations.json": leaderboard_a_observations,
        "test_leaderboard_a_answers.json": leaderboard_a_answers,
        "test_leaderboard_b/observations.json": leaderboard_b_observations,
        "test_leaderboard_b_answers.json": leaderboard_b_answers,
    }
    for relative, value in files.items():
        write_json(staging / relative, value)

    for split in ("train", "pretrain", "pretest", "test_leaderboard_a", "test_leaderboard_b"):
        names = sorted(path.name for path in (staging / split).iterdir())
        if names != ["observations.json"]:
            raise ValueError(f"{split}: unsafe files inside participant-visible split: {names}")

    if output.exists():
        shutil.rmtree(output)
    staging.replace(output)

    manifest_path = output.with_name(output.name + "_manifest.json")
    manifest = {
        "version": 1,
        "source_archive": str(archive_path),
        "source_sha256": sha256(archive_path),
        "pretrain_seed": PRETRAIN_SEED,
        "pretest_seed": PRETEST_SEED,
        "files": {
            str(path.relative_to(output)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(output.rglob("*"))
            if path.is_file()
        },
    }
    write_json(manifest_path, manifest)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("organizer_archive", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = build(args.organizer_archive, args.output, force=args.force)
    print(f"built {args.output.resolve()}")
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main()
