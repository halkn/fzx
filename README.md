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
fzx init zsh
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

## Shell Integration

Rather than hand-writing wrappers, let `fzx` generate them. Add this to your
`.zshrc`:

```zsh
eval "$(fzx init zsh)"
```

Because Python startup is slow, the integration is deliberately a *static*
shell script: `fzx init zsh` only emits text. The Python process runs once at
shell startup to produce that script, then only again when you actually invoke
a widget — never on every prompt. `init` itself is on a fast path that skips
loading the command modules, so it is several times cheaper than a normal `fzx`
command.

### Cached startup (recommended for tmux / frequent shells)

If you open new shells constantly (e.g. a fresh pane per tmux split), even the
one `fzx init zsh` per startup adds up. Cache the generated script and source
it instead; `fzx` then runs *only* after you upgrade it:

```zsh
() {
  local cache="${XDG_CACHE_HOME:-$HOME/.cache}/fzx/init.zsh"
  # Regenerate only when the fzx binary is newer than the cached script.
  if [[ ! -r "$cache" || "$commands[fzx]" -nt "$cache" ]]; then
    mkdir -p "${cache:h}"
    fzx init zsh >| "$cache"
  fi
  source "$cache"
}
```

Sourcing the cached file is a couple of milliseconds and starts no Python at
all. Set any `FZX_*` configuration (below) before this block.

`fzx init zsh` defines ZLE widgets and binds them by default:

| Key         | Widget                    | Action                     |
| ----------- | ------------------------- | -------------------------- |
| `Ctrl-R`    | `fzx-history-widget`      | put a past command in the buffer |
| `Alt-C`     | `fzx-cd-widget`           | `cd` into a directory      |
| `Alt-W`     | `fzx-git-worktree-widget` | `cd` into a git worktree   |
| `Alt-R`     | `fzx-repo-cd-widget`      | `cd` into a repository     |

Configure it by setting these before the `eval` line:

```zsh
# Skip the default bindings and bind the widgets yourself.
FZX_NO_DEFAULT_KEYBINDINGS=1
eval "$(fzx init zsh)"
bindkey '^R' fzx-history-widget

# Or just override individual keys.
FZX_HISTORY_KEY='^T'
FZX_CD_KEY='^[c'
FZX_GIT_WORKTREE_KEY='^[w'
FZX_REPO_CD_KEY='^[r'
eval "$(fzx init zsh)"
```

The generated script is static, so you can cache it to shave the one-time
startup cost if you want:

```zsh
fzx init zsh > ~/.cache/fzx-init.zsh   # regenerate after upgrading fzx
source ~/.cache/fzx-init.zsh
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
