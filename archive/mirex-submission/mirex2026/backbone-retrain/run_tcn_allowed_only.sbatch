#!/usr/bin/env bash
#SBATCH --job-name=tcn-allowed-only
#SBATCH --account=ems011
#SBATCH --partition=amdgpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --gres=gpu:mi210:1
#SBATCH --time=12:00:00
#SBATCH --output=/group/ems011/zhe/auto_structbeat_results/slurm/tcn-allowed-only-%j.out
#SBATCH --error=/group/ems011/zhe/auto_structbeat_results/slurm/tcn-allowed-only-%j.err

set -euo pipefail
module purge
export PATH="/opt/rocm-6.4.2/bin:${PATH}"
export LD_LIBRARY_PATH="/opt/rocm-6.4.2/lib:/opt/rocm-6.4.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
source "${MYGROUP}/auto_structbeat/kaya/common.sh"
PYTHON="${MYGROUP}/envs/auto-structbeat-rocm/bin/python"
export PYTHONPATH="${PROJECT_ROOT}:${BEAT_THIS_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

TRAIN_DIR="${RUN_ROOT}/mirex_no_smc_20260929/tcn_single"
RESULT_ROOT="${RESULTS_ROOT}/mirex_no_smc_20261005/tcn_allowed_only"
CACHE_ROOT="${RUN_ROOT}/mirex_no_smc_20261005/tcn_allowed_only/caches"
DATA_VIEW="${DATA_ROOT}/views/no_smc_20260929/data"
MANIFEST="${RESULT_ROOT}/checkpoint_manifest.csv"
CHOICE="${RESULT_ROOT}/submission_choice.json"
CASM_CONFIG="${PROJECT_ROOT}/mirex2026/config/casm-no-smc.json"

[[ -f "${TRAIN_DIR}/TRAINING_COMPLETE" ]]
[[ -f "${CASM_CONFIG}" ]]
mkdir -p "${RESULT_ROOT}" "${CACHE_ROOT}"
export MIOPEN_USER_DB_PATH="${RUN_ROOT}/mirex_no_smc_20261005/tcn_allowed_only/miopen/user_db"
export MIOPEN_CUSTOM_CACHE_DIR="${RUN_ROOT}/mirex_no_smc_20261005/tcn_allowed_only/miopen/kernel_cache"
mkdir -p "${MIOPEN_USER_DB_PATH}" "${MIOPEN_CUSTOM_CACHE_DIR}"

"${PYTHON}" "${PROJECT_ROOT}/scripts/build_checkpoint_manifest.py" \
  --checkpoint-dir "${TRAIN_DIR}/checkpoints" --output "${MANIFEST}" --state-dedup

while IFS=, read -r candidate source epoch val_loss checkpoint sha256 state_sha inference_id canonical; do
  canonical="${canonical%$'\r'}"
  [[ "${candidate}" == candidate_id ]] && continue
  [[ "${canonical}" == true ]] || continue
  cache="${CACHE_ROOT}/${inference_id}"
  "${PYTHON}" "${PROJECT_ROOT}/scripts/cache_logits_dataset.py" \
    --checkpoint "${checkpoint}" --data-dir "${DATA_VIEW}" \
    --datasplit val --output-dir "${cache}" --gpu 0 --num-workers 8
  "${PYTHON}" "${PROJECT_ROOT}/scripts/validate_cache_dir.py" \
    --cache-dir "${cache}" --checkpoint-sha256 "${sha256}" \
    --architecture tcn --expected-count 556
  "${PYTHON}" "${PROJECT_ROOT}/scripts/evaluate_cache.py" \
    --cache-dir "${cache}" --decoder minimal --decoder-params '{}' \
    --workers 16 --output-prefix "${RESULT_ROOT}/raw/${inference_id}/allowed_val/direct"
done < "${MANIFEST}"

"${PYTHON}" "${PROJECT_ROOT}/scripts/freeze_submission_choice.py" \
  --manifest "${MANIFEST}" --results-root "${RESULT_ROOT}/raw" \
  --output "${CHOICE}" --architecture tcn

selected="$("${PYTHON}" -c 'import json,sys; print(json.load(open(sys.argv[1]))["inference_candidate_id"])' "${CHOICE}")"
casm_params="$("${PYTHON}" -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))["parameters"],separators=(",",":")))' "${CASM_CONFIG}")"
for method in casm_no_smc dbn_55_215 dbn_30_300; do
  case "${method}" in
    casm_no_smc) decoder=asm; params="${casm_params}" ;;
    dbn_55_215) decoder=dbn; params='{}' ;;
    dbn_30_300) decoder=dbn; params='{"min_bpm":30.0,"max_bpm":300.0}' ;;
  esac
  "${PYTHON}" "${PROJECT_ROOT}/scripts/evaluate_cache.py" \
    --cache-dir "${CACHE_ROOT}/${selected}" --decoder "${decoder}" \
    --decoder-params "${params}" --workers 16 \
    --output-prefix "${RESULT_ROOT}/raw/${selected}/allowed_val/${method}"
done

"${PYTHON}" -c 'import json,sys; from pathlib import Path; p=Path(sys.argv[1]); c=json.loads((p/"submission_choice.json").read_text()); s=c["inference_candidate_id"]; print("selected",c["candidate_id"],c["checkpoint_sha256"]); [(lambda m,j: print(m,*(round(100*j["macro_piece"]["beat_"+k],2) for k in ("fmeasure","cmlt","amlt"))))(m,json.loads((p/"raw"/s/"allowed_val"/(m+".summary.json")).read_text())) for m in ("direct","casm_no_smc","dbn_55_215","dbn_30_300")]' "${RESULT_ROOT}" > "${RESULT_ROOT}/summary.txt"
date --iso-8601=seconds > "${RESULT_ROOT}/COMPLETE"
