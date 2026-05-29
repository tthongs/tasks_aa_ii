# [BUG] Browsers (Chrome/Brave) consistently show "did not shut down properly"

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: ~/.config/google-chrome/, ~/.config/BraveSoftware/Brave-Browser/

## Description
Chrome and Brave browsers consistently report an unclean shutdown upon startup,
displaying a "Restore" button. This is caused by the `exit_type` flag being
stuck on `Crashed` or the presence of stale `SingletonLock` files.

## Steps to Reproduce
1. Open Google Chrome or Brave Browser.
2. Observe the "Restore pages? Chrome didn't shut down properly" notification.

## Proposed Solution / Action Items
- [x] Create a script to reset `exit_type` to `Normal` in all `Preferences` files.
- [x] Ensure `SingletonLock` files are removed if the browser is not running.
- [x] Provide a way to automate this (e.g., a shell alias or a login script).

## Resolution
Created `fix_browser_shutdown.sh` which uses `sed` to reset flags and `find` to
remove lock files. Added `fix_browser_shutdown.desktop` for autostart integration.

## Verification
Ran `fix_browser_shutdown.sh` and verified that `"exit_type":"Crashed"` was
changed to `"exit_type":"Normal"` in `~/.config/google-chrome/Default/Preferences`.
Confirmed the script handles symlinked profile directories correctly.
