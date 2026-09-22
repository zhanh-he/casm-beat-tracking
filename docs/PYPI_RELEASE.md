# PyPI release

The distribution name is `casm-beat-tracking`; the import name is `casm_beat_tracking`. The distribution name returned 404 from the public PyPI JSON endpoint on 2026-09-22, but it is not reserved until the first successful upload.

## Release blockers

1. Choose and add the project license. Do not publish code or CASM-trained weights until ownership and third-party obligations are settled.
2. Review the public API and bump the version in both `pyproject.toml` and `casm_beat_tracking.__version__`.
3. Make the release from a reviewed tag, not directly from an experiment checkout.

## Build and validate

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m build
python -m twine check dist/*
```

This produces a pure-Python wheel and source distribution. Test the wheel in a clean virtual environment before uploading.

## TestPyPI and PyPI

```bash
python -m twine upload --repository testpypi dist/*
# After installing and checking the TestPyPI artifact:
python -m twine upload dist/*
```

Prefer PyPI Trusted Publishing from a protected GitHub release workflow after the project has been created. It avoids storing a long-lived API token in repository secrets. The publication workflow is deliberately not enabled yet because the license decision and PyPI project ownership require maintainer approval.
