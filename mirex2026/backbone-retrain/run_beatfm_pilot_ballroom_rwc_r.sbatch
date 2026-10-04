#!/usr/bin/env bash
#SBATCH --job-name=beatfm-audio-pilot
#SBATCH --account=ems011
#SBATCH --partition=gpu
#SBATCH --gres=gpu:v100-32gb:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-pilot-%j.out
#SBATCH --error=/group/ems011/zhe/beatfm_mirex_20260930/logs/beatfm-pilot-%j.err

set -euo pipefail

# A 700-song end-to-end engineering pilot, NOT a MIREX submission checkpoint.
# It contains only verified Ballroom and RWC-R audio while other sources are
# acquired. V100 lacks bf16, so this uses full precision and microbatch 2.
protocol=/group/ems011/zhe/beatfm_mirex_20260930/protocol
data=/scratch/ems011/zhe/beatfm_mirex_20260930/data
export PYTHONPATH=/group/ems011/zhe/beatfm_mirex_20260930/python_deps${PYTHONPATH:+:$PYTHONPATH}
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4

/group/ems011/zhe/envs/auto-structbeat/bin/python "$protocol/train_beatfm.py" \
  --manifest "$data/pilot_ballroom_rwc_r.tsv" \
  --source-dir /group/ems011/zhe/beatfm_mirex_20260930/source/BeatFM \
  --mert-dir /group/ems011/zhe/beatfm_mirex_20260930/MERT-v1-95M \
  --run-dir /scratch/ems011/zhe/beatfm_mirex_20260930/runs/pilot_ballroom_rwc_r_seed0_e1_retry1 \
  --pilot-partial-audio \
  --seed 0 --epochs 1 --batch-size 2 --workers 2 --amp none \
  --checkpoint-every 1
