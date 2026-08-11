# Find the Order — code & data

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline/            the baseline solution package
  baseline-original/   the baseline as originally kept during development
  grading-original/    the grader used to score submissions
```

The **data is not in this repository** — it is published as a standalone Hugging Face dataset:

- <https://huggingface.co/datasets/IOAI-official/ioai-2026-find-the-order>

The dataset has `public/` (what contestants received) and `private/` (the graded leaderboard A/B splits) — its dataset card documents every subset.

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline transcribes each turn with a speech model and orders turns by a simple heuristic.

```bash
cd code/baseline
jupyter lab solution.ipynb
```

Needs `librosa`, `torch` and `transformers`. The audio dataset is large (~4.5 GB) — download only the splits you need.

## Scoring a solution

`code/grading-original/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
