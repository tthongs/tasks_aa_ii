# Chapter 5: Scripting & Workspace Automation

One of tmux's strongest capabilities is that **every single tmux command can be driven programmatically from the shell**.

Instead of opening a terminal and manually creating windows, splitting panes, navigating directories, and launching commands every morning, you can create a 1-click startup script.

---

## 1. Key Scripting Commands

| Command | Purpose |
| :--- | :--- |
| `tmux has-session -t <name> 2>/dev/null` | Check if session `<name>` already exists |
| `tmux new-session -d -s <name> -n <win>` | Create a session in detached/background mode (`-d`) |
| `tmux new-window -t <name> -n <win>` | Create a new window in the specified session |
| `tmux split-window -t <target> -h/-v` | Split a target window/pane horizontally or vertically |
| `tmux send-keys -t <target> 'cmd' C-m` | Send keystrokes to a pane (`C-m` represents `Enter`) |
| `tmux select-window -t <target>` | Set the active window |
| `tmux attach-session -t <name>` | Connect your terminal to the session |

---

## 2. A Real-World Startup Script

Here is an annotated script pattern for launching a complete development environment for a project:

```bash
#!/usr/bin/env bash

SESSION_NAME="myproject"
PROJECT_DIR="$HOME/projects/myproject"

# 1. If session already exists, simply attach to it
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists. Attaching..."
    tmux attach-session -t "$SESSION_NAME"
    exit 0
fi

# 2. Create detached session with first window named 'editor'
tmux new-session -d -s "$SESSION_NAME" -n "editor" -c "$PROJECT_DIR"

# Window 1: Editor
tmux send-keys -t "$SESSION_NAME:editor" "nvim" C-m

# Window 2: Servers & Logs
tmux new-window -t "$SESSION_NAME" -n "server" -c "$PROJECT_DIR"
# Split server window horizontally (side-by-side)
tmux split-window -t "$SESSION_NAME:server" -h -c "$PROJECT_DIR"
# Top/Left: start backend
tmux send-keys -t "$SESSION_NAME:server.1" "npm run dev" C-m
# Right: split vertically for database & logs
tmux split-window -t "$SESSION_NAME:server.2" -v -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:server.3" "tail -f /var/log/syslog" C-m

# Window 3: Git & General Shell
tmux new-window -t "$SESSION_NAME" -n "git" -c "$PROJECT_DIR"
tmux send-keys -t "$SESSION_NAME:git" "git status" C-m

# 3. Focus the 'editor' window and attach to the session
tmux select-window -t "$SESSION_NAME:editor"
tmux attach-session -t "$SESSION_NAME"
```

---

## 3. Dedicated Tools: tmuxinator & tmuxp

While shell scripts are lightweight and require no dependencies, if you manage dozens of complex multi-session layouts, you can explore YAML-based managers:
- **[tmuxinator](https://github.com/tmuxinator/tmuxinator)** (Ruby)
- **[tmuxp](https://github.com/tmux-python/tmuxp)** (Python)

Both allow defining your sessions, windows, splits, and commands declaratively in a `.yml` file.
