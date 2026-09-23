# Practice Drills: Building tmux Muscle Memory

Terminal efficiency is entirely about muscle memory. Complete these 5 drills in order once you have tmux installed.

---

## Drill 1: The "Disconnect & Reconnect" Dance (Sessions)

**Goal**: Experience session persistence firsthand.

1. Start a named session:
   ```bash
   tmux new -s drill1
   ```
2. In the session, launch a long-running process (e.g. counting seconds):
   ```bash
   for i in {1..1000}; do echo "Count: $i"; sleep 1; done
   ```
3. Detach from the session without stopping the count:
   - Press `<Prefix>` (default: `Ctrl + b`), release, then press `d`.
   - Notice you are back in your standard terminal, but the counter is still ticking in the background.
4. Check running sessions:
   ```bash
   tmux ls
   ```
5. Reattach to `drill1`:
   ```bash
   tmux a -t drill1
   ```
   - Notice the count has advanced!
6. Stop the loop (`Ctrl + c`), type `exit` to close the session.

---

## Drill 2: The Multi-Pane Grid (Splitting & Navigation)

**Goal**: Split screens and jump between them smoothly.

1. Start a session:
   ```bash
   tmux new -s drill2
   ```
2. Split vertically (stacked): `<Prefix> "` (or `<Prefix> -` with custom config).
3. Split the bottom pane horizontally (side-by-side): `<Prefix> %` (or `<Prefix> |`).
4. You should now have 3 panes: 1 wide top pane, 2 side-by-side bottom panes.
5. Move between panes:
   - Use `<Prefix> <Arrow>` (or `Alt + h/j/k/l`).
6. Cycle layout presets:
   - Press `<Prefix> Space` several times to watch tmux automatically rearrange the 3 panes into even columns, even rows, and grids.
7. Close panes one by one with `<Prefix> x` until session exits.

---

## Drill 3: The Zoom & Breakout (Focus Management)

**Goal**: Read crowded output without losing your multi-pane layout.

1. Start a session and create 4 panes (split in half, then split each half).
2. In one small corner pane, run a command with wide output:
   ```bash
   ip -br addr || ls -la /usr/bin
   ```
3. The pane is too small to read the output clearly.
4. Press `<Prefix> z` to **zoom** (maximize) the pane.
5. Notice the `*Z` indicator in the status bar. Read your output comfortably.
6. Press `<Prefix> z` again to restore the 4-pane grid.
7. Break the active pane into its own separate window: Press `<Prefix> !`.
8. Switch back to the previous window: `<Prefix> p`.
9. Kill the session: `tmux kill-session -t drill2` (from inside or outside).

---

## Drill 4: Copy Mode Detective (History & Search)

**Goal**: Navigate history, search, and copy text without touching your mouse.

1. Start a session:
   ```bash
   tmux new -s drill4
   ```
2. Generate 200 lines of test text:
   ```bash
   seq 1 200 | sed 's/142/FOUND_THE_SECRET_KEY/'
   ```
3. The secret string has scrolled off your screen.
4. Enter copy mode: Press `<Prefix> [`.
5. Search backwards for the secret:
   - Press `?` (or `/` to search forwards if at the top).
   - Type `SECRET` and hit `Enter`.
   - Your cursor jumps straight to `FOUND_THE_SECRET_KEY`!
6. Highlight and copy the text:
   - Press `Space` (or `v` in vi mode) to begin selection.
   - Use arrow keys or `w` to highlight the word.
   - Press `Enter` (or `y`) to copy.
7. Paste the copied secret into your prompt:
   - Press `<Prefix> ]`.
8. Exit the session (`exit`).

---

## Drill 5: Building a Dev Layout (Windows & Structure)

**Goal**: Build a multi-window development workspace from scratch.

1. Start session `dev`:
   ```bash
   tmux new -s dev
   ```
2. Rename window 1 to `code`:
   - Press `<Prefix> ,` -> type `code` -> press `Enter`.
3. Create window 2:
   - Press `<Prefix> c`.
4. Rename window 2 to `server`:
   - Press `<Prefix> ,` -> type `server` -> press `Enter`.
5. Split window 2 into side-by-side panes: `<Prefix> %`.
6. Open the interactive window tree:
   - Press `<Prefix> w`.
   - Use arrow keys or `j`/`k` to preview each window and pane.
   - Press `Enter` to jump directly into the highlighted pane.
7. Clean up: `<Prefix> d` to detach, then `tmux kill-session -t dev`.
