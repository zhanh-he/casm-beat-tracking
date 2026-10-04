"""Train the supplied BeatFM head on a strict no-SMC raw-audio manifest.

This imports the user's archived MSA and classifier code, but replaces its
incompatible feature-cache dataset and trainer. A partial-audio manifest may
only be used with an explicit pilot flag or an audited 911/1,684-piece
verified-subset flag. Pilot checkpoints are not submission artifacts; subset
checkpoints must disclose their reduced training data.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import socket
import sys
import time


SAMPLE_RATE = 24_000
CLIP_SECONDS = 15
CLIP_HOP_SECONDS = 10  # 5 seconds of overlap, as in the paper
SAMPLES = SAMPLE_RATE * CLIP_SECONDS
FRAMES_PER_SECOND = SAMPLE_RATE / 320
# MERT's seven convolutional strides total 320 samples; the 400-sample
# receptive field produces 1124 hidden-state frames from exactly 15 seconds.
FRAMES = 1124
SOURCE_ZIP_SHA256 = "4fbf554a78f2f353d1461f2267fa45f43b6cf864fc423f146ae46d301018858a"
MERT_REVISION = "12af15fef9d0ac838c3f475bfbbf26d2060dd4f5"


@dataclass(frozen=True)
class Record:
    dataset: str
    stem: str
    split: str
    audio_path: Path
    annotation_path: Path
    annotation_time_shift_seconds: float
    beat_count: int
    downbeat_count: int


def read_manifest(path: Path, *, pilot_partial_audio: bool = False,
                  verified_subset: bool = False,
                  expanded_verified_subset: bool = False) -> tuple[list[Record], str]:
    if sum((pilot_partial_audio, verified_subset, expanded_verified_subset)) > 1:
        raise ValueError("pilot and verified-subset modes are mutually exclusive")
    if not path.is_file():
        raise FileNotFoundError(f"complete original-audio manifest required: {path}")
    rows: list[Record] = []
    seen: set[tuple[str, str]] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"dataset", "stem", "split", "audio_path", "annotation_path", "beat_count", "downbeat_count"}
        if reader.fieldnames is None or not required <= set(reader.fieldnames):
            raise ValueError(f"manifest lacks required columns: {path}")
        for line_no, item in enumerate(reader, 2):
            dataset, stem, split = item["dataset"], item["stem"], item["split"]
            if dataset.lower() in {"smc", "gtzan"} or split not in {"train", "val"}:
                raise ValueError(f"forbidden development piece at {path}:{line_no}")
            if (dataset, stem) in seen:
                raise ValueError(f"duplicate piece at {path}:{line_no}")
            seen.add((dataset, stem))
            audio = Path(item["audio_path"])
            annotation = Path(item["annotation_path"])
            shift = float(item.get("annotation_time_shift_seconds") or 0.0)
            if not math.isfinite(shift) or abs(shift) > 0.5:
                raise ValueError(f"invalid annotation time shift at {path}:{line_no}")
            if not audio.is_file() or not annotation.is_file():
                raise FileNotFoundError(f"original audio or annotation missing at {path}:{line_no}")
            rows.append(Record(dataset, stem, split, audio, annotation, shift,
                               int(item["beat_count"]), int(item["downbeat_count"])))
    if not rows or not any(row.split == "train" for row in rows):
        raise ValueError("manifest has no allowed training pieces")
    if not any(row.split == "val" for row in rows):
        raise ValueError("manifest has no allowed validation pieces")
    # The published BeatThis single split has one empty Beatles annotation.
    # Exact counts make an accidental partial audio map impossible to train on.
    if pilot_partial_audio and len(rows) < 100:
        raise ValueError("pilot requires at least 100 verified original-audio pieces")
    counts = (sum(row.split == "train" for row in rows), sum(row.split == "val" for row in rows))
    if verified_subset:
        by_dataset_split = {
            (dataset, split): sum(row.dataset == dataset and row.split == split for row in rows)
            for dataset in ("ballroom", "rwc") for split in ("train", "val")
        }
        if by_dataset_split != {
            ("ballroom", "train"): 582, ("ballroom", "val"): 103,
            ("rwc", "train"): 192, ("rwc", "val"): 34,
        } or len(rows) != 911:
            raise ValueError("verified subset requires Ballroom 582/103 and RWC 192/34 train/val pieces")
    if expanded_verified_subset:
        expected = {
            ("ballroom", "train"): 582, ("ballroom", "val"): 103,
            ("rwc", "train"): 192, ("rwc", "val"): 34,
            ("hainsworth", "train"): 189, ("hainsworth", "val"): 33,
            ("candombe", "train"): 30, ("candombe", "val"): 5,
            ("groove_midi", "train"): 285, ("groove_midi", "val"): 51,
            ("guitarset", "train"): 153, ("guitarset", "val"): 27,
        }
        actual = {
            key: sum((row.dataset, row.split) == key for row in rows)
            for key in expected
        }
        if len(rows) != 1684 or counts != (1431, 253) or actual != expected:
            raise ValueError("expanded subset requires audited 1,431/253 pieces by dataset")
    if not (pilot_partial_audio or verified_subset or expanded_verified_subset) and counts != (3783, 556):
        raise ValueError("manifest is not the audited 3783-train/556-val no-SMC split")
    return rows, sha256(path.read_bytes()).hexdigest()


def read_events(path: Path) -> tuple[list[float], list[float]]:
    beats: list[float] = []
    downbeats: list[float] = []
    with path.open(encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            values = line.split()
            if not values:
                continue
            when = float(values[0])
            if not math.isfinite(when):
                raise ValueError(f"non-finite annotation at {path}:{line_no}")
            beats.append(when)
            if len(values) > 1 and float(values[1]) == 1:
                downbeats.append(when)
    return beats, downbeats


def make_targets(
    beats: list[float], downbeats: list[float], *, start_seconds: float, valid_seconds: float
):
    import torch

    target = torch.zeros((2, FRAMES), dtype=torch.float32)
    for channel, events in enumerate((beats, downbeats)):
        for when in events:
            relative = when - start_seconds
            if not 0 <= relative < valid_seconds:
                continue  # clips negative Harmonix timestamps and out-of-audio events
            frame = round(relative * FRAMES_PER_SECOND)
            if 0 <= frame < FRAMES:
                target[channel, frame] = 1.0
    # Match the source's ±1/±2 soft labels without torch.roll wrap-around.
    widened = target.clone()
    for shift, weight in ((1, 0.5), (2, 0.25)):
        widened[:, shift:] += weight * target[:, :-shift]
        widened[:, :-shift] += weight * target[:, shift:]
    target = widened.clamp_(max=1.0)
    valid = torch.arange(FRAMES, dtype=torch.float32) / FRAMES_PER_SECOND < valid_seconds
    return target, valid


class ClipDataset:
    def __init__(self, records: list[Record], *, training: bool, pilot_one_crop_per_song: bool = False):
        import torchaudio

        self.records = records
        self.training = training
        self.pilot_one_crop_per_song = pilot_one_crop_per_song
        self.events = []
        for record in records:
            beats, downbeats = read_events(record.annotation_path)
            shift = record.annotation_time_shift_seconds
            self.events.append(([time + shift for time in beats],
                                [time + shift for time in downbeats]))
        self.source_rates: list[int] = []
        self.clips: list[tuple[int, float]] = []
        if pilot_one_crop_per_song:
            self.clips = [(index, 0.0) for index in range(len(records))]
        else:
            for index, record in enumerate(records):
                info = torchaudio.info(str(record.audio_path))
                if info.sample_rate <= 0 or info.num_frames <= 0:
                    raise ValueError(f"undecodable or empty waveform: {record.audio_path}")
                self.source_rates.append(info.sample_rate)
                duration = info.num_frames / info.sample_rate
                start = 0.0
                while start < duration:
                    self.clips.append((index, start))
                    start += CLIP_HOP_SECONDS

    def __len__(self):
        return len(self.clips)

    def __getitem__(self, index):
        import torch
        import torchaudio

        record_index, fixed_start = self.clips[index]
        record = self.records[record_index]
        if self.pilot_one_crop_per_song:
            waveform, source_rate = torchaudio.load(str(record.audio_path))
        else:
            source_rate = self.source_rates[record_index]
            first_source_sample = round(fixed_start * source_rate)
            waveform, source_rate = torchaudio.load(
                str(record.audio_path), frame_offset=first_source_sample,
                num_frames=round(CLIP_SECONDS * source_rate),
            )
        if waveform.ndim != 2 or waveform.shape[-1] == 0:
            raise ValueError(f"undecodable or empty waveform: {record.audio_path}")
        waveform = waveform.float().mean(dim=0)
        if source_rate != SAMPLE_RATE:
            waveform = torchaudio.functional.resample(waveform, source_rate, SAMPLE_RATE)
        duration = waveform.numel() / SAMPLE_RATE
        if self.pilot_one_crop_per_song:
            max_start = max(0.0, duration - CLIP_SECONDS)
            start = random.uniform(0.0, max_start) if self.training else max_start / 2.0
        else:
            start = 0.0
        first_sample = int(start * SAMPLE_RATE)
        clip = waveform[first_sample:first_sample + SAMPLES]
        valid_seconds = clip.numel() / SAMPLE_RATE
        if clip.numel() < SAMPLES:
            clip = torch.nn.functional.pad(clip, (0, SAMPLES - clip.numel()))
        beats, downbeats = self.events[record_index]
        target, valid = make_targets(beats, downbeats,
                                     start_seconds=fixed_start + first_sample / SAMPLE_RATE,
                                     valid_seconds=valid_seconds)
        return clip, target, valid, bool(record.downbeat_count)


def build_model(source_dir: Path, mert_dir: Path, device):
    import torch
    from torch import nn
    from transformers import AutoModel

    if not (source_dir / "MultilevelSemanticAggregation.py").is_file() or not (source_dir / "model.py").is_file():
        raise FileNotFoundError(f"incomplete BeatFM source directory: {source_dir}")
    if not (mert_dir / "pytorch_model.bin").is_file():
        raise FileNotFoundError(f"pinned MERT snapshot missing: {mert_dir}")
    sample_rate = json.loads((mert_dir / "preprocessor_config.json").read_text())["sampling_rate"]
    if sample_rate != SAMPLE_RATE:
        raise ValueError(f"unexpected MERT sample rate: {sample_rate}")
    sys.path.insert(0, str(source_dir.resolve()))
    from MultilevelSemanticAggregation import MultilevelSemanticAggregation
    from model import Classifier

    class SourceBeatFMHead(nn.Module):
        def __init__(self):
            super().__init__()
            self.MSA = MultilevelSemanticAggregation(input_channels=12, need_attention=False)
            self.conv1d = nn.Conv1d(12 * 768, 256, kernel_size=1)
            self.beat_classifier = Classifier(input_channel=256, hidden_channel=128, output_channel=1)
            self.downbeat_classifier = Classifier(input_channel=256, hidden_channel=128, output_channel=1)

        def forward(self, hidden_states):
            if len(hidden_states) != 12:
                raise ValueError(f"expected 12 MERT encoder layers, got {len(hidden_states)}")
            features = torch.stack(hidden_states, dim=1).permute(0, 1, 3, 2)
            features = self.MSA(features)
            batch, layers, channels, frames = features.shape
            features = self.conv1d(features.reshape(batch, layers * channels, frames))
            features = features.permute(0, 2, 1)
            return self.beat_classifier(features), self.downbeat_classifier(features)

    mert = AutoModel.from_pretrained(str(mert_dir), output_hidden_states=True,
                                     trust_remote_code=True).to(device).eval()
    mert.requires_grad_(False)
    head = SourceBeatFMHead().to(device)
    return mert, head


def batch_loss(logits, targets, valid, has_downbeat):
    import torch
    import torch.nn.functional as F

    beat_logits, downbeat_logits = logits
    if beat_logits.shape != (targets.shape[0], 1, FRAMES) or downbeat_logits.shape != beat_logits.shape:
        raise ValueError(f"MERT frame-count mismatch: beat={tuple(beat_logits.shape)}, target={tuple(targets.shape)}")
    beat = F.binary_cross_entropy_with_logits(
        beat_logits[:, 0], targets[:, 0], pos_weight=torch.tensor(5.0, device=targets.device), reduction="none"
    )
    beat = (beat * valid).sum() / valid.sum().clamp_min(1)
    downbeat = F.binary_cross_entropy_with_logits(
        downbeat_logits[:, 0], targets[:, 1], pos_weight=torch.tensor(20.0, device=targets.device), reduction="none"
    )
    downbeat_mask = valid * has_downbeat[:, None]
    downbeat = (downbeat * downbeat_mask).sum() / downbeat_mask.sum().clamp_min(1)
    return beat + downbeat


def save_checkpoint(path: Path, *, head, optimizer, epoch: int, val_loss: float | None,
                    manifest_sha256: str, seed: int, args):
    import torch

    payload = {
        "head_state_dict": head.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epoch,
        "val_loss": val_loss,
        "manifest_sha256": manifest_sha256,
        "source_zip_sha256": SOURCE_ZIP_SHA256,
        "source_msa_sha256": sha256((args.source_dir / "MultilevelSemanticAggregation.py").read_bytes()).hexdigest(),
        "source_model_sha256": sha256((args.source_dir / "model.py").read_bytes()).hexdigest(),
        "mert_revision": MERT_REVISION,
        "seed": seed,
        "recipe": {"sample_rate": SAMPLE_RATE, "clip_seconds": CLIP_SECONDS,
                   "batch_size": args.batch_size, "grad_accumulation": args.grad_accumulation,
                   "clip_hop_seconds": CLIP_HOP_SECONDS, "lr": args.lr,
                   "train_all_allowed": args.train_all_allowed, "amp": args.amp,
                   "pilot_partial_audio_not_submission": args.pilot_partial_audio,
                   "verified_ballroom_rwc_subset": args.verified_subset,
                   "expanded_verified_subset": args.expanded_verified_subset},
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)
    with path.with_suffix(path.suffix + ".sha256").open("w") as handle:
        handle.write(f"{sha256(path.read_bytes()).hexdigest()}  {path.name}\n")


def train(args):
    import torch
    from torch.utils.data import DataLoader

    if "5090" in socket.gethostname().lower():
        raise RuntimeError("BeatFM training is prohibited on lab5090; use Kaya or Gadi")
    if args.pilot_partial_audio and args.train_all_allowed:
        raise ValueError("a partial-audio pilot cannot be labeled an all-allowed-data retrain")
    if sum((args.pilot_partial_audio, args.verified_subset, args.expanded_verified_subset)) > 1:
        raise ValueError("pilot and verified-subset modes are mutually exclusive")
    records, manifest_hash = read_manifest(
        args.manifest, pilot_partial_audio=args.pilot_partial_audio,
        verified_subset=args.verified_subset,
        expanded_verified_subset=args.expanded_verified_subset,
    )
    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else
                          "cpu" if args.device == "auto" else args.device)
    if device.type != "cuda":
        raise RuntimeError("BeatFM training requires a Kaya/Gadi GPU; 5090 is reserved for inference")
    if args.amp == "bf16" and not torch.cuda.is_bf16_supported():
        raise RuntimeError("bf16 requested but this GPU does not support it")
    if args.run_dir.exists():
        raise FileExistsError(f"refusing to overwrite an existing run: {args.run_dir}")
    args.run_dir.mkdir(parents=True)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    train_rows = [r for r in records if r.split == "train" or args.train_all_allowed]
    val_rows = [] if args.train_all_allowed else [r for r in records if r.split == "val"]
    train_dataset = ClipDataset(train_rows, training=True,
                                pilot_one_crop_per_song=args.pilot_partial_audio)
    val_dataset = ClipDataset(val_rows, training=False,
                              pilot_one_crop_per_song=args.pilot_partial_audio) if val_rows else None
    train_loader = DataLoader(train_dataset,
                              batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, pin_memory=True)
    val_loader = DataLoader(val_dataset,
                            batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers, pin_memory=True) if val_dataset else None
    mert, head = build_model(args.source_dir, args.mert_dir, device)
    optimizer = torch.optim.Adam(head.parameters(), lr=args.lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min",
                                                            patience=5, factor=0.5)
    (args.run_dir / "run_config.json").write_text(json.dumps({
        "source_zip_sha256": SOURCE_ZIP_SHA256, "mert_revision": MERT_REVISION,
        "source_msa_sha256": sha256((args.source_dir / "MultilevelSemanticAggregation.py").read_bytes()).hexdigest(),
        "source_model_sha256": sha256((args.source_dir / "model.py").read_bytes()).hexdigest(),
        "manifest_sha256": manifest_hash, "seed": args.seed, "epochs": args.epochs,
        "train_pieces": len(train_rows), "val_pieces": len(val_rows),
        "train_clips": len(train_dataset), "val_clips": len(val_dataset) if val_dataset else 0,
        "shifted_annotation_pieces": sum(r.annotation_time_shift_seconds != 0 for r in records),
        "sample_rate": SAMPLE_RATE, "clip_seconds": CLIP_SECONDS,
        "clip_hop_seconds": CLIP_HOP_SECONDS,
        "batch_size": args.batch_size, "grad_accumulation": args.grad_accumulation,
        "lr": args.lr, "amp": args.amp,
        "train_all_allowed": args.train_all_allowed,
        "pilot_partial_audio_not_submission": args.pilot_partial_audio,
        "verified_ballroom_rwc_subset": args.verified_subset,
        "expanded_verified_subset": args.expanded_verified_subset,
    }, indent=2) + "\n")
    best = math.inf
    stale = 0
    with (args.run_dir / "epochs.jsonl").open("w") as log:
        for epoch in range(1, args.epochs + 1):
            started = time.monotonic()
            head.train()
            train_total = 0.0
            optimizer.zero_grad(set_to_none=True)
            for step, (audio, targets, valid, has_downbeat) in enumerate(train_loader, 1):
                audio, targets, valid = (x.to(device, non_blocking=True) for x in (audio, targets, valid))
                has_downbeat = has_downbeat.to(device, non_blocking=True)
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16,
                                                     enabled=args.amp == "bf16"):
                    features = mert(audio).hidden_states[1:]
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=args.amp == "bf16"):
                    logits = head(features)
                    loss = batch_loss(logits, targets, valid, has_downbeat)
                if not torch.isfinite(loss):
                    raise FloatingPointError(f"non-finite training loss in epoch {epoch}")
                group_start = ((step - 1) // args.grad_accumulation) * args.grad_accumulation
                group_size = min(args.grad_accumulation, len(train_loader) - group_start)
                (loss / group_size).backward()
                if step % args.grad_accumulation == 0 or step == len(train_loader):
                    torch.nn.utils.clip_grad_norm_(head.parameters(), max_norm=1.0)
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                train_total += float(loss.detach()) * len(audio)
            train_loss = train_total / len(train_dataset)
            val_loss = None
            if val_loader is not None:
                head.eval()
                val_total = 0.0
                with torch.no_grad():
                    for audio, targets, valid, has_downbeat in val_loader:
                        audio, targets, valid = (x.to(device, non_blocking=True) for x in (audio, targets, valid))
                        has_downbeat = has_downbeat.to(device, non_blocking=True)
                        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=args.amp == "bf16"):
                            features = mert(audio).hidden_states[1:]
                            logits = head(features)
                            loss = batch_loss(logits, targets, valid, has_downbeat)
                        val_total += float(loss) * len(audio)
                val_loss = val_total / len(val_dataset)
                scheduler.step(val_loss)
                if val_loss < best:
                    best, stale = val_loss, 0
                    save_checkpoint(args.run_dir / "best_val_loss.pt", head=head,
                                    optimizer=optimizer, epoch=epoch, val_loss=val_loss,
                                    manifest_sha256=manifest_hash, seed=args.seed, args=args)
                else:
                    stale += 1
            if epoch % args.checkpoint_every == 0 or epoch == args.epochs:
                save_checkpoint(args.run_dir / f"epoch_{epoch:04d}.pt", head=head,
                                optimizer=optimizer, epoch=epoch, val_loss=val_loss,
                                manifest_sha256=manifest_hash, seed=args.seed, args=args)
            entry = {"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
                     "lr": optimizer.param_groups[0]["lr"],
                     "elapsed_seconds": time.monotonic() - started}
            log.write(json.dumps(entry) + "\n")
            log.flush()
            print(json.dumps(entry), flush=True)
            if val_loader is not None and stale >= args.patience:
                print(f"early stopping after {stale} epochs without val-loss improvement", flush=True)
                break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--mert-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--grad-accumulation", type=int, default=1,
                        help="microbatch steps per optimizer update; 2 x 8 reproduces effective batch 16")
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--checkpoint-every", type=int, default=10)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--amp", choices=("bf16", "none"), default="bf16")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--train-all-allowed", action="store_true")
    parser.add_argument("--pilot-partial-audio", action="store_true", help="run a non-submission pilot on a verified subset")
    parser.add_argument("--verified-subset", action="store_true",
                        help="train on audited 911-piece Ballroom/RWC subset; not full-data reproduction")
    parser.add_argument("--expanded-verified-subset", action="store_true",
                        help="train on audited 1,684-piece original-audio subset; not full-data reproduction")
    args = parser.parse_args()
    if args.epochs < 1 or args.checkpoint_every < 1 or args.batch_size < 1 or args.grad_accumulation < 1:
        parser.error("epochs, checkpoint interval, batch size, and accumulation must be positive")
    train(args)


if __name__ == "__main__":
    main()
