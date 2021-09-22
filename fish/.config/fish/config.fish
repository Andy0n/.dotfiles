set -x PATH $PATH /sbin/

function ls
    exa -al --color=always --group-directories-first $argv
end
function vi
    nvim $argv
end
function fd
    fdfind $argv
end
