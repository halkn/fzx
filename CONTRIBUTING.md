# Contributing

## Development Setup

```sh
uv sync
uv run fzx --help
```

For shell-wrapper development, install the local source tree as an editable
tool:

```sh
uv tool install --editable .
```

Reinstall the editable tool after changing console scripts or other entry point
metadata in `pyproject.toml`.

## Checks

Run these before opening a pull request:

```sh
uv sync --locked
uv run ruff check
uv run ruff format --check
uv run ty check
uv run pytest
```

The GitHub Actions workflow runs the same checks on Python 3.12 and 3.13.
