# The Interactive tmux Tutorial (`tut.md`)

Welcome to your hands-on guide to mastering **tmux** (Terminal Multiplexer).

This tutorial is divided into 7 sequential, bite-sized lessons with practical exercises you can execute directly in your terminal.

---

## Table of Contents
1. [Lesson 1: Verification & First Launch](#lesson-1-verification--first-launch)
2. [Lesson 2: The Prefix Key & Status Bar Anatomy](#lesson-2-the-prefix-key--status-bar-anatomy)
3. [Lesson 3: Panes — Splitting, Moving, and Zooming](#lesson-3-panes--splitting-moving-and-zooming)
4. [Lesson 4: Windows — Creating and Navigating Tabs](#lesson-4-windows--creating-and-navigating-tabs)
5. [Lesson 5: Sessions — The Magic of Detach & Reattach](#lesson-5-sessions--the-magic-of-detach--reattach)
6. [Lesson 6: Copy Mode — Scrollback, Search & Vi Mode](#lesson-6-copy-mode--scrollback-search--vi-mode)
7. [Lesson 7: Custom Config & Next Steps](#lesson-7-custom-config--next-steps)

---

## Lesson 1: Verification & First Launch

### 1.1 Verify Installation
Before starting, ensure `tmux` is installed:
```bash
tmux -V
```
If not installed, install it via:
```bash
sudo pacman -S tmux
```

### 1.2 Starting tmux
Start a new tmux session loaded with our starter configuration:
```bash
tmux -f /home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf new -s tutorial
```
*(Or simply run `tmux` if using system defaults).*

You will immediately notice a status bar appear at the bottom of your terminal screen. You are now inside a tmux session!

---

## Lesson 2: The Prefix Key & Status Bar Anatomy

### 2.1 The Concept of the Prefix Key
Because tmux runs inside your shell, typing keys like `c` or `d` would normally type letters into your shell. To tell tmux *"Hey, this next key is a tmux shortcut"*, you must first send the **Prefix Key**.

- **Default Prefix**: `Ctrl + b` (written as `<Prefix>` or `C-b`).
- **How to execute a shortcut**:
  1. Hold down `Ctrl` and press `b`.
  2. Release **both** keys.
  3. Press the target action key (e.g., `c`, `d`, `%`).

### 2.2 Status Bar Anatomy
Look at the bar at the bottom:
```
[tutorial]  1:bash*                            15:30 | 23-Sep-26 archlinux
  ▲          ▲                                              ▲
  │          │                                              │
Session   Window # & Name                            System info & time
 Name    (* indicates active window)
```

---

## Lesson 3: Panes — Splitting, Moving, and Zooming

A **pane** is an individual pseudo-terminal inside your current window.

### Step 3.1: Split the screen
Try both splits now:
1. **Vertical split (side-by-side)**:
   - Default: Press `<Prefix>`, release, then press `%` (`Shift + 5`).
   - With our config: Press `<Prefix>`, release, then press `|` (`Shift + \`).
2. **Horizontal split (stacked)**:
   - Default: Press `<Prefix>`, release, then press `"` (`Shift + '`).
   - With our config: Press `<Prefix>`, release, then press `-`.

You should now see 3 distinct terminal panes on a single screen!

### Step 3.2: Move Between Panes
- **Default**: `<Prefix>` followed by arrow keys (`Up`, `Down`, `Left`, `Right`).
- **With our config**: `Alt + h` (Left), `Alt + j` (Down), `Alt + k` (Up), `Alt + l` (Right) — no prefix needed!
- **Show Pane Numbers**: Press `<Prefix> q`. Numbers will flash over each pane. Press `0`, `1`, etc., while numbers are visible to jump straight to that pane.

### Step 3.3: The Power Feature — Zooming (`<Prefix> z`)
When you are working across multiple panes and need full-screen space:
1. Navigate to any small pane.
2. Run `top` or `htop`.
3. Press `<Prefix> z`. The pane expands to fill the entire window! Notice the `*Z` flag in the status bar.
4. Press `<Prefix> z` again. Your original multi-pane layout is restored intact!

### Step 3.4: Closing a Pane
Move to a pane you want to close and either:
- Type `exit` and hit `Enter`, or
- Press `<Prefix> x` and confirm with `y`.

---

## Lesson 4: Windows — Creating and Navigating Tabs

Think of a **window** as a full desktop workspace or a browser tab containing its own set of panes.

### Step 4.1: Create a New Window
Press:
```
<Prefix> c
```
A new blank shell opens, and the status bar updates to show `1:bash 2:bash*`.

### Step 4.2: Rename the Window
Press:
```
<Prefix> ,
```
The status bar switches to an edit prompt. Clear `bash`, type `editor`, and press `Enter`.

### Step 4.3: Switch Between Windows
- Jump by number: `<Prefix> 1` or `<Prefix> 2`.
- Next / Previous: `<Prefix> n` (Next) or `<Prefix> p` (Previous).
- Interactive Window Tree: Press `<Prefix> w`.
  - Use `j`/`k` or arrow keys to browse all windows and panes.
  - Press `Enter` to jump to whichever one you highlight.

---

## Lesson 5: Sessions — The Magic of Detach & Reattach

A **session** encapsulates all windows and panes. It runs inside a background server daemon that persists even if your terminal closes or SSH drops.

### Step 5.1: Start a Background Counter
In your active window, start a continuous task:
```bash
for i in $(seq 1 1000); do echo "Tick $i"; sleep 1; done
```
You should see ticks printing every second.

### Step 5.2: Detach
Now, leave the session without killing the task:
Press:
```
<Prefix> d
```
You are back at your original terminal prompt outside tmux! Notice the message:
`[detached (from session tutorial)]`

### Step 5.3: Check Running Sessions
Run in your shell:
```bash
tmux ls
```
You will see:
```
tutorial: 2 windows (created ...)
```

### Step 5.4: Reattach
Re-enter your session:
```bash
tmux attach -t tutorial
```
Notice your loop is still counting smoothly at `Tick 25... Tick 26...`! Hit `Ctrl + c` to stop it.

---

## Lesson 6: Copy Mode — Scrollback, Search & Vi Mode

Because tmux takes over terminal display rendering, standard terminal mouse scrolling can be tricky without Copy Mode.

### Step 6.1: Enter Copy Mode
Press:
```
<Prefix> [
```
A position indicator appears in the top-right corner: e.g., `[0/120]`.

### Step 6.2: Navigate History
With Vi mode active (`setw -g mode-keys vi`):
- `k` / `j`: Move up / down one line.
- `Ctrl + u`: Half-page up.
- `Ctrl + d`: Half-page down.
- `g`: Jump to the very beginning of the buffer.
- `G`: Jump to the bottom of the buffer.

### Step 6.3: Search
- Press `?` (search upward) or `/` (search downward).
- Type a search query (e.g., `Tick`) and press `Enter`.
- Press `n` for next match, `N` for previous match.

### Step 6.4: Copy and Paste
1. Move the cursor to where you want to start copying.
2. Press `Space` (or `v` in vi mode).
3. Move cursor to highlight the desired text.
4. Press `Enter` (or `y` with custom config) to copy.
5. Exit copy mode automatically.
6. Paste anywhere with:
   ```
   <Prefix> ]
   ```

---

## Lesson 7: Custom Config & Next Steps

### 7.1 Inspect Your Starter Config
Take a look at the annotated configuration file provided in this workspace:
- File: [tmux.conf](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf)

To make it your default configuration for all future sessions:
```bash
cp /home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/tmux.conf ~/.tmux.conf
```

### 7.2 Run Automated Dev Environments
Inspect and test the automated launcher script:
- Script: [example_dev_env.sh](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/example_dev_env.sh)

Run it with:
```bash
./example_dev_env.sh
```

### 7.3 Reference Materials
- Complete quick reference: [cheatsheet.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/cheatsheet.md)
- Hands-on drills: [practice_drills.md](file:///home/tthhongs/build_tthongs/tasks_aa_ii/tmux_tut/practice_drills.md)
