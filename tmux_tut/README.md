# Mastering tmux: From Fundamentals to Power User

Welcome to the tmux tutorial workspace! This repository contains a structured, practical curriculum to help you learn `tmux` (terminal multiplexer) and integrate it into your daily terminal workflow.

---

## Prerequisites: Installing tmux

tmux is not yet installed on this machine. Since you are on Arch Linux, install it using:

```bash
sudo pacman -S tmux
```

Optionally, install a clipboard utility for seamless copying from tmux to your desktop clipboard:
```bash
# If using Wayland:
sudo pacman -S wl-clipboard

# If using X11:
sudo pacman -S xclip
```

Verify installation:
```bash
tmux -V
```

---

## Learning Curriculum

Work through the modules in this order:

| Guide | Description | Key Takeaways |
| :--- | :--- | :--- |
| **[01_basics.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/01_basics.md)** | Core concepts & architecture | Sessions vs. Windows vs. Panes, the Prefix key, detaching/attaching |
| **[02_navigation_and_management.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/02_navigation_and_management.md)** | Window & Pane manipulation | Splitting, switching, resizing, zooming (`Prefix + z`), rearranging layouts |
| **[03_copy_mode.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/03_copy_mode.md)** | Scrollback & copy mode | Navigating history, Vi keybindings, searching, system clipboard integration |
| **[04_custom_config.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/04_custom_config.md)** | Modern configuration | Explaining [tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf), mouse mode, prefix remapping, plugins (TPM) |
| **[05_automation_scripting.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/05_automation_scripting.md)** | Scripting workspace layouts | Launching multi-pane development environments with a single command |
| **[practice_drills.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/practice_drills.md)** | Hands-on drills | 5 targeted challenges to build keyboard muscle memory |

---

## Quick Reference & Starter Config

- **[cheatsheet.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/cheatsheet.md)**: Fast lookup for all common commands and default keybindings.
- **[tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf)**: A clean, modern configuration file ready to use. You can test it immediately without altering system settings:
  ```bash
  tmux -f ./tmux.conf
  ```
