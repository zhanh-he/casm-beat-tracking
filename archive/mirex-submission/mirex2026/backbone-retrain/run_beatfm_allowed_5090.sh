#!/usr/bin/env bash
# Inference-only validation replica on lab5090; no training is performed here.
set -euo pipefail

root=/storage/zhanh_storage/auto_structbeat_runs/beatfm_allowed_5090_20261004
bundle=/storage/zhanh_storage/auto_structbeat_runs/mirex_submission_smoke_20261004/casm-mirex2026-three-backbone-provisional-20261004
panel="$root/allowed_validation_137_transfer_v1"
checkpoint="$root/checkpoints"
export PYTHONPATH="$root/protocol:$bundle:$bundle/third_party/beat_this:$bundle/vendor/casm/src:/home/mengh/research/beatfm_mirex_inference_20260930/python_deps${PYTHONPATH:+:$PYTHONPATH}"
export BEATFM_SOURCE_DIR="$bundle/third_party/beatfm_source"
export BEATFM_MERT_DIR="$bundle/third_party/mert_v1_95m"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4

/home/mengh/miniconda3/envs/auto-structbeat/bin/python "$root/protocol/evaluate_beatfm_allowed.py" \
  --manifest "$panel/source_manifest.tsv" \
  --relocated-validation "$panel/validation_relocated.tsv" \
  --source-dir "$BEATFM_SOURCE_DIR" \
  --mert-dir "$BEATFM_MERT_DIR" \
  --casm-config "$bundle/config/casm-no-smc.json" \
  --checkpoint best_val_loss="$checkpoint/best_val_loss.pt" \
  --checkpoint epoch_0005="$checkpoint/epoch_0005.pt" \
  --checkpoint epoch_0010="$checkpoint/epoch_0010.pt" \
  --checkpoint epoch_0015="$checkpoint/epoch_0015.pt" \
  --checkpoint epoch_0020="$checkpoint/epoch_0020.pt" \
  --output-dir "$root/allowed_eval_seed0_v2"
