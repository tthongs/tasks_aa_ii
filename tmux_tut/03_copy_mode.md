# Chapter 3: Scrollback, Copy Mode & Clipboard

One of the first surprises for tmux newcomers is: **"Why doesn't my mouse wheel or Shift+PageUp scroll terminal history?"**

In tmux, every pane maintains its own independent scrollback history buffer. To scroll back, search text, or select and copy output without using the mouse, tmux provides **Copy Mode**.

---

## 1. Entering & Exiting Copy Mode

- **Enter Copy Mode**:
  ```
  <Prefix> [
  ```
  You will see an indicator in the top-right corner of the pane showing your position in history (e.g. `[0/500]`).
- **Exit Copy Mode**: Press `q` or `Esc`.

> [!TIP]
> With `set -g mouse on` enabled in your `tmux.conf`, you can also enter copy mode simply by scrolling up with your mouse wheel or dragging to select text.

---

## 2. Navigating in Copy Mode (Vi Mode)

By setting `setw -g mode-keys vi` in `tmux.conf`, copy mode uses standard Vim keybindings:

### Moving the Cursor
| Key | Action |
| :--- | :--- |
| `h` / `j` / `k` / `l` | Left / Down / Up / Right |
| `w` / `b` | Forward / Backward by word |
| `0` / `$` | Start / End of current line |
| `g` | Jump to the very top (oldest line in buffer) |
| `G` | Jump to the bottom (most recent line) |
| `Ctrl + u` | Scroll half-page UP |
| `Ctrl + d` | Scroll half-page DOWN |
| `Ctrl + b` | Scroll full-page UP |
| `Ctrl + f` | Scroll full-page DOWN |

---

## 3. Searching History

Just like in Vim or `less`:
1. Press `/` to search **downward** or `?` to search **upward**.
2. Type your search term and press `Enter`.
3. Press `n` to jump to the **next** match.
4. Press `N` to jump to the **previous** match.

---

## 4. Selecting & Copying Text

### The Standard tmux Workflow
1. Enter copy mode: `<Prefix> [`
2. Move cursor to the start of the text you want.
3. Press `Space` (or `v` if configured with Vi bindings) to start highlighting.
4. Move cursor with `h/j/k/l` or `w/b` to cover the text.
5. Press `Enter` (or `y` if configured) to copy the text into tmux's internal buffer.
6. The copy mode automatically closes.

### Pasting Copied Text
To paste what you copied into any tmux pane:
```
<Prefix> ]
```

### Listing and Pasting Previous Buffers
tmux keeps a history of multiple copied buffers:
- Open buffer selector: `<Prefix> =`
- Choose a buffer from the list to paste it directly.

---

## 5. Integrating with the System Clipboard

By default, tmux copies into its own internal buffer, not your desktop clipboard (X11 or Wayland).

In our [tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf), we automatically bridge tmux to `wl-copy` (Wayland) or `xclip` (X11):

```tmux
# In tmux.conf:
if-shell 'command -v wl-copy >/dev/null 2>&1' \
  'bind -T copy-mode-vi y send -X copy-pipe-and-cancel "wl-copy"' \
  'if-shell "command -v xclip >/dev/null 2>&1" \
     "bind -T copy-mode-vi y send -X copy-pipe-and-cancel \"xclip -selection clipboard -in\"" \
     "bind -T copy-mode-vi y send -X copy-selection-and-cancel"'
```

With this configured:
- Pressing `y` in copy mode will copy directly to your system clipboard so you can `Ctrl + v` in your browser or any desktop application.
