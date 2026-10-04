#!/usr/bin/env bash
#SBATCH --job-name=beatfm-allowed-eval
#SBATCH --account=ems011
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100-32gb:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=1-00:00:00
#SBATCH --output=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-allowed-eval-%j.out
#SBATCH --error=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-allowed-eval-%j.err

set -euo pipefail

protocol=/group/ems011/zhe/beatfm_mirex_20260930/protocol
data=/scratch/ems011/zhe/beatfm_mirex_20260930/data
run=/scratch/ems011/zhe/beatfm_mirex_20260930/runs/verified_ballroom_rwc_seed0_v1
export PYTHONPATH="$protocol:/group/ems011/zhe/beatfm_mirex_20260930/python_deps${PYTHONPATH:+:$PYTHONPATH}"
export BEATFM_SOURCE_DIR=/group/ems011/zhe/beatfm_mirex_20260930/source/BeatFM
export BEATFM_MERT_DIR=/group/ems011/zhe/beatfm_mirex_20260930/MERT-v1-95M
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4

/group/ems011/zhe/envs/auto-structbeat/bin/python "$protocol/evaluate_beatfm_allowed.py" \
  --manifest "$data/verified_ballroom_rwc_911.tsv" \
  --source-dir "$BEATFM_SOURCE_DIR" \
  --mert-dir "$BEATFM_MERT_DIR" \
  --casm-config "$protocol/casm-no-smc.json" \
  --checkpoint best_val_loss="$run/best_val_loss.pt" \
  --checkpoint epoch_0005="$run/epoch_0005.pt" \
  --checkpoint epoch_0010="$run/epoch_0010.pt" \
  --checkpoint epoch_0015="$run/epoch_0015.pt" \
  --checkpoint epoch_0020="$run/epoch_0020.pt" \
  --output-dir /scratch/ems011/zhe/beatfm_mirex_20260930/runs/allowed_eval_seed0_v3
