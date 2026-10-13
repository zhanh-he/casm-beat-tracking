"""Allow ``python -m casm_beat_tracking`` to run the CLI."""

from .cli import main

raise SystemExit(main())
