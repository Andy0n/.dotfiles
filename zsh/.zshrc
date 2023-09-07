# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

###############################################################################
# Oh my zsh config:
###############################################################################
# Path to your oh-my-zsh installation.
export ZSH="$HOME/oh-my-zsh/"

ZSH_THEME="jaischeema"

plugins=(git)

source $ZSH/oh-my-zsh.sh

###############################################################################
# User configuration
###############################################################################
# aliases:
alias ls='exa -laa'
alias bat='bat --theme="Catppuccin-mocha"'
alias v='nvim'
alias p='python'
alias t='tmux-sessionizer'
alias c='tmux-cht.sh'
alias l='exa -laGs type'

# Useful env vars:
export EDITOR='nvim'
export VISUAL='nvim'
export PAGER='less'
export MANPAGER='nvim +Man!'

# Custom scripts
export PATH="$HOME/.local/scripts:$PATH"

###############################################################################
# Tools:
###############################################################################
# Install Ruby Gems to ~/gems
export GEM_HOME="$HOME/gems"
export PATH="$HOME/gems/bin:$PATH"


# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/andy/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/andy/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/andy/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/andy/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Node Version Manager:
# source /usr/share/nvm/init-nvm.sh

###############################################################################
# i use arch btw
###############################################################################
neofetch

