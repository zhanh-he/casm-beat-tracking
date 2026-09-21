"""Public CASM decoding API."""

from .config import CASMConfig, DEFAULT_CONFIG
from .decoder import CASMDecoder

__all__ = ["CASMConfig", "CASMDecoder", "DEFAULT_CONFIG"]
__version__ = "0.1.0"
