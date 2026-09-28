# DBN experiments

This directory records the DBN calibration-scale study used for the paper.
The grid varies minimum BPM, maximum BPM, and transition strength while keeping
the observation model and meter inventory fixed.

- `run_dbn_calibration_scale.py`: experiment driver.
- `calibration/`: frozen protocols, selected configurations, audit tables, and
  fixed-panel summaries.

The conventional baseline uses meters `{3, 4}`, transition weight `100`,
observation weight `16`, threshold `0.05`, and 55–215 BPM. The matched-support
diagnostic changes only the tempo range to 30–300 BPM.
