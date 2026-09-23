# tmux Cheatsheet

> In tmux, all default shortcuts begin with the **Prefix key**: `Ctrl + b` (written as `<Prefix>`).
> Press `<Prefix>`, release both keys, and then press the command key.

---

## 1. CLI Commands (from your standard shell)

| Command | Action |
| :--- | :--- |
| `tmux` | Start a new unnamed session |
| `tmux new -s <name>` | Start a new session named `<name>` |
| `tmux ls` (or `tmux list-sessions`) | List all running sessions |
| `tmux attach` (or `tmux a`) | Attach to the last active session |
| `tmux a -t <name>` | Attach to a session named `<name>` |
| `tmux kill-session -t <name>` | Terminate session `<name>` |
| `tmux kill-server` | Terminate all tmux sessions and kill the server |
| `tmux source-file ~/.tmux.conf` | Reload configuration from terminal |

---

## 2. Session Management (Inside tmux)

| Keybinding | Action |
| :--- | :--- |
| `<Prefix> d` | **Detach** from current session (session stays running in background) |
| `<Prefix> s` | Interactive session tree/selector (navigate with arrows or j/k) |
| `<Prefix> $` | Rename current session |
| `<Prefix> (` / `)` | Switch to previous / next session |
| `<Prefix> :` | Open the tmux command prompt |

---

## 3. Window Management (Tabs)

| Keybinding | Action |
| :--- | :--- |
| `<Prefix> c` | **Create** a new window |
| `<Prefix> ,` | Rename current window |
| `<Prefix> n` / `p` | Go to **Next** / **Previous** window |
| `<Prefix> 0-9` | Jump directly to window number `0-9` |
| `<Prefix> w` | Interactive visual window/session list |
| `<Prefix> &` | Kill current window (with confirmation) |
| `<Prefix> l` | Jump to the last active window |

---

## 4. Pane Management (Splits)

| Default Key | Custom ([tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf)) | Action |
| :--- | :--- | :--- |
| `<Prefix> %` | `<Prefix> \|` | Split pane **horizontally** (side-by-side) |
| `<Prefix> "` | `<Prefix> -` | Split pane **vertically** (top-and-bottom) |
| `<Prefix> <Arrow>` | `Alt + h/j/k/l` | Navigate between panes |
| `<Prefix> z` | `<Prefix> z` or `<Prefix> m` | **Zoom** toggle (maximize/restore pane) |
| `<Prefix> x` | `<Prefix> x` | Close / kill current pane |
| `<Prefix> !` | `<Prefix> !` | Break current pane out into its own window |
| `<Prefix> {` / `}` | `<Prefix> {` / `}` | Swap current pane with previous / next pane |
| `<Prefix> q` | `<Prefix> q` | Show pane numbers briefly (type number to jump) |
| `<Prefix> Space` | `<Prefix> Space` | Cycle through preset pane layouts |
| `<Prefix> Ctrl+<Arrow>` | `<Prefix> H/J/K/L` | Resize current pane |

---

## 5. Copy Mode & Scrollback (Vi Mode)

| Keybinding | Action |
| :--- | :--- |
| `<Prefix> [` | Enter copy / scroll mode |
| `q` | Exit copy mode |
| `k` / `j` or `Up` / `Down` | Move up / down one line |
| `Ctrl + u` / `Ctrl + d` | Scroll half-page up / down |
| `Ctrl + b` / `Ctrl + f` | Scroll full-page up / down |
| `/` | Search forward in history |
| `?` | Search backward in history |
| `n` / `N` | Next / previous search match |
| `Space` (or `v` with custom config) | Begin text selection |
| `Enter` (or `y` with custom config) | Copy selection and exit copy mode |
| `<Prefix> ]` | Paste tmux buffer into current pane |
