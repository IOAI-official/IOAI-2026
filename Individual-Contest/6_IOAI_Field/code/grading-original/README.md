# ci-template — IOAI Field grader

Private GitLab/Yandex Contest grader for student `solution.ipynb` submissions
with an optional `custom_model.py` module.

## Grading contract

The API-triggered `test` job downloads the submitted notebook and optional
`custom_model.py`, then runs `python3 check.py` on the default git+podman runner:

1. **Validate and preflight** — require a notebook no larger than 1 MiB, validate
   `custom_model.py` when present, and require CUDA plus CPython 3.13 inside the
   pinned IOAI runtime image.
2. **Training prerun** — copy the pristine notebook and custom model module into
   a disposable workspace, mount `data/train_config` read-only at
   `/work/data/train_config`, execute the notebook without network access, and
   validate its `model.pt` with the real scorer. A participant error writes a
   zero-score `report.json`, attaches a bounded, sanitized `ERROR` artifact, and
   stops before hidden testing.
3. **Hidden test** — discard the complete prerun workspace and copy the pristine
   inputs into a new one. Mount `data/$GRADE_SPLIT` at the same
   `/work/data/train_config` path, execute again, and score only this model.
4. **Publish** — `send_report` publishes structured participant results;
   grader/infrastructure failures reach `send_crash` and publish `Crash`.

Both notebook phases run in podman with `--network=none`, GPU access, a writable
temporary filesystem, and grader-owned read-only mounts for `core/`, `problem.py`,
`metrics/`, `_dist-linux-py313/`, and the phase's selected configuration.

The notebook must call `torch.save(model, "model.pt")`. It may save one
`torch.nn.Module`, or a list with one module per field config. Leaderboard A has
one config; leaderboard B has multiple configs and averages their scores.

## Custom model classes

A repository submission may include one `custom_model.py` file. It may contain:

- Imports from `torch` or `torch.*` only.
- An optional module docstring.
- One or more model class definitions.

Other imports, relative imports, executable top-level statements, symlinks,
invalid Python/UTF-8, and files larger than 1 MiB are rejected.

Example `custom_model.py`:

```python
import torch.nn as nn


class CustomModel(nn.Module):
    def __init__(self, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x):
        return self.net(x)
```

The notebook must import the class before constructing it:

```python
from custom_model import CustomModel

model = CustomModel(...)
# train model
torch.save(model.cpu(), "model.pt")
```

Do not redefine the class in the notebook: that records it as
`__main__.CustomModel`, which cannot be resolved by the separate scorer process.
File-only submissions may generate `custom_model.py` before importing the class.

## Outputs

- `report.json` — contest verdict and a CALCULATOR result whose JSON-encoded
  `message` is `{"a": score}` for leaderboard A or `{"b": score}` for
  leaderboard B, plus an `ERROR` artifact reference when a participant-facing
  diagnostic is available.
- `artifacts/field_score-error.txt` — bounded, sanitized failure diagnostic.
- `prerun_executed.ipynb`, `prerun_stdout.log`, `prerun_stderr.log` — diagnostic
  phase artifacts.
- `executed.ipynb`, `executed_stdout.log`, `executed_stderr.log` — hidden phase
  artifacts.

## Important files

- `.gitlab-ci.yml` — runtime image, phase budgets, hidden split, artifacts, and
  report-publishing jobs.
- `check.py` — validation, isolation, podman execution, gating, and reporting.
- `score_model.py` — grader-owned in-container model loader/scorer.
- `metrics/field_score.py` — canonical metric implementation.
- `data/train_config/` — public diagnostic configuration.
- `data/leaderboard_a_config/`, `data/leaderboard_b_config/` — hidden configs.
- `_dist-linux-py313/` — protected Linux x86_64 CPython 3.13 field runtime.

The protected runtime only imports under the matching Python ABI. To use another
Python version, rebuild and ship the corresponding `_dist-linux-py<version>`
artifact.
