# Double Agent Dilemma — code

Everything needed to develop a solution to this task and to score it the way the contest did.

```
code/
  baseline/   the reference solution given to contestants, plus any helper code
  grading/    the grader used to score submissions
```

The **data is not in this repository** — it is published separately on Hugging Face:

- public data (given to contestants): <https://huggingface.co/IOAI-official/IOAI-2026/double-agent-dilemma/public>
- private data (used for grading): <https://huggingface.co/IOAI-official/IOAI-2026/double-agent-dilemma/private>

Download it and place it so the notebook can find it (see the note below), then open the baseline.

## Running the baseline

The baseline is the longest of the six and walks through loading both classifiers, comparing their predictions, and assembling a submission.

```bash
cd baseline
jupyter lab solution.ipynb
```

Needs `torch`, `torchvision` and `timm`, plus the two pretrained models. Paths are set by the `DATA_DIR`, `MODELS_DIR`, `TRAIN_SPLIT` and `TEST_SPLIT` environment variables.

## Scoring a solution

`grading/` holds the grader used during the contest. It reads a solution plus the private data and prints a score. The grader's own README documents how it is invoked and what it expects; it was built to run inside a prepared container image, so running it locally takes some setup.

## A note on the baselines

These are deliberately simple — several score close to zero. They are starting points that show the input and output format correctly, not strong solutions. Improving on them is the exercise.
