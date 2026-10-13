#!/usr/bin/env bash
set -uo pipefail

# Paper-faithful BeatThis `final0` recipe, with SMC removed from the data view.
# GTZAN remains the held-out test set. The only intentional differences from
# CPJKU final0 are the no-SMC data view and extra milestone checkpoints.

PROJECT=${PROJECT:-/media/mengh/SharedData/zhanh/auto_beatthis_mscnn}
DATA_VIEW=${DATA_VIEW:-/home/mengh/AIWorker/auto_beatthis_mscnn_data_no_smc_20260929/data}
RUN_ROOT=${RUN_ROOT:?Set RUN_ROOT to an empty output directory}
PYTHON=${PYTHON:-/home/mengh/miniconda3/envs/auto-beatthis-mscnn/bin/python}
LOG="$RUN_ROOT/production/train.log"

mkdir -p "$RUN_ROOT/production/checkpoints" "$RUN_ROOT/provenance"
cd "$PROJECT"

export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

{
  echo "production_start=$(date -Is)"
  echo "host=$(hostname)"
  echo "project=$PROJECT"
  echo "data_view=$DATA_VIEW"
  echo "run_root=$RUN_ROOT"
  echo "git_head=$(git rev-parse HEAD)"
  echo "protocol=CPJKU final0 --no-val, minus SMC; GTZAN held out"
  nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader
} | tee -a "$LOG"

git rev-parse HEAD > "$RUN_ROOT/provenance/git_head.txt"
git diff -- launch_scripts/train.py beat_this/model/pl_module.py \
  > "$RUN_ROOT/provenance/training_code.patch"
sha256sum launch_scripts/train.py beat_this/model/pl_module.py \
  > "$RUN_ROOT/provenance/training_code.sha256"

set +e
/usr/bin/time -v "$PYTHON" launch_scripts/train.py \
  --architecture beat_this \
  --data-dir "$DATA_VIEW" \
  --checkpoint-dir "$RUN_ROOT/production/checkpoints" \
  --name beatthis_final_nosmc_seed0_e100 \
  --no-val \
  --max-epochs 100 \
  --batch-size 8 \
  --accumulate-grad-batches 8 \
  --train-length 1500 \
  --num-workers 8 \
  --val-frequency 5 \
  --checkpoint-every-n-epochs 10 \
  --checkpoint-save-top-k 0 \
  --lr 0.0008 \
  --weight-decay 0.01 \
  --warmup-steps 1000 \
  --optimizer adamw \
  --loss shift_tolerant_weighted_bce \
  --tempo-augmentation \
  --pitch-augmentation \
  --mask-augmentation \
  --sum-head \
  --partial-transformers \
  --length-based-oversampling-factor 0.65 \
  --logger none \
  --seed 0 2>&1 | tee -a "$LOG"
status=${PIPESTATUS[0]}
set -e

printf '%s\n' "$status" > "$RUN_ROOT/production/exit_status.txt"
echo "production_end=$(date -Is) status=$status" | tee -a "$LOG"
if [[ "$status" -eq 0 ]]; then
  touch "$RUN_ROOT/production/TRAINING_COMPLETE"
fi
exit "$status"
