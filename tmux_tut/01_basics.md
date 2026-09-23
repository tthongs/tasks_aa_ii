# Chapter 1: Core Concepts & Architecture

tmux stands for **Terminal Multiplexer**. It lets you run multiple terminal sessions inside a single window, detach from them, and reattach later without interrupting any running programs.

---

## 1. The tmux Hierarchy

Understanding how tmux models your workspace is key to using it effectively:

```
[ tmux server ]
       │
       ├── Session 1 ("project-api")
       │       ├── Window 1: "editor"  ─── [ Pane 1 (Neovim) ]
       │       └── Window 2: "server"  ─── ┬── [ Pane 1 (dev server) ]
       │                                   └── [ Pane 2 (logs) ]
       │
       └── Session 2 ("scratch")
               └── Window 1: "bash"    ─── [ Pane 1 (shell) ]
```

1. **Server**: The background daemon that manages all sessions, windows, and panes. It stays running as long as at least one session is open.
2. **Session**: A collection of one or more windows. A session typically represents a specific project or context (e.g., `web-backend`, `dotfiles`, `data-pipeline`).
3. **Window**: Similar to a tab in a browser or graphical terminal emulator. Only one window is displayed at a time per session (unless multi-attached).
4. **Pane**: A slice of a window. Windows can be split horizontally or vertically into multiple panes.

---

## 2. The Prefix Key

Because tmux runs inside a terminal, it must distinguish between keys you want to send to your shell (like `ls` or `Enter`) and keys meant for tmux itself.

It accomplishes this using a **Prefix key**:
* **Default Prefix**: `Ctrl + b`
* **How to press it**:
  1. Press and hold `Ctrl`.
  2. Press `b`.
  3. Release both keys.
  4. Press the command key (e.g., `c` to create a window, or `%` to split).

> [!TIP]
> In tmux documentation and configs, `Ctrl + b` is written as `C-b` or `<Prefix>`.

---

## 3. Session Lifecycle: Detach and Reattach

The superpower of tmux is persistence. If your SSH connection drops or you close your terminal window, programs running in tmux **do not terminate**.

### Starting a Session
```bash
# Start an unnamed session (0, 1, 2...):
tmux

# Recommended: Start a named session:
tmux new -s my-work
```

### Detaching from a Session
Inside tmux, press:
```
<Prefix> d
```
You will return to your regular terminal prompt, with a message like `[detached (from session my-work)]`. Your processes inside tmux are still running in the background.

### Listing Active Sessions
```bash
tmux ls
```
Output:
```
my-work: 1 windows (created Wed Sep 23 15:20:00 2026)
```

### Reattaching to a Session
```bash
# Reattach to the most recently used session:
tmux a

# Reattach to a specific session by name:
tmux a -t my-work
```

### Terminating a Session
- **From inside tmux**: Type `exit` in each shell pane until all panes/windows close.
- **Or from your regular terminal**:
  ```bash
  tmux kill-session -t my-work
  ```

---

## 4. Summary of Chapter 1 Commands

| Command | Action |
| :--- | :--- |
| `tmux new -s <name>` | Create and attach to named session |
| `<Prefix> d` | Detach safely from current session |
| `tmux ls` | List all running tmux sessions |
| `tmux a -t <name>` | Reattach to named session |
| `tmux kill-session -t <name>` | Kill specific session |
