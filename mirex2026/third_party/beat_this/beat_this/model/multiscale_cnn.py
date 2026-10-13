"""
Multiscale multitask CNN for beat and downbeat tracking.

The module follows the Beat This model interface: input spectrograms are shaped
as (batch, time, frequency), and the output is a dictionary with framewise beat
and downbeat logits of shape (batch, time).
"""

from __future__ import annotations

import torch
from torch import nn


class MultiscaleTemporalBlock(nn.Module):
    """Residual temporal block with parallel convolutional time scales."""

    def __init__(
        self,
        channels: int,
        kernel_sizes: tuple[int, ...],
        dilation: int,
        dropout: float,
    ) -> None:
        super().__init__()
        if not kernel_sizes:
            raise ValueError("kernel_sizes must not be empty")
        for kernel_size in kernel_sizes:
            if kernel_size % 2 == 0:
                raise ValueError("kernel_sizes must be odd to preserve frame alignment")

        branch_channels = max(1, channels // len(kernel_sizes))
        out_channels = branch_channels * len(kernel_sizes)
        self.branches = nn.ModuleList(
            nn.Sequential(
                nn.Conv1d(
                    channels,
                    branch_channels,
                    kernel_size=kernel_size,
                    padding=(kernel_size // 2) * dilation,
                    dilation=dilation,
                    bias=False,
                ),
                nn.BatchNorm1d(branch_channels),
                nn.GELU(),
            )
            for kernel_size in kernel_sizes
        )
        self.mix = nn.Sequential(
            nn.Conv1d(out_channels, channels, kernel_size=1, bias=False),
            nn.BatchNorm1d(channels),
            nn.GELU(),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = torch.cat([branch(x) for branch in self.branches], dim=1)
        return x + self.mix(y)


class MultiscaleMultitaskCNN(nn.Module):
    """
    Multiscale CNN backend for beat/downbeat multitask learning.

    It intentionally keeps the same logits and optional sum-head semantics as
    Beat This, so losses, postprocessing, chunked prediction, and metrics remain
    unchanged.
    """

    def __init__(
        self,
        spect_dim: int = 128,
        channels: int = 128,
        n_layers: int = 8,
        kernel_sizes: tuple[int, ...] = (3, 5, 9, 17),
        dilation_cycle: tuple[int, ...] = (1, 2, 4, 8),
        dropout: float = 0.2,
        sum_head: bool = True,
    ) -> None:
        super().__init__()
        if n_layers < 1:
            raise ValueError("n_layers must be at least 1")
        if channels < 1:
            raise ValueError("channels must be at least 1")
        if not dilation_cycle:
            raise ValueError("dilation_cycle must not be empty")

        self.sum_head = sum_head
        self.input_norm = nn.BatchNorm1d(spect_dim)
        self.stem = nn.Sequential(
            nn.Conv1d(spect_dim, channels, kernel_size=1, bias=False),
            nn.BatchNorm1d(channels),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.blocks = nn.Sequential(
            *[
                MultiscaleTemporalBlock(
                    channels=channels,
                    kernel_sizes=kernel_sizes,
                    dilation=dilation_cycle[i % len(dilation_cycle)],
                    dropout=dropout,
                )
                for i in range(n_layers)
            ]
        )
        self.head = nn.Conv1d(channels, 2, kernel_size=1)

        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Conv1d):
            nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
            if module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        x = x.transpose(1, 2)
        x = self.input_norm(x)
        x = self.stem(x)
        x = self.blocks(x)
        beat_downbeat = self.head(x)
        beat = beat_downbeat[:, 0]
        downbeat = beat_downbeat[:, 1]
        if self.sum_head:
            beat = beat.float() + downbeat.float()
        return {"beat": beat, "downbeat": downbeat}
