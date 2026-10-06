#!/usr/bin/env bash
#SBATCH --job-name=mscnn-full-cuda
#SBATCH --account=ems011
#SBATCH --partition=ondemand-gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=10:00:00
#SBATCH --output=/group/ems011/zhe/auto_structbeat_results/slurm/mscnn-full-cuda-%j.out
#SBATCH --error=/group/ems011/zhe/auto_structbeat_results/slurm/mscnn-full-cuda-%j.err

set -euo pipefail

module purge
source "${MYGROUP}/auto_structbeat/kaya/common.sh"
ENV_PREFIX="${MYGROUP}/envs/auto-structbeat"
PYTHON="${ENV_PREFIX}/bin/python"
DATA_VIEW="${DATA_ROOT}/views/no_smc_20260929/data"
OUTPUT_DIR="${RUN_ROOT}/mirex_no_smc_20261005/mscnn_full_allowed_seed0_e1500_cuda"
CHECKPOINT_DIR="${OUTPUT_DIR}/checkpoints"
export PYTHONPATH="${PROJECT_ROOT}:${BEAT_THIS_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
export BEAT_THIS_ROOT

require_path "${ENV_PREFIX}/ENVIRONMENT_READY" "validated CUDA environment"
require_path "${DATA_ROOT}/state/DATA_READY" "verified Beat This data marker"
require_path "${DATA_VIEW}" "no-SMC training view"
[[ ! -e "${DATA_VIEW}/annotations/smc" ]] || {
  echo "FATAL: SMC is present in the training view" >&2
  exit 1
}

mkdir -p "${CHECKPOINT_DIR}"
[[ ! -f "${OUTPUT_DIR}/TRAINING_COMPLETE" ]] || exit 0

# Resolve the actual data list before training. GTZAN is visible only as the
# Beat This test set and must be absent from train_items.
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

# Lightning/PyTorch 2.6 defaults to restricted checkpoint loading. This
# checkpoint was written by our own preceding segment in CHECKPOINT_DIR and
# must restore optimizer, scheduler, and RNG state to continue epoch 900.
if [[ ${#resume_args[@]} -gt 0 ]]; then
  export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
  sha256sum "${resume_args[1]}"
fi

cd "${BEAT_THIS_ROOT}"
"${PYTHON}" "${MYGROUP}/auto_structbeat/kaya/train_mscnn_without_target_test.py" \
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
