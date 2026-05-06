# fzx

Shell-independent fzf helpers.

`fzx` is a Python CLI that moves personal fzf workflows out of zsh functions.
Commands that can complete by themselves run the action directly. Commands that
must change shell state print the selected value to stdout so a shell wrapper can
decide what to do with it.

## Install

For local development:

```sh
uv sync
uv run fzx --help
```

To test the command from shell wrappers while editing the source tree:

```sh
uv tool install --editable .
fzx --help
```

Re-run the install command after changing entry points in `pyproject.toml`.

As a user tool:

```sh
uv tool install git+https://github.com/halkn/fzx
```

## Commands

```text
fzx history
fzx cd
fzx rm
fzx git branch
fzx git stage
fzx git log
fzx git worktree
fzx repo list
fzx repo get <url|owner/repo>
fzx repo cd
```

`fzx cd`, `fzx git worktree`, `fzx repo cd`, and `fzx history` print the
selected path or command to stdout. They are intended to be wrapped by the
calling shell.

Example zsh wrappers:

```zsh
fh() {
  local command
  command=$(fc -l 1 | fzx history) || return
  [[ -n "$command" ]] && print -z -- "$command"
}

fcd() {
  local dir
  dir=$(fzx cd) || return
  [[ -n "$dir" ]] && cd -- "$dir"
}

fgw() {
  local dir
  dir=$(fzx git worktree) || return
  [[ -n "$dir" ]] && cd -- "$dir"
}
```

## Repo Layout

`fzx repo` uses `~/dev` by default. Override it with `--root` or
`FZX_REPO_ROOT`.

```sh
fzx repo --root ~/src list
FZX_REPO_ROOT=~/src fzx repo cd
```

`--root` is a `repo` option, so place it before the subcommand.

Supported `repo get` inputs:

- `https://github.com/owner/name.git`
- `git@github.com:owner/name.git`
- `owner/name`
- `https://dev.azure.com/org/project/_git/name`

The clone destination is derived as:

```text
<root>/<host>/<owner>/<name>
<root>/dev.azure.com/<org>/<project>/<name>
```

## Optional Tools

`fzf` is required for interactive commands. Other tools are optional and have
fallbacks:

- `fd` -> `find`
- `bat` -> `sed`
- `lsd` or `eza` -> `ls` or `find`
- `delta` -> raw git output

## Development

```sh
uv run pytest
uv run ruff check
uv run ruff format --check
uv run ty check
```

CI runs the same checks on Python 3.12 and 3.13 with `uv sync --locked`.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the PR checklist.

If `uv` cannot write to its default cache in a sandboxed environment, point the
cache at a writable directory:

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run fzx --help
```
