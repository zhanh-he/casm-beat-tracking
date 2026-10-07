#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ROOT}/third_party/beat_this:${ROOT}/vendor/casm/src${PYTHONPATH:+:${PYTHONPATH}}"
if [[ -d "${ROOT}/third_party/beatfm_source" && -d "${ROOT}/third_party/mert_v1_95m" ]]; then
  export BEATFM_SOURCE_DIR="${BEATFM_SOURCE_DIR:-${ROOT}/third_party/beatfm_source}"
  export BEATFM_MERT_DIR="${BEATFM_MERT_DIR:-${ROOT}/third_party/mert_v1_95m}"
fi
if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="${PYTHON}"
elif [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT}/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi
exec "${PYTHON_BIN}" "${ROOT}/run_pipeline.py" "$@"
