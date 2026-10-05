#!/usr/bin/env bash
#SBATCH --job-name=beatfm-expanded-eval
#SBATCH --account=ems011
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100-32gb:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=1-00:00:00
#SBATCH --output=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-expanded-eval-%j.out
#SBATCH --error=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-expanded-eval-%j.err

set -euo pipefail

protocol=/group/ems011/zhe/beatfm_mirex_20260930/protocol
data=/scratch/ems011/zhe/beatfm_mirex_20260930/data
run=/scratch/ems011/zhe/beatfm_mirex_20260930/runs/expanded_verified_1684_seed0_v1
export PYTHONPATH="$protocol:/group/ems011/zhe/beatfm_mirex_20260930/python_deps${PYTHONPATH:+:$PYTHONPATH}"
export BEATFM_SOURCE_DIR=/group/ems011/zhe/beatfm_mirex_20260930/source/BeatFM
export BEATFM_MERT_DIR=/group/ems011/zhe/beatfm_mirex_20260930/MERT-v1-95M
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4

# Fail before allocating scoring output if the packaged backend cannot import
# its architecture module. The first evaluation attempt (job 69066) stopped
# here before scoring because this path was not staged on Kaya.
test -f "$protocol/backbone-retrain/train_beatfm.py"

/group/ems011/zhe/envs/auto-structbeat/bin/python "$protocol/evaluate_beatfm_allowed.py" \
  --manifest "$data/expanded_verified_1684.tsv" \
  --subset expanded-1684 \
  --panel common-137 \
  --source-dir "$BEATFM_SOURCE_DIR" \
  --mert-dir "$BEATFM_MERT_DIR" \
  --casm-config "$protocol/casm-no-smc.json" \
  --checkpoint best_val_loss="$run/best_val_loss.pt" \
  --checkpoint epoch_0005="$run/epoch_0005.pt" \
  --checkpoint epoch_0010="$run/epoch_0010.pt" \
  --checkpoint epoch_0015="$run/epoch_0015.pt" \
  --checkpoint epoch_0020="$run/epoch_0020.pt" \
  --output-dir /scratch/ems011/zhe/beatfm_mirex_20260930/runs/expanded_common_eval_seed0_retry1
