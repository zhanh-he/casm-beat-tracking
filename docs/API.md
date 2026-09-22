# Python API

CASM is an activation postprocessor. It deliberately does not bundle an audio frontend or neural checkpoint: any backbone that produces aligned beat and downbeat activations at 50 Hz can use the same frozen decoder.

## Madmom-style processor

```python
import numpy as np
from casm_beat_tracking import CASMDownBeatTrackingProcessor

activations = np.load("activations.npy")  # shape: (frames, 2)
processor = CASMDownBeatTrackingProcessor(input_type="probabilities")
events = processor(activations)
```

Column 0 of the input is the beat activation and column 1 is the downbeat activation. `events` has shape `(num_beats, 2)`: time in seconds followed by the natural beat-in-bar number, where 1 denotes a downbeat.

`CASMProcessor` is a short alias. `CASMBeatTrackingProcessor` accepts a one-dimensional beat activation and returns beat times only. All processor objects implement both `processor(data)` and `processor.process(data)`.

This is intentionally familiar to madmom users, but it is not a drop-in replacement for every madmom class. In particular, CASM expects activations rather than an audio filename and supports offline decoding only.

## Low-level decoder

```python
from casm_beat_tracking import CASMDecoder

beats, downbeats = CASMDecoder().decode(
    beat_logits,
    downbeat_logits,
    input_type="logits",
)
```

Use `CASMDecoder` when separate beat/downbeat arrays or separate outputs are more convenient. Both arrays must be finite, one-dimensional, equal in length, and sampled at the configured `fps`.

## Configuration

`CASMDecoder()` and every processor use the frozen 7F setting. Controlled experiments may pass a `CASMConfig`, a JSON file through `CASMConfig.from_json`, or named constructor overrides. Production callers should avoid track-specific overrides.

## Performance contract

The release implementation keeps the original sparse candidate-event dynamic program and local autocorrelation implementation. It does not instantiate madmom, a dense DBN state lattice, PyTorch, or a neural model. The processor wrapper adds shape validation and O(n) event formatting only; benchmark it with:

```bash
python benchmarks/benchmark_decoder.py --api processor
python benchmarks/benchmark_decoder.py --api decoder
```
