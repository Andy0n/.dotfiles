# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

###############################################################################
# Oh my zsh config:
###############################################################################
# Path to your oh-my-zsh installation.
export ZSH="$HOME/oh-my-zsh/"
export ZSH_COMPDUMP=$ZSH/cache/.zcompdump-$HOST

ZSH_THEME="jaischeema"

plugins=(git)

source $ZSH/oh-my-zsh.sh

###############################################################################
# User configuration
###############################################################################
# functions:
function nvm_command() {
    if (( $+commands[nvm] )); then
        nvm "$@"
    else
        source /usr/share/nvm/init-nvm.sh
        nvm "$@"
    fi
}

# aliases:
alias ls='eza -laa'
alias bat='bat --theme="Catppuccin-mocha"'
alias v='nvim'
alias n='nvim'
alias p='python'
alias t='tmux-sessionizer'
alias c='tmux-cht.sh'
alias l='eza -laGs type'
alias ssh='kitty +kitten ssh'
alias yeet="paru -Rns"
alias yay="paru"
alias venv="source venv/bin/activate"
alias nv="nvm_command"

# Useful env vars:
export EDITOR='nvim'
export VISUAL='nvim'
export PAGER='less'
export MANPAGER='nvim +Man!'

# Catppuccin for fzf:
export FZF_DEFAULT_OPTS=" \
--color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8 \
--color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc \
--color=marker:#f5e0dc,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8"

# Custom scripts
export PATH="$HOME/.local/scripts:$PATH"

# Custom handlers
command_not_found_handler() {
    # echo "\033[1;31mwtf is '$@'?\033[0m"
    echo "\033[1;31mWRONG!\033[0m"
    return 127
}

###############################################################################
# Tools:
###############################################################################
# Install Ruby Gems to ~/gems
export GEM_HOME="$HOME/gems"
export PATH="$HOME/gems/bin:$PATH"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
# __conda_setup="$('/home/andy/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
# if [ $? -eq 0 ]; then
#     eval "$__conda_setup"
# else
#     if [ -f "/home/andy/miniconda3/etc/profile.d/conda.sh" ]; then
#         . "/home/andy/miniconda3/etc/profile.d/conda.sh"
#     else
#         export PATH="/home/andy/miniconda3/bin:$PATH"
#     fi
# fi
# unset __conda_setup
# <<< conda initialize <<<

###############################################################################
# i use arch btw
###############################################################################
fastfetch

