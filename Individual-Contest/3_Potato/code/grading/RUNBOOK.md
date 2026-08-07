# Potato Contact — grader runbook

Operational procedures for the CI template. The design rationale lives in
`README.md`; this file is the "how do I actually do it" reference.

---

## 1. Switch the graded round

Live leaderboard runs on A; the final standings run on B.

1. Edit `GRADE_SPLIT` in `.gitlab-ci.yml` (`test_leaderboard_a` → `test_leaderboard_b`).
2. Commit and push.
3. Retest the submissions you want scored on B.

That value is the only edit. `split_grader.py` resolves the file name, and
`preflight_splits()` re-verifies both rounds on every submission, so a mistake in the
round you are *not* grading still surfaces immediately.

The `author-solution` repository is detected by path and always graded on **both**
rounds, each in a fresh container, so state learned on A cannot influence B. Never
enable `both` for a participant repository — it would expose B while the contest is
running and make it tunable.

## 2. Rebuild the job image (whenever the models change)

The weights are **not** in this repository. They live in the job image, and the exact
same bundle is what participants receive via `.dataset-url`. Keep the two identical —
a participant who tunes against a different bundle than the judge mounts will silently
score differently.

```bash
# 1. Assemble the bundle. The vendor/name layout must match statement.md section 6.
#    models/
#      Qwen/Qwen3-Embedding-0.6B/   (+ example.py)
#      BAAI/bge-m3/                 (+ example.py)

# 2. Build and push. NEVER reuse a tag -- CI caches by tag.
REG=contest.gitlab.yandexcloud.net:5050/problems/9945797-2026-06-03-98m1xdyeso/ml/ci-template
TAG=$(date +%Y%m%d)
docker login "$REG"
docker build -t "$REG/potato-job:$TAG" .
docker push  "$REG/potato-job:$TAG"

# 3. Point CI at the new tag.
#    .gitlab-ci.yml -> test.image: .../potato-job:$TAG
```

Then verify the bundle still loads offline before you trust it:

```bash
POTATO_MODELS_DIR=models POTATO_DATA_DIR=public_data \
  python models/Qwen/Qwen3-Embedding-0.6B/example.py
POTATO_MODELS_DIR=models POTATO_DATA_DIR=public_data \
  python models/BAAI/bge-m3/example.py
```

Both must print `(1602, 1024)` with no network access. Run them with
`HF_HUB_OFFLINE=1` already set — the examples set it themselves, but an inherited
`HF_TOKEN` in your shell can mask a missing file by silently fetching it.

## 3. Refresh the participant `.dataset-url`

The bundle is ~3.3 GB, far past the 100 MB in-repo limit, so participants download it
from object storage. Refreshing the link needs **no re-upload**:

```bash
aws s3 presign --endpoint-url https://storage.yandexcloud.net \
  --expires-in 2592000 s3://ioai-2026-datasets/datasets/potato-models.zip
```

Paste the result into `.dataset-url` in the **statements** repository. Only re-upload
when the bundle contents actually change.

## 4. Change a limit

All limits are declared in the `variables:` block of `.gitlab-ci.yml` and read as
environment variables by `grader.py`:

| Variable | Meaning | Verdict when exceeded |
|---|---|---|
| `MAX_NOTEBOOK_BYTES` | notebook size, checked before conversion | `PresentationError` |
| `TIME_LIMIT_SEC` | the whole round: start-up, preparation and every game | `TimeLimitExceeded` |

There is deliberately **one** time limit, not a per-turn budget and a total. A
submission spends its allowance however it likes -- all of it on loading a model,
or spread across turns. That also means there is no `IdlenessLimitExceeded`
verdict: a submission that stalls simply burns its own budget and ends in
`TimeLimitExceeded`.

Keep the job `timeout:` above `TIME_LIMIT_SEC` × 2 (author-solution runs both
rounds) plus image-pull time.

Anything published to participants — the time limit above all — must be changed in
the "Rules" section of `statements/statement.md` in the same breath.

The statement quotes the limit in **minutes** (`TIME_LIMIT_SEC: "600"` -> "10
minutes"), so convert when you change it, and change both in the same commit.

## 5. Re-test the failure paths

The `author-solution` repository carries `broken/`, one notebook per verdict. After any
grader change, run each through the real pipeline and confirm the verdict still
matches the filename. The expected results are logged in
`author-solution/README.md`; update that table when you re-run them.

## 6. Reading a failed job

- `report.json` — always published, always carries `runningTime`.
- `solution_stderr.log` — the participant's stderr, kept as an artifact. On
  `RuntimeError` a tail is also printed into the job log.
- `Crash` means the grader itself failed, not the submission. Check the job log for
  `Internal grader error:`; the most common causes are a missing model mount
  (`MODELS_SRC`), an unpullable `RUNTIME_IMAGE`, or podman failing to start.
- A CPU-only run logs `GPU unavailable, grading on CPU`. Grading is still correct;
  model-heavy submissions are just slower, which can turn into a `TimeLimitExceeded`
  that would not happen on a GPU runner. If you see that line on the production
  runner, fix the runner before believing any TLE verdict.
