# Robot Chasing — code & data

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline/            unofficial educational baseline — for use outside the contest environment
  grading/             unofficial educational evaluation — replays the grading outside the contest
  baseline-original/   official: the baseline exactly as kept during the contest
  grading-original/    official: the grader exactly as used to score submissions
```

## Run it outside the contest (unofficial, educational)

The `*-original` folders are the **official contest artifacts**, preserved verbatim — they are what actually ran during IOAI 2026, and they remain the authoritative reference. `baseline/` and `grading/` are **unofficial educational versions**, provided purely for convenience: they let anyone use the task code outside the contest environment and read the data directly from the Hugging Face dataset, with one click on Google Colab. Where the two disagree, the originals win.

| | |
|---|---|
| **Run the baseline** — fetches the dataset from Hugging Face and runs the untouched baseline | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/IOAI-official/IOAI-2026/blob/main/Individual-Contest/2_Robot_Chasing/code/baseline/solution.ipynb) |
| **Evaluate a solution** — replays the contest grading against the leaderboard splits | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/IOAI-official/IOAI-2026/blob/main/Individual-Contest/2_Robot_Chasing/code/grading/evaluate.ipynb) |

To evaluate your own attempt: open the evaluation notebook, upload your edited `solution.ipynb` via the Files pane, Run all.

The **data is not in this repository** — it is published as a standalone Hugging Face dataset:

- <https://huggingface.co/datasets/IOAI-official/ioai-2026-robot-chasing>

The dataset has `public/` (what contestants received) and `private/` (the graded leaderboard A/B splits) — its dataset card documents every subset.

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline predicts the same action (`0 = up`) for every observation, so it scores near zero on purpose. It exists to show the input/output contract.

```bash
cd code/baseline-original
jupyter lab solution.ipynb
```

`visualize_dataset.ipynb` and `visualization.py` render the grid worlds — useful for understanding the task.

Reads `dataset/test_public/observations.json`, writes `predictions.json`. Override the data location with the `DATASET_ROOT` environment variable.

## Scoring a solution

`code/grading-original/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
