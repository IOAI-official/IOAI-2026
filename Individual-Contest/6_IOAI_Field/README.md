# IOAI Field — code & data

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline/   the reference solution given to contestants, plus any helper code
  grading/    the grader used to score submissions
```

The **data is not in this repository** — it is published as a standalone Hugging Face dataset:

- <https://huggingface.co/datasets/IOAI-official/ioai-2026-ioai-field>

The dataset has `public/` (what contestants received) and `private/` (the hidden leaderboard A/B configurations and held-out test) — its dataset card documents every subset.

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline trains a small network from scratch to reproduce the logo field, then saves it as `model.pt`.

```bash
cd code/baseline
PYTHONPATH=../grading jupyter lab solution.ipynb
```

`custom_model.py` holds the `CustomModel` class the notebook trains.

**The notebook imports `core`, which lives in `../grading/core`** — during the contest it was mounted read-only next to the notebook. Set `PYTHONPATH=../grading` (as above) or the import will fail. The model must stay under 20,260 parameters or the score is halved.

## Scoring a solution

`code/grading/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
