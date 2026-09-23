# Chapter 2: Navigation & Pane/Window Management

Once inside a tmux session, the core day-to-day workflow revolves around manipulating windows (tabs) and panes (splits).

---

## 1. Understanding Panes (Splits)

> [!NOTE]
> **tmux Terminology Note**:
> - A **horizontal split** in tmux docs (`split-window -h` / `%`) divides the current pane left-and-right (producing vertical divider lines).
> - A **vertical split** (`split-window -v` / `"`) divides the current pane top-and-bottom (producing horizontal divider lines).
>
> In our [tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf), we remap these to `|` (side-by-side) and `-` (stacked) to avoid confusion.

### Splitting Panes
- **Default keys**:
  - `<Prefix> %` : Split horizontally (side-by-side)
  - `<Prefix> "` : Split vertically (stacked)
- **Custom keys** (with our config):
  - `<Prefix> |` : Split side-by-side
  - `<Prefix> -` : Split stacked

### Navigating Between Panes
- **Default**: `<Prefix> <Arrow Key>`
- **With our config**: `Alt + h / j / k / l` (no prefix needed!) or `<Prefix> h / j / k / l`
- **Show Pane Numbers**: `<Prefix> q` (displays large numbers over each pane; type the number to jump directly to it).

### Resizing Panes
- **Default**: Press and hold `<Prefix>`, then press `Ctrl + <Arrow Key>`.
- **With our config**: `<Prefix> Shift + H / J / K / L` (resizes in 5-cell increments).

### The Killer Feature: Zooming a Pane (`<Prefix> z`)
When you are looking at long logs, running a debugger, or reading code in Neovim across a small pane:
1. Press `<Prefix> z` to temporarily maximize the active pane to fill the entire window.
2. Notice the `*Z` indicator in the window status line.
3. Press `<Prefix> z` again to restore the exact multi-pane layout.

### Closing and Moving Panes
- **Close active pane**: `<Prefix> x` (confirms with `y/n`) or just type `exit`.
- **Break pane into its own window**: `<Prefix> !` (promotes the active pane to a brand new window).
- **Swap panes**:
  - `<Prefix> {` : Swap current pane with previous pane.
  - `<Prefix> }` : Swap current pane with next pane.

### Cycling Layouts
Press `<Prefix> Space` repeatedly to cycle through tmux's built-in layout engines:
- `even-horizontal` (all columns)
- `even-vertical` (all rows)
- `main-horizontal` (large top pane, small bottom panes)
- `main-vertical` (large left pane, small right panes)
- `tiled` (grid)

---

## 2. Managing Windows (Tabs)

Windows represent separate screens inside the same session.

### Window Operations
| Keybinding | Action |
| :--- | :--- |
| `<Prefix> c` | Create a new window |
| `<Prefix> ,` | **Rename** current window (e.g., `api`, `tests`, `db`) |
| `<Prefix> n` | Switch to Next window |
| `<Prefix> p` | Switch to Previous window |
| `<Prefix> <number>` | Jump immediately to window number (e.g. `<Prefix> 1`) |
| `<Prefix> w` | Open interactive visual tree of all sessions and windows |
| `<Prefix> l` | Toggle back to the last active window |
| `<Prefix> &` | Kill current window and all its panes |

---

## 3. Workflow Pro-Tip: Naming Matters!

Keep your workspace tidy by naming sessions and windows:
- Rename session: `<Prefix> $`
- Rename window: `<Prefix> ,`

A clean status bar like `[proj-api] 1:nvim* 2:server 3:logs` is significantly faster to navigate than `[0] 1:bash* 2:bash 3:bash`.
