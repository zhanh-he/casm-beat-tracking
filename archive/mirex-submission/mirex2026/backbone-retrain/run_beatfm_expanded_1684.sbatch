#!/usr/bin/env bash
#SBATCH --job-name=beatfm-expanded-1684
#SBATCH --account=ems011
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100-32gb:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=2-00:00:00
#SBATCH --output=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-expanded-%j.out
#SBATCH --error=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-expanded-%j.err

set -euo pipefail

protocol=/group/ems011/zhe/beatfm_mirex_20260930/protocol
data=/scratch/ems011/zhe/beatfm_mirex_20260930/data
export PYTHONPATH=/group/ems011/zhe/beatfm_mirex_20260930/python_deps${PYTHONPATH:+:$PYTHONPATH}
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4

/group/ems011/zhe/envs/auto-structbeat/bin/python "$protocol/train_beatfm_expanded.py" \
  --manifest "$data/expanded_verified_1684.tsv" \
  --source-dir /group/ems011/zhe/beatfm_mirex_20260930/source/BeatFM \
  --mert-dir /group/ems011/zhe/beatfm_mirex_20260930/MERT-v1-95M \
  --run-dir /scratch/ems011/zhe/beatfm_mirex_20260930/runs/expanded_verified_1684_seed0_v1 \
  --expanded-verified-subset --seed 0 --epochs 100 --patience 20 \
  --batch-size 2 --grad-accumulation 8 --workers 2 --amp none \
  --checkpoint-every 5
