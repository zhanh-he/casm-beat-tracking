"""Inference copy of the audited StructBeat TCN trained for MIREX 2026.

The architecture and its 128-bin-to-74-bin adapter match the frozen Kaya
checkpoint. Keep this implementation independent of the training framework.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import nn


class TCNResidualBlock(nn.Module):
    def __init__(self, channels: int, kernel_size: int, dilation: int, dropout: float):
        super().__init__()
        self.residual = nn.Conv1d(channels, channels, kernel_size=1)
        self.dilated_1 = nn.Conv1d(
            channels, channels, kernel_size, dilation=dilation,
            padding=dilation * (kernel_size - 1) // 2,
        )
        self.dilated_2 = nn.Conv1d(
            channels, channels, kernel_size, dilation=2 * dilation,
            padding=2 * dilation * (kernel_size - 1) // 2,
        )
        self.dropout = nn.Dropout1d(dropout)
        self.mix = nn.Conv1d(2 * channels, channels, kernel_size=1)

    def forward(self, values: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        residual = self.residual(values)
        branch = torch.cat((self.dilated_1(values), self.dilated_2(values)), dim=1)
        branch = self.mix(self.dropout(F.elu(branch)))
        return residual + branch, branch


class BeatTCN(nn.Module):
    def __init__(
        self,
        spect_dim: int = 128,
        channels: int = 20,
        kernel_size: int = 5,
        dilations: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024),
        dropout: float = 0.15,
        sum_head: bool = False,
        frequency_adapter: str = "madmom_74",
        original_spect_dim: int = 74,
    ):
        super().__init__()
        if spect_dim < 40 or kernel_size % 2 == 0 or not dilations:
            raise ValueError("invalid TCN frontend dimensions")
        if frequency_adapter not in {"madmom_74", "legacy_post_pool"}:
            raise ValueError("unknown TCN frequency adapter")
        if frequency_adapter == "madmom_74" and original_spect_dim != 74:
            raise ValueError("madmom_74 requires 74 original bands")
        self.spect_dim = spect_dim
        self.sum_head = sum_head
        self.frequency_adapter = frequency_adapter
        self.original_spect_dim = original_spect_dim
        self.frontend = nn.ModuleList((
            nn.Conv2d(1, channels, kernel_size=(3, 3)),
            nn.Conv2d(channels, channels, kernel_size=(1, 10)),
            nn.Conv2d(channels, channels, kernel_size=(3, 3)),
        ))
        self.frontend_dropout = nn.Dropout(dropout)
        self.blocks = nn.ModuleList(
            TCNResidualBlock(channels, kernel_size, dilation, dropout)
            for dilation in dilations
        )
        self.beat_dropout = nn.Dropout(dropout)
        self.downbeat_dropout = nn.Dropout(dropout)
        self.beat_head = nn.Conv1d(channels, 1, kernel_size=1)
        self.downbeat_head = nn.Conv1d(channels, 1, kernel_size=1)

    def _frontend(self, spectrogram: torch.Tensor) -> torch.Tensor:
        if spectrogram.ndim != 3 or spectrogram.shape[-1] != self.spect_dim:
            raise ValueError("TCN expects (batch, frames, 128) log-Mel input")
        spectrogram = spectrogram.to(dtype=self.frontend[0].weight.dtype)
        if self.frequency_adapter == "madmom_74":
            spectrogram = F.interpolate(
                spectrogram, size=self.original_spect_dim,
                mode="linear", align_corners=False,
            )
        values = F.pad(spectrogram[:, None], (0, 0, 2, 2), mode="replicate")
        values = self.frontend_dropout(
            F.max_pool2d(F.elu(self.frontend[0](values)), kernel_size=(1, 3))
        )
        values = self.frontend_dropout(
            F.max_pool2d(F.elu(self.frontend[1](values)), kernel_size=(1, 3))
        )
        values = self.frontend_dropout(
            F.max_pool2d(F.elu(self.frontend[2](values)), kernel_size=(1, 3))
        )
        if self.frequency_adapter == "legacy_post_pool":
            values = F.adaptive_avg_pool2d(values, output_size=(values.shape[2], 1))
        elif values.shape[-1] != 1:
            raise RuntimeError("TCN 74-band frontend did not reduce frequency to one bin")
        return values.squeeze(-1)

    def forward(self, spectrogram: torch.Tensor) -> dict[str, torch.Tensor]:
        values = self._frontend(spectrogram)
        for block in self.blocks:
            values, _ = block(values)
        values = F.elu(values)
        beat = self.beat_head(self.beat_dropout(values)).squeeze(1)
        downbeat = self.downbeat_head(self.downbeat_dropout(values)).squeeze(1)
        if self.sum_head:
            beat = beat.float() + downbeat.float()
        return {"beat": beat, "downbeat": downbeat}
