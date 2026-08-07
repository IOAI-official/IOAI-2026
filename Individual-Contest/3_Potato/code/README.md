# Potato — code

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline/   the reference solution given to contestants, plus any helper code
  grading/    the grader used to score submissions
```

The **data is not in this repository** — it is published separately on Hugging Face:

- public data (given to contestants): <https://huggingface.co/IOAI-official/IOAI-2026/potato/public>
- private data (used for grading): <https://huggingface.co/IOAI-official/IOAI-2026/potato/private>

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline loads the public word embeddings and repeatedly proposes the unused word most similar to the current winner.

```bash
cd baseline
jupyter lab solution.ipynb
```

`local_test.py` scores a solution offline: `python local_test.py solution.ipynb`. It uses the public embeddings, so its score only approximates the official one.

This task speaks a line-by-line JSON protocol on stdin/stdout. Keep debug prints on **stderr** — anything on stdout is read as a protocol message. Override the data location with `POTATO_DATA_DIR`.

## Scoring a solution

`grading/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
