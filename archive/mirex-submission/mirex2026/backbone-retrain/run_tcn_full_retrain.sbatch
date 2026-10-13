#!/usr/bin/env bash
#SBATCH --job-name=tcn-full-allowed
#SBATCH --account=ems011
#SBATCH --partition=amdgpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:mi210:1
#SBATCH --time=06:00:00
#SBATCH --output=/group/ems011/zhe/auto_structbeat_results/slurm/tcn-full-allowed-%j.out
#SBATCH --error=/group/ems011/zhe/auto_structbeat_results/slurm/tcn-full-allowed-%j.err

set -euo pipefail
module purge
export PATH="/opt/rocm-6.4.2/bin:${PATH}"
export LD_LIBRARY_PATH="/opt/rocm-6.4.2/lib:/opt/rocm-6.4.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
source "${MYGROUP}/auto_structbeat/kaya/common.sh"
PYTHON="${MYGROUP}/envs/auto-structbeat-rocm/bin/python"
export PYTHONPATH="${PROJECT_ROOT}:${BEAT_THIS_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

CHOICE_ROOT="${RESULTS_ROOT}/mirex_no_smc_20261005/tcn_allowed_only"
DATA_VIEW="${DATA_ROOT}/views/no_smc_20260929/data"
OUTPUT_DIR="${RUN_ROOT}/mirex_no_smc_20261005/tcn_full_allowed_seed0"
[[ -f "${CHOICE_ROOT}/COMPLETE" ]]
[[ -f "${CHOICE_ROOT}/submission_choice.json" ]]
[[ -f "${CHOICE_ROOT}/checkpoint_manifest.csv" ]]
[[ ! -e "${OUTPUT_DIR}" ]] || { echo "Output exists; refusing overwrite: ${OUTPUT_DIR}" >&2; exit 1; }

epochs="$("${PYTHON}" -c 'import csv,json,sys; c=json.load(open(sys.argv[1])); rows=list(csv.DictReader(open(sys.argv[2]))); r=next(x for x in rows if x["candidate_id"]==c["candidate_id"]); e=r["epoch"]; print(int(e)+1 if e else 120)' "${CHOICE_ROOT}/submission_choice.json" "${CHOICE_ROOT}/checkpoint_manifest.csv")"
mkdir -p "${OUTPUT_DIR}"
export MIOPEN_USER_DB_PATH="${OUTPUT_DIR}/miopen/user_db"
export MIOPEN_CUSTOM_CACHE_DIR="${OUTPUT_DIR}/miopen/kernel_cache"
mkdir -p "${MIOPEN_USER_DB_PATH}" "${MIOPEN_CUSTOM_CACHE_DIR}"

"${PYTHON}" "${PROJECT_ROOT}/scripts/train_tcn_checkpointed.py" \
  --data-dir "${DATA_VIEW}" --output-dir "${OUTPUT_DIR}" \
  --training-profile beat_this --no-val --epochs "${epochs}" \
  --batch-size 8 --train-length-seconds 30 --num-workers 8 \
  --precision 32-true --checkpoint-save-top-k 0 \
  --checkpoint-every-n-epochs 0 --seed 0

[[ -f "${OUTPUT_DIR}/checkpoints/last.ckpt" ]]
sha256sum "${OUTPUT_DIR}/checkpoints/last.ckpt" > "${OUTPUT_DIR}/SHA256SUMS"
"${PYTHON}" -c 'import json,sys; from pathlib import Path; src=Path(sys.argv[1]); dst=Path(sys.argv[2]); data=json.loads(src.read_text()); data["full_retrain_epochs"]=int(sys.argv[3]); data["training_data"]="4339 allowed pieces; no SMC/GTZAN; no independent validation"; (dst/"frozen_source_choice.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")' "${CHOICE_ROOT}/submission_choice.json" "${OUTPUT_DIR}" "${epochs}"
date --iso-8601=seconds > "${OUTPUT_DIR}/TRAINING_COMPLETE"
