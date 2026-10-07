#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT}/third_party/beat_this:${ROOT}/../casm/src${PYTHONPATH:+:${PYTHONPATH}}"
if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="${PYTHON}"
elif [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT}/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi
exec "${PYTHON_BIN}" "${ROOT}/run_pipeline.py" "$@"
