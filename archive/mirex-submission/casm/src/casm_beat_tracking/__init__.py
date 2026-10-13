"""Public CASM decoding API."""

from .config import CASMConfig, DEFAULT_CONFIG
from .decoder import CASMDecoder
from .processors import (
    CASMBeatTrackingProcessor,
    CASMDownBeatTrackingProcessor,
    CASMProcessor,
    beat_numbers,
    events_from_times,
)

__all__ = [
    "CASMBeatTrackingProcessor",
    "CASMConfig",
    "CASMDecoder",
    "CASMDownBeatTrackingProcessor",
    "CASMProcessor",
    "DEFAULT_CONFIG",
    "beat_numbers",
    "events_from_times",
]
__version__ = "0.1.0"
