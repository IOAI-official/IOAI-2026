# Job image for Potato Contact = runner base + the offline embedding models baked in
# + the grader's own Python dependencies.
#
# The weights are NOT in this repository (models/ is gitignored) -- committing 3.3 GB
# through LFS is what this image replaces. Before building, place the two model
# directories under ./models:
#
#   models/Qwen/Qwen3-Embedding-0.6B/
#   models/BAAI/bge-m3/
#
# The layout under ./models must match the paths printed in statement.md section 6,
# because the same bundle is what participants receive; the container mounts it at
# /models and the statement's example loads "models/<vendor>/<name>".
#
# Build and push (never reuse a tag -- CI caches by tag):
#
#   REG=contest.gitlab.yandexcloud.net:5050/problems/9945797-2026-06-03-98m1xdyeso/ml/ci-template
#   docker build -t "$REG/potato-job:20260801" .
#   docker push  "$REG/potato-job:20260801"
#   # then point `image:` in .gitlab-ci.yml at the new tag
#
# Full procedure, including where to source the weights: see RUNBOOK.md.
FROM cr.yandex/crphb5jkfgvtue082qcp/runner-job-image:gpu

# Grader-side dependencies only (numpy + nbconvert). The participant's libraries
# live in RUNTIME_IMAGE, not here -- the grader itself never loads a model.
#
# The base image ships a PEP 668 "externally managed" Python (3.14) with none of
# these present, so the install needs --break-system-packages. That is safe here:
# this image exists only to run the grader, and nothing else shares its Python.
COPY requirements.txt /problem/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages \
        -r /problem/requirements.txt \
    && python3 -c "import numpy, nbconvert" \
    && jupyter --version

# Offline model bundle, mounted read-only into the participant container at /models.
COPY models /problem/models
