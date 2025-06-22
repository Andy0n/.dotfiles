#!/usr/bin/env bash
# SAVE_DIR="$HOME/Pictures/Screenshots"
# mkdir -p "$SAVE_DIR"
# TS=$(date +%Y-%m-%d_%H-%M-%S)
# OUT="$SAVE_DIR/screenshot_$TS.png"
# MODE="$1"    # full|window|region
#
# # 1) capture into $OUT …
# case "$MODE" in
#   full)   grim "$OUT" ;;
#   window)
#     geom=$(hyprctl activewindow \
#            | awk '/geometry:/ {
#                gsub(/geometry: |[+x]/," ");
#                print $3","$4" "$1"x"$2;
#                exit
#              }')
#     grim -g "$geom" "$OUT"
#     ;;
#   region) grim -g "$(slurp)" "$OUT" ;;
#   *)
#     echo "Usage: $0 {full|window|region}" >&2
#     exit 1
#     ;;
# esac
#
#
# # 5) send to clipboard & notify
# wl-copy --type image/png < "$OUT"
# notify-send "📸 Screenshot saved & copied" "$OUT"

SAVE_DIR="$HOME/Pictures/Screenshots"
mkdir -p "$SAVE_DIR"

TS=$(date +%Y-%m-%d_%H-%M-%S)
OUT="$SAVE_DIR/screenshot_$TS.png"

function get_windows() {
    # grimblast:
    # FULLSCREEN_WORKSPACES="$(hyprctl workspaces -j | jq -r 'map(select(.hasfullscreen) | .id)')"
    # WORKSPACES="$(hyprctl monitors -j | jq -r '[(foreach .[] as $monitor (0; if $monitor.specialWorkspace.name == "" then $monitor.activeWorkspace else $monitor.specialWorkspace end)).id]')"
    # WINDOWS="$(hyprctl clients -j | jq -r --argjson workspaces "$WORKSPACES" --argjson fullscreenWorkspaces "$FULLSCREEN_WORKSPACES" 'map((select(([.workspace.id] | inside($workspaces)) and ([.workspace.id] | inside($fullscreenWorkspaces) | not) or .fullscreen > 0)))')"
    # # shellcheck disable=2086 # if we don't split, spaces mess up slurp
    # GEOM=$(echo "$WINDOWS" | jq -r '.[] | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"' | slurp $SLURP_ARGS)

    # hyprshot:
    local monitors=`hyprctl -j monitors`
    local clients=`hyprctl -j clients | jq -r '[.[] | select(.workspace.id | contains('$(echo $monitors | jq -r 'map(.activeWorkspace.id) | join(",")')'))]'`
    local boxes="$(echo $clients | jq -r '.[] | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1]) \(.title)"' | cut -f1,2 -d' ')"
    echo "$boxes" | slurp
}

# hyprctl keyword animation "fadeOut,0,0,default"
hyprctl keyword layerrule "noanim,selection" >/dev/null

grim -g "$(get_windows)" "$OUT"

# hyprctl keyword animation "fadeOut,1,4,default"

wl-copy --type image/png < "$OUT"

notify-send "📸 Screenshot saved & copied" "$OUT"
