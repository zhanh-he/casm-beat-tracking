#!/usr/bin/env bash
set -euo pipefail

# The MIREX 2026 rules prohibit SMC/GTZAN for any development purpose. This
# runner is retained only for exact reproduction of pre-rule historical work.
if [[ "${HISTORICAL_TARGET_REBUILD:-}" != "yes" ]]; then
  echo "disabled for MIREX 2026: SMC/GTZAN may not be used for development; set HISTORICAL_TARGET_REBUILD=yes only for retrospective reproduction" >&2
  exit 2
fi

EVAL_PROJECT=${EVAL_PROJECT:-/media/mengh/SharedData/zhanh/auto_structbeat}
TRAIN_PROJECT=${TRAIN_PROJECT:-/media/mengh/SharedData/zhanh/auto_beatthis_mscnn}
PYTHON=${PYTHON:-/home/mengh/miniconda3/envs/auto-structbeat/bin/python}
FULL_DATA=${FULL_DATA:-/home/mengh/AIWorker/auto_beatthis_mscnn_data/data}
NO_SMC_VIEW=${NO_SMC_VIEW:-/home/mengh/AIWorker/auto_beatthis_mscnn_data_no_smc_20260929/data}
CASM_NO_SMC=${CASM_NO_SMC:-/storage/zhanh_storage/auto_structbeat_runs/beatthis_nosmc_single_seed0_e100_20260929T085029/evaluation/selection/casm_no_smc_frozen.json}
EVALUATION_ROOT=${EVALUATION_ROOT:?Set EVALUATION_ROOT}
MODELS_TSV=${MODELS_TSV:?Set MODELS_TSV}
REPORT_SCRIPT=${REPORT_SCRIPT:?Set REPORT_SCRIPT}
POLICY_SCRIPT=${POLICY_SCRIPT:-$(dirname "$REPORT_SCRIPT")/evaluation_policy.py}
REQUIRED_FREEZE=${REQUIRED_FREEZE:-}

if [[ -n "$REQUIRED_FREEZE" && ! -f "$REQUIRED_FREEZE" ]]; then
  echo "required pre-target freeze marker is missing: $REQUIRED_FREEZE" >&2
  exit 2
fi
for required in "$MODELS_TSV" "$REPORT_SCRIPT" "$POLICY_SCRIPT" "$CASM_NO_SMC"; do
  [[ -f "$required" ]] || { echo "missing required file: $required" >&2; exit 3; }
done
eligibility="$($PYTHON "$POLICY_SCRIPT" --models "$MODELS_TSV")"
if [[ -f "$EVALUATION_ROOT/COMPLETE" ]]; then
  "$PYTHON" "$REPORT_SCRIPT" --evaluation-root "$EVALUATION_ROOT" \
    --models "$MODELS_TSV" --casm-config "$CASM_NO_SMC" >/dev/null
  echo "target comparison already complete and eligibility-checked: $EVALUATION_ROOT"
  exit 0
fi
[[ ! -e "$NO_SMC_VIEW/annotations/smc" ]] || {
  echo "SMC leaked into no-SMC data view" >&2
  exit 4
}

mkdir -p "$EVALUATION_ROOT"/{cache,raw,logs,manifest,final,data_smc_only/annotations,data_smc_only/audio/spectrograms}
ln -sfn "$FULL_DATA/annotations/smc" "$EVALUATION_ROOT/data_smc_only/annotations/smc"
ln -sfn "$FULL_DATA/audio/spectrograms/smc.npz" "$EVALUATION_ROOT/data_smc_only/audio/spectrograms/smc.npz"

export PYTHONPATH="$EVAL_PROJECT:$TRAIN_PROJECT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

cp "$MODELS_TSV" "$EVALUATION_ROOT/manifest/models.frozen.tsv"
sha256sum "$EVALUATION_ROOT/manifest/models.frozen.tsv" "$CASM_NO_SMC" \
  "$EVAL_PROJECT/scripts/cache_logits.py" "$EVAL_PROJECT/scripts/evaluate_cache.py" \
  "$REPORT_SCRIPT" "$POLICY_SCRIPT" "$0" \
  > "$EVALUATION_ROOT/manifest/protocol_sha256.txt"
