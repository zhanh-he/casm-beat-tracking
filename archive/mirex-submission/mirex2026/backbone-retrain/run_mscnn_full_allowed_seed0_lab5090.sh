#!/usr/bin/env bash
# Full-allowed MSCNN retrain for the lab RTX 5090. This mirrors the frozen
# Kaya recipe but runs without a batch scheduler.

set -euo pipefail

PROJECT=${PROJECT:-/media/mengh/SharedData/zhanh/auto_beatthis_mscnn}
DATA_VIEW=${DATA_VIEW:-/home/mengh/AIWorker/auto_beatthis_mscnn_data_no_smc_20260929/data}
PYTHON=${PYTHON:-/home/mengh/miniconda3/envs/auto-beatthis-mscnn/bin/python}
OUTPUT_DIR=${OUTPUT_DIR:-/storage/zhanh_storage/auto_structbeat_runs/mirex_no_smc_20261005/mscnn_full_allowed_seed0_e1500_5090}
CHECKPOINT_DIR="${OUTPUT_DIR}/checkpoints"
export PYTHONPATH="${PROJECT}${PYTHONPATH:+:${PYTHONPATH}}"
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}

[[ -x "${PYTHON}" ]] || { echo "Missing Python: ${PYTHON}" >&2; exit 1; }
[[ -d "${PROJECT}" ]] || { echo "Missing Beat This project: ${PROJECT}" >&2; exit 1; }
[[ -d "${DATA_VIEW}" ]] || { echo "Missing no-SMC view: ${DATA_VIEW}" >&2; exit 1; }
[[ ! -e "${DATA_VIEW}/annotations/smc" ]] || {
  echo "FATAL: SMC is present in the training view" >&2
  exit 1
}

mkdir -p "${CHECKPOINT_DIR}"
[[ ! -f "${OUTPUT_DIR}/TRAINING_COMPLETE" ]] || exit 0

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

cd "${PROJECT}"
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

[[ -f "${CHECKPOINT_DIR}/last.ckpt" ]] || {
  echo "Missing final checkpoint" >&2
  exit 1
}
sha256sum "${CHECKPOINT_DIR}"/*.ckpt > "${OUTPUT_DIR}/SHA256SUMS"
date --iso-8601=seconds > "${OUTPUT_DIR}/TRAINING_COMPLETE"
