# [TASK] Configure Bash-Insulter to Insult on Every Command Not Found Error

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: `/home/tthhongs/build_tthongs/bash-insulter`, `~/.bashrc`, `~/.zshrc`

## Description
The user configured `bash-insulter` in `~/build_tthongs/bash-insulter`, but by default upstream `bash-insulter` only outputs insults ~50% of the time (`if [[ $((${RANDOM} % 2)) -lt 1 ]]`). The user requested configuring the handler so that on 100% of command-not-found errors, an insult is printed.

## Configuration & Changes
- **Source Script**: `/home/tthhongs/build_tthongs/bash-insulter/src/bash.command-not-found`
- **Logic Modification**: Removed the modulo random gate (`if [[ $((${RANDOM} % 2)) -lt 1 ]]`) in `print_message()` so that every command triggering `command_not_found_handle` (Bash) or `command_not_found_handler` (Zsh) reliably prints a bold red insult to `stderr`.
- **Shell Configuration**:
  - `~/.bashrc`: Verified persistent sourcing from `$HOME/build_tthongs/bash-insulter/src/bash.command-not-found`.
  - `~/.zshrc`: Added conditional sourcing block for seamless behavior when running `zsh`.

## Proposed Solution / Action Items
- [x] **Modified `print_message` in `bash.command-not-found`**: Removed 50% probability check to ensure 100% trigger rate.
- [x] **Verified Shell Startup Scripts**: Confirmed `~/.bashrc` loads the handler and configured `~/.zshrc` to match.
- [x] **Verified Across Shells**: Tested invalid commands under both `bash` and `zsh` subshells.
- [x] **Documented Commands**: Appended Section 17 to `unix_issues_cmds.txt`.
- [x] **Updated GEMINI.md**: Added `ISSUE_020` to repository issue tracker.

## Verification
- Ran multiple consecutive invalid commands in `bash -c`: Verified 3/3 insults returned before command-not-found output.
- Ran multiple consecutive invalid commands in `zsh -c`: Verified 3/3 insults returned before command-not-found output.
