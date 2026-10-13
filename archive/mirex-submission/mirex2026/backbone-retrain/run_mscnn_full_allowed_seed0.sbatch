#!/usr/bin/env bash
#SBATCH --job-name=mscnn-full-allowed
#SBATCH --account=ems011
#SBATCH --partition=amdgpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --gres=gpu:mi210:1
#SBATCH --time=18:00:00
#SBATCH --output=/group/ems011/zhe/auto_structbeat_results/slurm/mscnn-full-allowed-%j.out
#SBATCH --error=/group/ems011/zhe/auto_structbeat_results/slurm/mscnn-full-allowed-%j.err

set -euo pipefail

module purge
ROCM_ROOT=/opt/rocm-6.4.2
export PATH="${ROCM_ROOT}/bin:${PATH}"
export LD_LIBRARY_PATH="${ROCM_ROOT}/lib:${ROCM_ROOT}/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

source "${MYGROUP}/auto_structbeat/kaya/common.sh"
ENV_PREFIX="${MYGROUP}/envs/auto-structbeat-rocm"
PYTHON="${ENV_PREFIX}/bin/python"
DATA_VIEW="${DATA_ROOT}/views/no_smc_20260929/data"
OUTPUT_DIR="${RUN_ROOT}/mirex_no_smc_20261005/mscnn_full_allowed_seed0_e1500"
CHECKPOINT_DIR="${OUTPUT_DIR}/checkpoints"
export PYTHONPATH="${PROJECT_ROOT}:${BEAT_THIS_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
export MIOPEN_USER_DB_PATH="${OUTPUT_DIR}/miopen/user_db"
export MIOPEN_CUSTOM_CACHE_DIR="${OUTPUT_DIR}/miopen/kernel_cache"

require_path "${ENV_PREFIX}/ENVIRONMENT_READY" "validated ROCm environment"
require_path "${DATA_ROOT}/state/DATA_READY" "verified Beat This data marker"
require_path "${DATA_VIEW}" "no-SMC training view"
[[ ! -e "${DATA_VIEW}/annotations/smc" ]] || {
  echo "FATAL: SMC is present in the training view" >&2
  exit 1
}

mkdir -p "${CHECKPOINT_DIR}" "${MIOPEN_USER_DB_PATH}" "${MIOPEN_CUSTOM_CACHE_DIR}"
[[ ! -f "${OUTPUT_DIR}/TRAINING_COMPLETE" ]] || exit 0

# Audit the effective loader, not just directory names. GTZAN remains visible
# to Beat This as its test set but must never enter train_items. The raw allowed
# split has 4,340 rows; one empty Beatles annotation is rejected by the loader,
# leaving the expected 4,339 effective training pieces.
DATA_VIEW="${DATA_VIEW}" "${PYTHON}" - <<'PY'
import os
from pathlib import Path

from beat_this.dataset.dataset import BeatDataModule

data = BeatDataModule(
    Path(os.environ["DATA_VIEW"]),
    batch_size=12,
    num_workers=0,
    no_val=True,
    test_dataset="gtzan",
)
data.setup("fit")
forbidden = [
    item for item in data.train_items
    if item.startswith(("smc/", "gtzan/"))
]
assert not forbidden, f"forbidden target items entered training: {forbidden[:5]}"
assert len(data.train_items) == 4340, len(data.train_items)
assert len(data.train_dataset) == 4339, len(data.train_dataset)
print("TRAINING_VIEW_AUDIT_OK: 4339 allowed pieces; SMC=0; GTZAN=0")
PY

resume_args=()
if [[ -f "${CHECKPOINT_DIR}/last.ckpt" ]]; then
  resume_args=(--resume-checkpoint "${CHECKPOINT_DIR}/last.ckpt")
else
  mapfile -t existing < <(
    find "${CHECKPOINT_DIR}" -maxdepth 1 -type f -name '*.ckpt' -printf '%T@ %p\n' | sort -nr
  )
  if [[ ${#existing[@]} -gt 0 ]]; then
    resume_args=(--resume-checkpoint "${existing[0]#* }")
  fi
fi

cd "${BEAT_THIS_ROOT}"
"${PYTHON}" launch_scripts/train.py \
  --name mirex_no_smc_mscnn_full_allowed_seed0 \
  --architecture multiscale_cnn \
  --data-dir "${DATA_VIEW}" \
  --checkpoint-dir "${CHECKPOINT_DIR}" \
  --train-length-seconds 30 \
  --no-val \
  --multiscale-channels 128 \
  --multiscale-layers 8 \
  --multiscale-kernel-sizes 3 5 9 17 \
  --multiscale-dilation-cycle 1 2 4 8 \
  --batch-size 12 \
  --accumulate-grad-batches 8 \
  --num-workers 8 \
  --max-epochs 1500 \
  --val-frequency 25 \
  --num-sanity-val-steps 0 \
  --checkpoint-every-n-epochs 100 \
  --checkpoint-save-top-k 0 \
  --optimizer adamw \
  --lr 0.0008 \
  --weight-decay 0.01 \
  --warmup-steps 1000 \
  --compile \
  --logger none \
  --seed 0 \
  "${resume_args[@]}" 2>&1 | tee -a "${OUTPUT_DIR}/train.log"

require_path "${CHECKPOINT_DIR}/last.ckpt" "final MSCNN checkpoint"
sha256sum "${CHECKPOINT_DIR}"/*.ckpt > "${OUTPUT_DIR}/SHA256SUMS"
date --iso-8601=seconds > "${OUTPUT_DIR}/TRAINING_COMPLETE"
