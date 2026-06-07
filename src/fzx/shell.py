from __future__ import annotations

SUPPORTED_SHELLS = ("zsh",)

_ZSH_INIT = r"""# fzx shell integration for zsh.
# Loaded with: eval "$(fzx init zsh)"
#
# The integration is pure shell, so startup only pays the cost of evaluating
# this static script once. fzx (and its Python interpreter) runs only when a
# widget is invoked.
#
# Configuration (set before the eval above):
#   FZX_NO_DEFAULT_KEYBINDINGS  set to any value to skip default bindkey calls
#   FZX_HISTORY_KEY             key for the history widget   (default ^R)
#   FZX_CD_KEY                  key for the cd widget        (default ^[c)
#   FZX_GIT_WORKTREE_KEY        key for the worktree widget  (default ^[w)
#   FZX_REPO_CD_KEY             key for the repo cd widget   (default ^[r)

# --- command history: replace the edit buffer with the chosen command --------
fzx-history-widget() {
  local selected
  selected="$(fc -l 1 | fzx history)" || { zle reset-prompt; return }
  if [[ -n "$selected" ]]; then
    BUFFER="$selected"
    CURSOR=$#BUFFER
  fi
  zle reset-prompt
}
zle -N fzx-history-widget

# --- cd into the chosen directory --------------------------------------------
fzx-cd-widget() {
  local dir
  dir="$(fzx cd)" || { zle reset-prompt; return }
  if [[ -n "$dir" ]]; then
    builtin cd -- "$dir"
  fi
  local ret=$?
  zle reset-prompt
  return $ret
}
zle -N fzx-cd-widget

# --- cd into the chosen git worktree -----------------------------------------
fzx-git-worktree-widget() {
  local dir
  dir="$(fzx git worktree)" || { zle reset-prompt; return }
  if [[ -n "$dir" ]]; then
    builtin cd -- "$dir"
  fi
  local ret=$?
  zle reset-prompt
  return $ret
}
zle -N fzx-git-worktree-widget

# --- cd into the chosen repository -------------------------------------------
fzx-repo-cd-widget() {
  local dir
  dir="$(fzx repo cd)" || { zle reset-prompt; return }
  if [[ -n "$dir" ]]; then
    builtin cd -- "$dir"
  fi
  local ret=$?
  zle reset-prompt
  return $ret
}
zle -N fzx-repo-cd-widget

if [[ -z "${FZX_NO_DEFAULT_KEYBINDINGS:-}" ]]; then
  bindkey "${FZX_HISTORY_KEY:-^R}" fzx-history-widget
  bindkey "${FZX_CD_KEY:-^[c}" fzx-cd-widget
  bindkey "${FZX_GIT_WORKTREE_KEY:-^[w}" fzx-git-worktree-widget
  bindkey "${FZX_REPO_CD_KEY:-^[r}" fzx-repo-cd-widget
fi
"""

_INIT_SCRIPTS = {
    "zsh": _ZSH_INIT,
}


def init_script(shell: str) -> str:
    """Return the shell integration script for ``shell``.

    Raises ``ValueError`` for an unsupported shell.
    """
    try:
        return _INIT_SCRIPTS[shell]
    except KeyError:
        supported = ", ".join(SUPPORTED_SHELLS)
        raise ValueError(f"unsupported shell '{shell}' (supported: {supported})") from None
