#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT}/third_party/beat_this:${ROOT}/vendor/casm/src${PYTHONPATH:+:${PYTHONPATH}}"
exec "${PYTHON:-python3}" "${ROOT}/run_pipeline.py" "$@"
