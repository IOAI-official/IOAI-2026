# Catch the Robot — CI template (grader)

Grades submissions for **Catch the Robot**. This repo is grader-side only; it is
never exposed to participant code during a run. For how to operate it — dataset
layout, switching rounds, rebuilding the job image — see [RUNBOOK.md](RUNBOOK.md).

## Grading contract

An api-triggered pipeline (`.gitlab-ci.yml`) runs on the job image, which carries
the locked dataset at `/problem/dataset`. `before_script` checks that root is
provisioned and pulls the participant's `solution.ipynb` into `$REPO_NAME`. Then
`python check.py`:

1. **runs the notebook inside a podman sandbox** (`--network=none`, GPU via
   `--device`, the shared `ioai-gitlab` runtime so nothing is pip-installed at
   grade time); data crosses only as read-only bind mounts:
   - `<TRAIN_SPLIT>/` → `/work/dataset/train`, with `<TRAIN_SPLIT>_answers.json`
     layered back in as `/work/dataset/train/labels.json` (public);
   - `<GRADE_SPLIT>/` → `/work/dataset/test_public` — observations only; the
     ground truth lives at the dataset root and is mounted nowhere;
   `$REPO` is the read-write `/work` volume — `solution.ipynb` in,
   `predictions.json` (a JSON list of ints `0`–`5`) + `executed.ipynb` out;
2. **scores** per-robot accuracy against `<GRADE_SPLIT>_answers.json` — pure
   Python on the host, so no numpy/torch is needed outside the container — and
   writes `report.json`.

The podman harness (`.gitlab-ci.yml` skeleton and check.py's
`_podman_run`/`preflight_gpu`/`run_notebook`) is shared verbatim across problems;
only the `variables:` block, `_volume_args()`, `preflight_dataset()` and
`score_submission()` differ.

`GRADE_SPLIT` = `pretest` (dry run) | `test_leaderboard_a` (live) |
`test_leaderboard_b` (final).

## Metric

Mean over the 6 robots of (fraction of that robot's moves predicted correctly),
on a 0–100 scale. Verdicts: `OK` / `RuntimeError` / `TimeLimitExceeded` /
`PresentationError` / `Crash`.

`report.json` carries the score, verdict and checking time on **every** path,
including failures. `result.message` carries the score as the JSON string
`{\"a\": ...}` for the CALCULATOR-backed live leaderboard; detailed diagnostics
remain in the CI job log.

## Files

- `.gitlab-ci.yml` — canonical 3-stage skeleton (test → send_report → send_crash);
  only the per-problem `variables:` block differs from the other problems.
- `Dockerfile` — the job image: `runner-job-image:gpu` with the dataset copied to
  `/problem/dataset`.
- `prepare_dataset.py` — deterministic organizer archive → registry layout builder.
- `test_check.py` — regression coverage for the six-action output contract.
- `check.py` — the grader (preflight → execute → score).
- `RUNBOOK.md` — dataset contract, round switching, image rebuild, reference scores.
- `dataset/` — **not committed**; baked into the job image (see RUNBOOK).
