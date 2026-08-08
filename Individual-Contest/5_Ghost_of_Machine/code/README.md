# Ghost of the Machine — code

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline/   the reference solution given to contestants, plus any helper code
  grading/    the grader used to score submissions
```

The **data is not in this repository**, and the dataset for this task is **not published**.

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline measures the average position of the boundary across the training passages and predicts that same fraction for every test passage.

```bash
cd baseline
jupyter lab solution.ipynb
```

Pure Python — no machine-learning libraries needed to run it. Reads `dataset/train` and `dataset/test_public`, writes `answers.jsonl`.

## Scoring a solution

`grading/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
