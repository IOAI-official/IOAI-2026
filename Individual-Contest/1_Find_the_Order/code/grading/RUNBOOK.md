# Find the Order — grader runbook

Internal. `README.md` is Contest's own CI documentation; this file is how *this*
grader is operated.

## The dataset contract

`dataset/` and `models/` are **gitignored** — they are baked into the job image, not
committed. That keeps submissions fast, but it also means the layout below is the
only thing tying the image to `check.py`. Get it wrong and grading fails at best,
leaks ground truth at worst. `check.py`'s `preflight_dataset()` asserts all of it
before a notebook is allowed to run.

```
/problem/dataset/
  train/<did>/chunk_*.wav          # + prefix.json
  pretrain/…                       # 20-dialogue dry-run slice of train
  pretest/…                        # 20-dialogue dry-run slice of test_public
  test_leaderboard_a/…             # live leaderboard
  test_leaderboard_b/…             # final ranking
  train_answers.json
  pretrain_answers.json
  pretest_answers.json
  test_leaderboard_a_answers.json
  test_leaderboard_b_answers.json
/problem/models/{qwen2.5-0.5b,whisper-small,wav2vec2-base-960h}/
```

Two rules, both load-bearing:

1. **`prefix.json` lives inside each split; `answers.json` never does.** Ground truth
   sits at the dataset *root* as `<split>_answers.json`. A split directory is
   bind-mounted **whole** into the participant's container, so anything inside it is
   readable by their notebook. An `answers.json` left in a graded split hands over
   the answers.
2. **Answer files are named `<split>_answers.json`**, not `answers_<split>.json`.
   `check.py` derives the path from `GRADE_SPLIT`; a mismatched name means the
   grader cannot find the ground truth and Crashes *after* paying for a full run.

## Switching rounds

Edit `GRADE_SPLIT` in `.gitlab-ci.yml` and nothing else:

| Round | `GRADE_SPLIT` | `TRAIN_SPLIT` |
|---|---|---|
| Dry run / pipeline validation | `pretest` | `pretrain` |
| Live leaderboard | `test_leaderboard_a` | `train` |
| Final ranking | `test_leaderboard_b` | `train` |

Run a `pretest` dry run after **any** change to the grader or the image. It grades
20 dialogues instead of 100, so it costs a couple of minutes, and it exercises the
identical code path as a real round.

## pretrain / pretest

Length-stratified slices of `train` and `test_public`, 20 dialogues each, baked into
the job image alongside every other split.

`pretest` is carved from **`test_public`** — never from `test_leaderboard_a` or
`test_leaderboard_b`. Dry runs are repeated many times; pointing them at a graded
split is how a hidden split gets contaminated. The public split costs nothing here,
because `pretest` only proves the pipeline runs and scores, it measures nothing
secret.

Both were selected to match their parent's chunk-count distribution (mean 10.8
chunks, ~30% of dialogues longer than 12) so a dry run exercises the same long
dialogues that dominate the time budget in a real round.

To reconstruct them, read the dialogue ids from the image's own
`/problem/dataset/pretrain_answers.json` and `pretest_answers.json`, copy those
directories out of the canonical dataset into `dataset/<name>/`, prune `prefix.json`
to those ids, and write the ground truth to `dataset/<name>_answers.json` at the
dataset **root** — never inside the split.

## Rebuilding the job image

The job image is `runner-job-image:gpu` with the dataset and models copied in. It is
referenced by `image:` in `.gitlab-ci.yml`.

```bash
REG=contest.gitlab.yandexcloud.net:5050/problems/9945797-2026-05-21-bqev5jsece/ml/ci-template
TAG=$(date +%Y%m%d)                # NEVER reuse a tag: CI caches by tag

# 1. lay out ./dataset and ./models exactly as in "The dataset contract" above.
#    Source the audio from the CANONICAL dataset, not from a clone of this repo --
#    the wavs in a fresh clone are git-LFS pointer stubs (131 bytes) unless you have
#    run `git lfs pull`, and baking those produces a silently broken image.

# 2. build + push
podman login contest.gitlab.yandexcloud.net:5050
podman build -t $REG:$TAG -f Dockerfile .
podman push $REG:$TAG

# 3. point CI at the new tag, commit, push
#    image: $REG:$TAG        <- in .gitlab-ci.yml
# 4. trigger a GRADE_SPLIT=pretest dry run and confirm it reports OK
```

The current `image:` line has **no tag**, so it resolves to `:latest` and CI caching
can serve a stale image after a rebuild. Move to dated tags at the next rebuild.

## What the grader guarantees

- Only `solution.ipynb` is fetched from a submission — never the contestant's repo.
- Dataset and models are mounted **read-only**; only `$REPO` is writable.
- The notebook runs with `--network=none`; grading secrets are unset before it starts.
- Ground truth is never inside any directory the notebook can see.

A hostile notebook can still read `/proc/<ppid>/environ`. Full isolation needs a
network-isolated runner.
