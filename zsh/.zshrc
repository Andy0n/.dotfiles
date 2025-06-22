# [ZINIT] load:
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"
[ ! -d $ZINIT_HOME ] && mkdir -p "$(dirname $ZINIT_HOME)"
[ ! -d $ZINIT_HOME/.git ] && git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
source "${ZINIT_HOME}/zinit.zsh"

# [ZINIT] plugins:
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab
zinit load atuinsh/atuin

# [ZINIT] snippets:
zinit snippet OMZP::git
zinit snippet OMZP::sudo
zinit snippet OMZP::archlinux
zinit snippet OMZP::aws
zinit snippet OMZP::kubectl
zinit snippet OMZP::kubectx
zinit snippet OMZP::command-not-found

# [ZSH-COMPLETIONS] load:
autoload -U compinit && compinit
zinit cdreplay -q

# [ZSH] key bindings:
bindkey -e

# [ZSH] env vars:
export EDITOR='nvim'
export VISUAL='nvim'
export PAGER='less'
export MANPAGER='nvim +Man!'
export SUDO_EDITOR='nvim'
# local scripts:
export PATH="$HOME/.local/scripts:$PATH"
# ruby gems:
export GEM_HOME="$HOME/gems"
export PATH="$HOME/gems/bin:$PATH"
# nix:
export PATH="$HOME/.nix-profile/bin:$PATH"
# fzf:
export FZF_DEFAULT_OPTS="$FZF_DEFAULT_OPTS \
  --height=40% \
  --highlight-line \
  --info=inline-right \
  --ansi \
  --layout=reverse \
  --border=none \
  --color=bg+:#283457 \
  --color=border:#27a1b9 \
  --color=fg:#c0caf5 \
  --color=gutter:#16161e \
  --color=header:#ff9e64 \
  --color=hl+:#2ac3de \
  --color=hl:#2ac3de \
  --color=info:#545c7e \
  --color=marker:#ff007c \
  --color=pointer:#ff007c \
  --color=prompt:#2ac3de \
  --color=query:#c0caf5:regular \
  --color=scrollbar:#27a1b9 \
  --color=separator:#ff9e64 \
  --color=spinner:#ff007c \
"

# [ZSH-COMPLETIONS] config:
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:*' fzf-preview \
   '[[ -d $realpath ]] && { echo "       Directory: \e[1m$(basename "$realpath")\e[0m" && eza -1a --color=always --ignore-glob ".DS_Store|.idea|.vscode" $realpath } || bat --color=always $realpath'
zstyle ':fzf-tab:complete:*' fzf-flags                                                                                 \
    $(print -r -- "$FZF_DEFAULT_OPTS") \
    --preview-window=right:60%:wrap:cycle:border-double \
    --bind="tab:toggle-down"                                                                                           \
    --bind="ctrl-p:change-preview-window(down,90%,wrap,cycle,border-double|hidden|right,50%,wrap,cycle,border-double)" \
    --bind="ctrl-v:execute(bat --paging=always --color=always {+})"

# [ZSH] functions:
function nvm_command() {
    if (( $+commands[nvm] )); then
        nvm "$@"
    else
        source /usr/share/nvm/init-nvm.sh
        nvm "$@"
    fi
}

# [ZSH] aliases:
alias ls='eza -laa'
alias l='eza -laGs type'
alias n='nvim'
alias p='python'
alias venv="source .venv/bin/activate"
alias t='tmux-sessionizer'
alias c='tmux-cht.sh'
alias nv="nvm_command"
alias bat='bat --theme="Catppuccin-mocha"'
alias yeet="paru -Rns"
alias yay="paru"

# [ZSH] shell integrations:
eval "$(zoxide init --cmd cd zsh)"
eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/config.yaml)"
# eval "$(starship init zsh)"

# Custom handlers
command_not_found_handler() {
    echo "\033[1;31mWRONG!\033[0m"
    return 127
}

# i use arch btw
# printf '\n%.0s' {1..100}
fastfetch
