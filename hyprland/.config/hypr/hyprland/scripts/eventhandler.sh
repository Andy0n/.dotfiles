#!/bin/sh

do_workspace() {
    id=$1
    name=$2

    # echo "Changed to workspace $name (id: $id)"

    if [ "$id" = "10" ]; then
        # echo "This is the last workspace"
        swww img --transition-type outer ~/oof/wallhaven-jx7p2p.jpg
    else
        # echo "This is not the last workspace"
        swww img --transition-type outer ~/wallpapers/wallhaven-j5xoq5.jpg
    fi
}

handle() {
  args=$(echo $1 | sed "s/.*>>//g" | tr "," "\n")

  case $1 in
      workspacev2*) do_workspace $args ;;
  esac
}

socat -U - UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock | while read -r line; do handle "$line"; done
