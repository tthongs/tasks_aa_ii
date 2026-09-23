# Chapter 4: Configuring tmux & Essential Plugins

tmux is extremely configurable. The configuration file lives at `~/.tmux.conf` (or `$XDG_CONFIG_HOME/tmux/tmux.conf`).

This repository includes a tested, modern configuration in [tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf).

---

## 1. Deep Dive: Key Settings Explained

### A. Terminal Colors & Escape Delay
```tmux
set -g default-terminal "tmux-256color"
set -as terminal-overrides ",xterm-256color:Tc"
set -s escape-time 0
```
- **24-bit True Color**: Ensures your terminal color schemes (e.g. Catppuccin, Gruvbox, TokyoNight) and syntax highlighting look identical inside tmux as outside.
- **Escape Time**: By default, tmux waits 500ms after an `Escape` key to check if it's an escape sequence. Setting `escape-time 0` makes switching modes in Vim/Neovim instantaneous.

### B. Ergonomic Indexing (Start at 1, not 0)
```tmux
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on
```
- The `0` key is on the far right of the number row, while `1` is on the far left. Starting windows and panes at `1` matches the physical layout of your hands.
- `renumber-windows on` ensures that if you close window 2 of [1, 2, 3], window 3 becomes window 2, leaving no gaps.

### C. Splitting in Current Directory
By default, creating a new window or pane starts in your home directory (`~`). This setting preserves your current directory:
```tmux
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
bind c new-window -c "#{pane_current_path}"
```

### D. Mouse Mode
```tmux
set -g mouse on
```
- Allows selecting panes and windows by clicking.
- Enables resizing pane borders by dragging.
- Enables mouse wheel scrolling directly into the history buffer.

> [!TIP]
> **Selecting with terminal mouse instead of tmux**:
> If you want to use your terminal emulator's native selection (for example, to copy text directly without tmux copy mode), hold `Shift` while dragging your mouse.

---

## 2. Testing & Reloading Configuration

You can reload your configuration immediately without killing your running sessions:
- Inside tmux: Press `<Prefix> r` (configured in our starter config).
- Or from shell:
  ```bash
  tmux source-file ~/.tmux.conf
  ```

---

## 3. Extending with TPM (Tmux Plugin Manager)

When you are comfortable with the basics, TPM allows installing community plugins easily.

### Installing TPM
```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

### Popular Community Plugins
Add these to the bottom of `~/.tmux.conf`:
```tmux
# List of plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'christoomey/vim-tmux-navigator' # Seamless Ctrl-h/j/k/l between Vim & tmux panes
set -g @plugin 'tmux-plugins/tmux-resurrect'    # Save and restore sessions across reboots
set -g @plugin 'tmux-plugins/tmux-continuum'    # Continuous automatic saving

# Initialize TMUX plugin manager (keep this line at the very bottom of tmux.conf)
run '~/.tmux/plugins/tpm/tpm'
```

### Installing the Plugins Inside tmux
Press `<Prefix> I` (capital `I`) inside tmux to fetch and install the plugins.
