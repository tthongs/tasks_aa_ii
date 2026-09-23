#!/usr/bin/env bash
# ==============================================================================
# example_dev_env.sh - Launch an automated multi-window tmux session
# Usage: ./example_dev_env.sh
# ==============================================================================

set -euo pipefail

SESSION="demo-dev"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if tmux is installed
if ! command -v tmux >/dev/null 2>&1; then
    echo "Error: tmux is not installed. Run 'sudo pacman -S tmux' first." >&2
    exit 1
fi

# If session already exists, attach to it
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Attaching to existing session '$SESSION'..."
    tmux attach-session -t "$SESSION"
    exit 0
fi

echo "Creating new session '$SESSION'..."

# Window 1: Notes / Docs (pane starts in tutorial dir)
tmux new-session -d -s "$SESSION" -n "docs" -c "$DIR"
tmux send-keys -t "$SESSION:docs" "cat README.md" C-m

# Window 2: Two-pane split (side-by-side)
tmux new-window -t "$SESSION" -n "split-view" -c "$DIR"
tmux split-window -t "$SESSION:split-view" -h -c "$DIR"

# Send commands to both panes
tmux send-keys -t "$SESSION:split-view.1" "echo 'Left pane: System monitor' && (command -v htop >/dev/null && htop || top)" C-m
tmux send-keys -t "$SESSION:split-view.2" "echo 'Right pane: Quick terminal' && ls -lah" C-m

# Window 3: Practice Scratchpad
tmux new-window -t "$SESSION" -n "scratch" -c "$DIR"
tmux send-keys -t "$SESSION:scratch" "echo 'Welcome to the scratchpad pane! Try creating some splits here.'" C-m

# Select the first window and attach
tmux select-window -t "$SESSION:docs"
tmux attach-session -t "$SESSION"
