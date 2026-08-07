# Catch the Robot — grader runbook

Internal. `README.md` is Contest's own CI documentation; this file is how *this*
grader is operated.

## The dataset contract

`dataset/` is **gitignored** — it is baked into the job image, not committed. That
keeps submissions fast, but it also means the layout below is the only thing tying
the image to `check.py`. Get it wrong and grading fails at best, leaks ground truth
at worst. `check.py`'s `preflight_dataset()` asserts all of it before a notebook is
allowed to run.

```
/problem/dataset/
  train/observations.json               # 60000 rows, 10000 per robot
  pretrain/observations.json            # 3000-row dry-run slice of train
  pretest/observations.json             #  600-row dry-run slice of test_public
  test_leaderboard_a/observations.json  # 3600 rows, live leaderboard
  test_leaderboard_b/observations.json  # 3600 rows, final ranking
  train_answers.json
  pretrain_answers.json
  pretest_answers.json
  test_leaderboard_a_answers.json
  test_leaderboard_b_answers.json
```

Two rules, both load-bearing:

1. **A split directory holds only `observations.json`; ground truth never does.**
   It sits at the dataset *root* as `<split>_answers.json`. A split directory is
   bind-mounted **whole** into the participant's container, so anything inside it is
   readable by their notebook. Labels left in a graded split hand over the answers.
   `train`'s public labels are re-attached by `check.py` as a single nested file
   mount at `dataset/train/labels.json`, which is the path the statement documents.
2. **Answer files are named `<split>_answers.json`**, not `answers_<split>.json`.
   `check.py` derives the path from `GRADE_SPLIT`; a mismatched name means the
   grader cannot find the ground truth and Crashes *after* paying for a full run.

At grading time `dataset/test_public/` therefore contains **no** `labels.json`,
even though the participant package ships one. The statement says so explicitly; a
notebook that reads test_public labels unconditionally gets a RuntimeError.

## Switching rounds

Edit `GRADE_SPLIT` in `.gitlab-ci.yml` and nothing else:

| Round | `GRADE_SPLIT` | `TRAIN_SPLIT` |
|---|---|---|
| Dry run / pipeline validation | `pretest` | `pretrain` |
| Live leaderboard | `test_leaderboard_a` | `train` |
| Final ranking | `test_leaderboard_b` | `train` |

Run a `pretest` dry run after **any** change to the grader or the image. It grades
600 rows instead of 3600 and trains on 3000 instead of 60000, so it costs a couple
of minutes, and it exercises the identical code path as a real round.

A dry-run score for the new multi-task dataset must be calibrated after its
`pretrain` and `pretest` slices are rebuilt. Judge the first dry run by its verdict,
then record the deterministic reference score here.

## Building pretrain / pretest

Both are slices of splits that already exist — no new rows. `pretrain` is 500 rows
per robot taken from `train`; `pretest` is 100 per robot taken from `test_public`.
`prepare_dataset.py` cuts both with fixed seeds and stratifies by `robot_id`, because
the metric is the mean of the six per-robot accuracies and a dry-run split that
under-represented a robot would not exercise the metric it exists to validate.

`pretest` is carved from **`test_public`** — never from `test_leaderboard_a` or
`test_leaderboard_b`. Dry runs are repeated many times; pointing them at a graded
split is how a hidden split gets contaminated. The public split costs nothing here,
because `pretest` only proves the pipeline runs and scores, it measures nothing
secret.

They live in the job image and are reproducible from the same organizer archive:

```bash
python3 prepare_dataset.py /path/to/organizer_splits.zip ./dataset --force
```

The adjacent `dataset_manifest.json` records the source archive hash, sampling
seeds and every generated file hash. It is intentionally excluded from the image.

## Rebuilding the job image

The job image is `runner-job-image:gpu` with the dataset copied in (that is the
whole of `Dockerfile`). It is referenced by `image:` in `.gitlab-ci.yml`.

The canonical commands are the ones GitLab prints on this repo's own
**Container Registry** page — use those, they already carry the right registry
path. Log in once and it covers every problem; the build and push are per-problem,
each with its own dataset.

```bash
REG=contest.gitlab.yandexcloud.net:5050/problems/9945797-2026-05-21-5hxevedli4/ml/ci-template

# 1. Build ./dataset from the organizer-only archive. This deterministically
#    creates new 500-row-per-robot pretrain and 100-row-per-robot pretest slices.
python3 prepare_dataset.py /path/to/organizer_splits.zip ./dataset --force

# 2. Build a dated immutable tag (docker and podman are interchangeable here).
docker login contest.gitlab.yandexcloud.net:5050
docker build --platform linux/amd64 --provenance=false \
  -t $REG:multitask-v6-20260803 -f Dockerfile .
docker push $REG:multitask-v6-20260803

# 3. Pin the same tag in .gitlab-ci.yml, then trigger a GRADE_SPLIT=pretest
#    dry run and confirm it reports OK.
```

**The image must exist before the `image:` line is merged** — a pipeline pointed at
an image that has not been pushed fails with an image-pull error before it grades
anything.

Use immutable dataset tags. Reusing `:latest` allows CI caching to serve a stale
image after a rebuild and makes a previous dataset difficult to recover. Push the
dated tag first, validate that it exists, and only then update `image:` in
`.gitlab-ci.yml` to the same tag.

Registry access for the runners was still outstanding on Nikita's side as of
2026-07-28 — if the pull fails from CI even though the image is visible on the
Container Registry page, that is the cause, not this repo.

## Reference scores

Measured locally against the shipped splits (`tools/` is not involved; these come
from running the notebooks in `../author-solution/`):

| Submission | `test_leaderboard_a` | `test_leaderboard_b` |
|---|---|---|
| `solution.ipynb` baseline — always `up` | 20.81 | 20.58 |
| Author solution — per-robot MLPs | 72.03 | 71.14 |

The gap is the point of the problem: the leaderboard rewards modelling each
robot's behaviour across navigation, pickup and placement rather than relying on a
single dominant movement action.

## What the grader guarantees

- Only `solution.ipynb` is fetched from a submission — never the contestant's repo.
- The dataset is mounted **read-only**; only `$REPO` is writable.
- The notebook runs with `--network=none`; grading secrets are unset before it starts.
- Ground truth is never inside any directory the notebook can see.

A hostile notebook can still read `/proc/<ppid>/environ`. Full isolation needs a
network-isolated runner.
