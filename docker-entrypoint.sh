#!/usr/bin/env bash

set -Eeuo pipefail

if [ "${1:0:1}" = '-' ]; then
  set -- bicep-lint-sarif-fixer "$@"
fi

exec "$@"
