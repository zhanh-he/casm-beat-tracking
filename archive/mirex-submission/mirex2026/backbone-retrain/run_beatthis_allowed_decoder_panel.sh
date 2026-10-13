#!/usr/bin/env bash
# Decoder comparison for the frozen search checkpoint on allowed validation.
set -euo pipefail

root=/storage/zhanh_storage/auto_structbeat_runs/beatthis_expanded_search_20260929T1200
candidate=epoch_0119_2f56b23a
cache="$root/allowed_search/cache/$candidate/allowed_val"
output="$root/allowed_decoder_panel_20261004"
project=/media/mengh/SharedData/zhanh/auto_structbeat
beatthis=/media/mengh/SharedData/zhanh/auto_beatthis_mscnn
python=/home/mengh/miniconda3/envs/auto-structbeat/bin/python
config="$output/casm-no-smc.json"

[[ "$(find "$cache" -maxdepth 1 -name '*.npz' | wc -l)" -eq 556 ]] || {
  echo 'allowed-validation cache does not have 556 pieces' >&2; exit 2;
}
export PYTHONPATH="$project:$beatthis${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$output"
casm_params="$($python -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))["selection"]["decoder_parameters"],separators=(",",":")))' "$config")"
for method in direct casm_no_smc dbn_55_215 dbn_30_300; do
  case "$method" in
    direct) decoder=minimal; params='{}' ;;
    casm_no_smc) decoder=asm; params="$casm_params" ;;
    dbn_55_215) decoder=dbn; params='{}' ;;
    dbn_30_300) decoder=dbn; params='{"min_bpm":30.0,"max_bpm":300.0}' ;;
  esac
  "$python" "$project/scripts/evaluate_cache.py" \
    --cache-dir "$cache" --decoder "$decoder" --decoder-params "$params" \
    --workers 6 --output-prefix "$output/$method" \
    > "$output/$method.log" 2>&1
  echo "$method complete $(date -Is)"
done
date -Is > "$output/COMPLETE"
