#!/usr/bin/env bash
#SBATCH --job-name=casm-7f-release
#SBATCH --account=ems011
#SBATCH --partition=work
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=/group/ems011/zhe/auto_structbeat_results/slurm/casm-7f-release-%j.out
#SBATCH --error=/group/ems011/zhe/auto_structbeat_results/slurm/casm-7f-release-%j.err

set -euo pipefail
shopt -s nullglob

module purge
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASM_PYTHON="${MYGROUP}/envs/auto-structbeat-rocm/bin/python"
EVALUATE="${REPO_ROOT}/experiments/evaluate_activations.py"
CONFIG="${REPO_ROOT}/config/casm-7f-default.json"
CACHE_ROOT="${MYSCRATCH}/auto_structbeat_runs/caches"
TCN_CACHE_ROOT="${MYSCRATCH}/auto_structbeat_runs/tcn_beatthis_protocol/caches/tcn_beatthis_protocol"
OUTPUT_ROOT="${MYGROUP}/auto_structbeat_results/casm_7f_release_20260921"

mkdir -p "${OUTPUT_ROOT}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

evaluate() {
  local output_prefix="$1"
  shift
  PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}" \
  "${CASM_PYTHON}" "${EVALUATE}" \
    "$@" \
    --config "${CONFIG}" \
    --output-prefix "${OUTPUT_ROOT}/${output_prefix}"
}

all_caches_present() {
  local cache_dir
  for cache_dir in "$@"; do
    compgen -G "${cache_dir}/*.npz" > /dev/null || return 1
  done
}

beat_this_folds=()
tcn_folds=()
mscnn_folds=()
beat_this_fold_dirs=()
tcn_fold_dirs=()
mscnn_fold_dirs=()
for fold in {0..7}; do
  beat_this_dir="${CACHE_ROOT}/beat_this_official/fold${fold}_val"
  tcn_dir="${TCN_CACHE_ROOT}/fold${fold}_val"
  beat_this_fold_dirs+=("${beat_this_dir}")
  tcn_fold_dirs+=("${tcn_dir}")
  beat_this_folds+=(--cache-dir "${beat_this_dir}")
  tcn_folds+=(--cache-dir "${tcn_dir}")
  if (( fold < 4 )); then
    mscnn_dir="${CACHE_ROOT}/mscnn_partial_20260812/4fold_best/fold${fold}_val"
  else
    mscnn_dir="${CACHE_ROOT}/mscnn_best/fold${fold}_val"
  fi
  mscnn_fold_dirs+=("${mscnn_dir}")
  mscnn_folds+=(--cache-dir "${mscnn_dir}")
done

missing_file="${OUTPUT_ROOT}/MISSING_CACHES.txt"
: > "${missing_file}"
if all_caches_present "${beat_this_fold_dirs[@]}"; then
  evaluate beat_this_8fold_7f "${beat_this_folds[@]}"
else
  printf 'BeatThis 8-fold caches incomplete\n' >> "${missing_file}"
fi
if all_caches_present "${mscnn_fold_dirs[@]}"; then
  evaluate mscnn_8fold_7f "${mscnn_folds[@]}"
else
  printf 'MSCNN 8-fold caches incomplete\n' >> "${missing_file}"
fi
if all_caches_present "${tcn_fold_dirs[@]}"; then
  evaluate tcn_8fold_7f "${tcn_folds[@]}"
else
  printf 'TCN 8-fold caches incomplete\n' >> "${missing_file}"
fi

for seed in {0..2}; do
  beat_this_gtzan="${CACHE_ROOT}/beat_this_official/final${seed}_gtzan"
  mscnn_gtzan="${CACHE_ROOT}/mscnn_partial_20260812/gtzan/final${seed}"
  tcn_gtzan="${TCN_CACHE_ROOT}/final${seed}_gtzan"
  if all_caches_present "${beat_this_gtzan}"; then
    evaluate "beat_this_gtzan_final${seed}_7f" --cache-dir "${beat_this_gtzan}"
  else
    printf 'BeatThis GTZAN final%s cache missing\n' "${seed}" >> "${missing_file}"
  fi
  if all_caches_present "${mscnn_gtzan}"; then
    evaluate "mscnn_gtzan_final${seed}_7f" --cache-dir "${mscnn_gtzan}"
  else
    printf 'MSCNN GTZAN final%s cache missing\n' "${seed}" >> "${missing_file}"
  fi
  if all_caches_present "${tcn_gtzan}"; then
    evaluate "tcn_gtzan_final${seed}_7f" --cache-dir "${tcn_gtzan}"
  else
    printf 'TCN GTZAN final%s cache missing\n' "${seed}" >> "${missing_file}"
  fi
done

checksum_tmp="${OUTPUT_ROOT}/SHA256SUMS.part"
: > "${checksum_tmp}"
result_files=("${OUTPUT_ROOT}"/*.json "${OUTPUT_ROOT}"/*.csv)
for result in "${result_files[@]}"; do
  sha256sum "${result}" >> "${checksum_tmp}"
done
mv "${checksum_tmp}" "${OUTPUT_ROOT}/SHA256SUMS"
if [[ -s "${missing_file}" ]]; then
  date --iso-8601=seconds > "${OUTPUT_ROOT}/PARTIAL"
  printf 'Release refresh incomplete; see %s\n' "${missing_file}" >&2
  exit 2
fi
rm "${missing_file}"
date --iso-8601=seconds > "${OUTPUT_ROOT}/COMPLETE"
