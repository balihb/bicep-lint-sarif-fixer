FROM python:3.13.0-alpine3.20

COPY --chmod=755 src/bicep_lint_sarif_fixer.py /usr/local/bin/bicep-lint-sarif-fixer
