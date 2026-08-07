# Potato Yandex CI template

The private grader for the Potato Contact problem. Operational procedures — switching
rounds, rebuilding the job image, changing a limit — are in `RUNBOOK.md`.

## Layout

```text
.gitlab-ci.yml     pipeline: fetch solution.ipynb, grade, publish
Dockerfile         job image = runner base + grader deps + the offline model bundle
grader.py          protocol driver, container sandbox, limits, reporting
split_grader.py    round selection (GRADE_SPLIT) and the split-aware report
public_data/       the grader's OWN copy of the participant-visible data
private_data/      hidden embeddings and hidden word lists -- never mounted
models/            offline model bundle, gitignored, baked into the job image
```

`private_data/` must contain:

```text
private_data/vocabulary.json
private_data/private_embeddings.npy
private_data/secrets_leaderboard_a.json
private_data/secrets_leaderboard_b.json
```

## How a submission is graded

1. **Fetch.** Only `solution.ipynb` is taken from the submission — a single-file
   download for file tasks, or a partial `git checkout <sha> -- solution.ipynb` for
   repository tasks. The contestant's repository is never fully checked out and their
   LFS objects are never smudged.
2. **Gate.** The notebook is rejected before anything runs if it is missing, is not a
   regular file, or exceeds `MAX_NOTEBOOK_BYTES` → `PresentationError`.
3. **Convert.** `jupyter nbconvert --to python`. The notebook is never *executed* as a
   notebook; the exported program is what plays the games.
4. **Run.** The program starts **once** inside `RUNTIME_IMAGE` under podman with
   `--network=none`, a pid cap, and read-only mounts only. It plays every
   game in the round over stdin/stdout.
5. **Report.** Aggregate score per round, plus `runningTime` on every path.

### Why the participant data is served by the grader

`public_data/` holds the grader's own byte-identical copy of `vocabulary.json`,
`public_embeddings.npy` and `test_public.json`, and that is what gets mounted at
`/data`. The submission's own checkout is never used as a data source, for two reasons:
a submission must not be able to change what the judge feeds it, and single-file
submissions do not carry a `data/` directory at all. Keep this copy in sync with the
`statements` repository — `preflight_public_data()` fails the job if the vocabulary
drifts from the private one.

### Isolation

The participant container gets `--network=none` and three read-only mounts: the
converted solution, `public_data/`, and the model bundle. `private_data/` is **never
mounted**, so the hidden embeddings and word lists have no path into the container at
all. The `chmod` calls in `.gitlab-ci.yml` are defence in depth on the runner itself.

#### Read-only bind mounts, not a symlink overlay

The pre-upload checklist says "the overlay is built with **symlinks**; grader files are
only ever read, never copied, overwritten, or deleted". This grader meets that
requirement with `:ro` bind mounts instead, deliberately:

- **A symlink overlay cannot cross into a container.** A symlink pointing at a path
  outside the container's mount namespace resolves to nothing. The checklist wording
  predates containerised execution, where the grader ran the submission directly on the
  runner and an overlay of symlinks was the only way to expose files without copying.
- **`:ro` is strictly stronger.** A symlink only protects the target if the target's
  permissions happen to forbid writing — the participant can otherwise write straight
  through it. A read-only bind mount is enforced by the kernel regardless of ownership
  or mode.
- **Symlinks are rejected on the submission side anyway.** `validate_submission_tree()`
  fails any submission containing one, so treating symlinks as the exposure mechanism
  would contradict the rest of the design.

Nothing is copied, overwritten or deleted, which is the property the checklist item
actually protects. Every other IOAI-2026 grader that runs under podman does the same.
**Open with Nikita:** amend the checklist wording to "grader files are exposed
read-only (symlink overlay or `:ro` bind mounts)" so the intent survives without
mandating a mechanism that does not work inside a container.

## Rounds and splits

Two hidden rounds of 120 words each, disjoint, both drawn from the public vocabulary:

- `test_leaderboard_a` — live leaderboard, the default;
- `test_leaderboard_b` — final standings, selected after the contest.

`preflight_splits()` re-validates **both** rounds on every submission — each parses,
each lies inside the vocabulary, and they remain disjoint — so damage to the round that
is not currently being graded is caught immediately rather than at the end of the
contest.

The `author-solution` repository is graded on **both** rounds, each in a fresh
container so state learned on A cannot influence B. Never enable `both` for a
participant repository.

**`pretrain` and `pretest` do not exist for this problem, deliberately.** There is
nothing to train: the submission is a search strategy over a fixed public vocabulary,
with no fitting step and no labelled training rows. The participant-side
`dataset/test_public.json` (120 words, disjoint from both hidden rounds) is the public
dry-run set and fills the role `pretest` plays elsewhere.

## Verdicts

| Verdict | Cause |
|---|---|
| `OK` | every game in the round completed |
| `PresentationError` | notebook missing, oversized, unconvertible; symlink or special file in the submission; malformed protocol JSON; a word outside the vocabulary |
| `TimeLimitExceeded` | the round exceeded `TIME_LIMIT_SEC` -- whether spent on preparation, on one stalled turn, or across all games |
| `OutputLimitExceeded` | a single response line over 4 KB |
| `RuntimeError` | the program died mid-round; a stderr tail is printed to the job log and kept as an artifact |
| `Crash` | the grader or the infrastructure failed — not the submission's fault |

A protocol failure is terminal for the round: the shared stdin/stdout stream cannot be
trusted afterwards, so the failing game and every remaining game take that verdict.
