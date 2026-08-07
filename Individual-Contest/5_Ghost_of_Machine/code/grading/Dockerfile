# Job image for Ghost of the Machine.
#
# Bakes the dataset and the bge model bundle into the image the CI job runs in,
# so a submission no longer pays `git lfs pull` for 419 MB of weights on every
# grade. check.py reads them from $DATASET_ROOT / $MODELS_ROOT (/problem/...).
#
# Build + push (the tag must match `image:` in .gitlab-ci.yml, and a tag is never
# reused -- runners cache by tag and will not re-download one they already have):
#
#   REG=contest.gitlab.yandexcloud.net:5050/problems/9945797-2026-05-21-l7mbvhtwra/ml/ci-template
#   docker build --platform linux/amd64 -t $REG:<YYYYMMDD> .
#   docker push $REG:<YYYYMMDD>
#
# --platform linux/amd64 matters when building on an Apple-silicon Mac: the
# runners are x86, and an arm64 image will fail to start there.
FROM cr.yandex/crphb5jkfgvtue082qcp/runner-job-image:gpu

COPY models /problem/models
COPY dataset /problem/dataset
