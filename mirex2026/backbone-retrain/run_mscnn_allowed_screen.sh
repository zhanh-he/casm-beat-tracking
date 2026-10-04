#!/usr/bin/env bash
# Four predeclared seed-0 MSCNN candidates; allowed validation only.
set -euo pipefail

root=/storage/zhanh_storage/auto_structbeat_runs/mscnn_mirex_allowed_screen_20261004
project=/media/mengh/SharedData/zhanh/auto_structbeat
beatthis=/media/mengh/SharedData/zhanh/auto_beatthis_mscnn
data=/home/mengh/AIWorker/auto_beatthis_mscnn_data_no_smc_20260929/data
python=/home/mengh/miniconda3/envs/auto-structbeat/bin/python
config="$root/casm-no-smc.json"

[[ ! -e "$data/annotations/smc" ]] || {
  echo 'SMC leaked into the no-SMC data view' >&2
  exit 2
}
[[ -f "$config" ]] || { echo "missing frozen CASM configuration: $config" >&2; exit 2; }
export PYTHONPATH="$project:$beatthis${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

casm_params="$($python -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))["selection"]["decoder_parameters"],separators=(",",":")))' "$config")"
for entry in \
  'best_0119|mirex_no_smc_mscnn_lite_single-best-0119-0.6027.ckpt' \
  'best_0139|mirex_no_smc_mscnn_lite_single-best-0139-0.6081.ckpt' \
  'best_0154|mirex_no_smc_mscnn_lite_single-best-0154-0.6068.ckpt' \
  'last_1499|mirex_no_smc_mscnn_lite_single-epoch1499.ckpt'; do
  IFS='|' read -r name filename <<< "$entry"
  checkpoint="$root/checkpoints/$filename"
  cache="$root/cache/$name"
  [[ -f "$checkpoint" ]] || { echo "missing checkpoint: $checkpoint" >&2; exit 3; }
  mkdir -p "$cache" "$root/results/$name" "$root/logs"
  if [[ ! -f "$cache/COMPLETE" ]]; then
    "$python" "$project/scripts/cache_logits.py" \
      --checkpoint "$checkpoint" --data-dir "$data" --datasplit val \
      --output-dir "$cache" --gpu 0 --num-workers 4 \
      > "$root/logs/$name.cache.log" 2>&1
    count=$(find "$cache" -maxdepth 1 -type f -name '*.npz' | wc -l)
    [[ "$count" -eq 556 ]] || { echo "$name: expected 556 allowed pieces, got $count" >&2; exit 4; }
    if find "$cache" -maxdepth 1 -type f -name '*.npz' | grep -Eq '/(smc|gtzan)[._-]'; then
      echo "$name: forbidden target dataset in validation cache" >&2
      exit 5
    fi
    date -Is > "$cache/COMPLETE"
  fi
  for method in direct casm_no_smc dbn_55_215 dbn_30_300; do
    case "$method" in
      direct) decoder=minimal; params='{}' ;;
      casm_no_smc) decoder=asm; params="$casm_params" ;;
      dbn_55_215) decoder=dbn; params='{}' ;;
      dbn_30_300) decoder=dbn; params='{"min_bpm":30.0,"max_bpm":300.0}' ;;
    esac
    prefix="$root/results/$name/$method"
    [[ -f "$prefix.summary.json" ]] && continue
    "$python" "$project/scripts/evaluate_cache.py" \
      --cache-dir "$cache" --decoder "$decoder" --decoder-params "$params" \
      --workers 8 --output-prefix "$prefix" \
      > "$root/logs/$name.$method.log" 2>&1
  done
  echo "complete: $name $(date -Is)"
done
date -Is > "$root/COMPLETE"