date -Is > "$EVALUATION_ROOT/TARGET_SCOPE_FROZEN"

casm_parameters="$($PYTHON - "$CASM_NO_SMC" <<'PY'
import json, sys
print(json.dumps(json.load(open(sys.argv[1]))["decoder_parameters"], separators=(",", ":")))
PY
)"

tail -n +2 "$MODELS_TSV" | while IFS=$'\t' read -r model_id checkpoint smc_training_status; do
  [[ -n "$model_id" && -f "$checkpoint" ]] || {
    echo "invalid model row: $model_id $checkpoint" >&2
    exit 5
  }
  cache_root="$EVALUATION_ROOT/cache/$model_id"
  mkdir -p "$cache_root" "$EVALUATION_ROOT/raw/$model_id"
  mapfile -t datasets < <(printf '%s\n' "$eligibility" | awk -F '\t' -v id="$model_id" '$1 == id {print $2}')
  [[ "${#datasets[@]}" -gt 0 ]] || { echo "no eligible dataset for $model_id" >&2; exit 6; }
  cache_args=()
  for dataset in "${datasets[@]}"; do
    mkdir -p "$cache_root/$dataset"
    case "$dataset" in
      smc)
        data_dir="$EVALUATION_ROOT/data_smc_only"
        datasplit=train
        expected=217
        ;;
      gtzan)
        data_dir="$NO_SMC_VIEW"
        datasplit=test
        expected=993
        ;;
      *) echo "unapproved evaluation dataset: $dataset" >&2; exit 6 ;;
    esac
    "$PYTHON" "$EVAL_PROJECT/scripts/cache_logits.py" \
      --checkpoint "$checkpoint" --data-dir "$data_dir" \
      --datasplit "$datasplit" --output-dir "$cache_root/$dataset" \
      --gpu 0 --num-workers 4 \
      > "$EVALUATION_ROOT/logs/$model_id.$dataset.cache.log" 2>&1
    count=$(find "$cache_root/$dataset" -maxdepth 1 -type f -name '*.npz' | wc -l)
    [[ "$count" -eq "$expected" ]] || {
      echo "cache count mismatch model=$model_id dataset=$dataset count=$count" >&2
      exit 6
    }
    cache_args+=(--cache-dir "$cache_root/$dataset")
  done

  for specification in \
    'direct|minimal|{}' \
    "casm_no_smc|asm|$casm_parameters" \
    'dbn_default|dbn|{}' \
    'dbn_30_300|dbn|{"min_bpm":30.0,"max_bpm":300.0}'; do
    IFS='|' read -r name decoder parameters <<< "$specification"
    "$PYTHON" "$EVAL_PROJECT/scripts/evaluate_cache.py" \
      "${cache_args[@]}" \
      --decoder "$decoder" --decoder-params "$parameters" --workers 8 \
      --output-prefix "$EVALUATION_ROOT/raw/$model_id/$name" \
      > "$EVALUATION_ROOT/logs/$model_id.$name.log" 2>&1
  done
  touch "$cache_root/COMPLETE"
done

"$PYTHON" "$REPORT_SCRIPT" --evaluation-root "$EVALUATION_ROOT" \
  --models "$MODELS_TSV" --casm-config "$CASM_NO_SMC"
find "$EVALUATION_ROOT/cache" -type f -name '*.npz' -print0 \
  | sort -z | xargs -0 sha256sum > "$EVALUATION_ROOT/manifest/cache_sha256.txt"
find "$EVALUATION_ROOT/raw" "$EVALUATION_ROOT/final" \
  -type f \( -name '*.csv' -o -name '*.json' \) -print0 \
  | sort -z | xargs -0 sha256sum > "$EVALUATION_ROOT/manifest/results_sha256.txt"
date -Is > "$EVALUATION_ROOT/COMPLETE"
echo "target_comparison_complete root=$EVALUATION_ROOT"
