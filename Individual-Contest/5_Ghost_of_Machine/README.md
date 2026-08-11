# Ghost of the Machine — code & data

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline-original/   the baseline solution package
  grading-original/    the grader used to score submissions
```

The **data is not in this repository** — it is published as a standalone Hugging Face dataset:

- <https://huggingface.co/datasets/IOAI-official/ioai-2026-ghost-of-the-machine>

The dataset has `public/` (what contestants received) and `private/` (the graded leaderboard A/B splits) — its dataset card documents every subset.

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline measures the average position of the boundary across the training passages and predicts that same fraction for every test passage.

```bash
cd code/baseline-original
jupyter lab solution.ipynb
```

Pure Python — no machine-learning libraries needed to run it. Reads `dataset/train` and `dataset/test_public`, writes `answers.jsonl`.

## Scoring a solution

`code/grading-original/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
