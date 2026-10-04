#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
VENV="${MIREX_VENV:-${ROOT}/.venv}"

"${PYTHON_BIN}" -m venv "${VENV}"
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -r "${ROOT}/requirements.txt"
"${VENV}/bin/python" -m pip install -r "${ROOT}/requirements-beatfm.txt"
"${VENV}/bin/python" -m pip install 'Cython==0.29.37'
"${VENV}/bin/python" -m pip install --no-build-isolation \
  -r "${ROOT}/requirements-dbn.txt"
printf 'Installed MIREX runtime at %s\n' "${VENV}"
printf 'Run with: PYTHON=%s/bin/python %s/run.sh %%input %%output\n' "${VENV}" "${ROOT}"
