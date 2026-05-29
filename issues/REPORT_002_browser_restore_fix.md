# Report: Fixing Persistent Browser Session Restore Prompts

## Overview
Users reported that Google Chrome and Brave Browser consistently displayed a 
"Chrome didn't shut down properly" notification with a "Restore" button upon 
every startup, even after a normal system shutdown.

## Root Cause Analysis
The issue was traced to the `exit_type` flag within the browser's `Preferences` 
JSON files. 
- **Flag State**: The flag was stuck at `"exit_type":"Crashed"`.
- **System Configuration**: The user's browser config directories 
  (`~/.config/google-chrome`) were found to be symlinks to a RAM-based profile 
  (likely managed by **Profile Sync Daemon**). This can sometimes lead to 
  improper sync-back or lock file cleanup during shutdown.
- **Lock Files**: Presence of `SingletonLock` files also contributed to the 
  browser thinking it was still "in use" or crashed.

## Implementation: fix_browser_shutdown.sh
A bash script was developed to automate the cleanup of these flags and files. 
It utilizes `find -L` to follow symlinks and `sed` to perform surgical edits 
on the JSON configuration.

```bash
#!/bin/bash
# Paths to browser config roots
PATHS=(
    "$HOME/.config/google-chrome"
    "$HOME/.config/BraveSoftware/Brave-Browser"
)

for BASE_PATH in "${PATHS[@]}"; do
    if [ -d "$BASE_PATH" ]; then
        # Reset exit_type and exited_cleanly flags
        find -L "$BASE_PATH" -name "Preferences" | while read -r pref_file; do
            sed -i 's/"exit_type":"[^"]*"/"exit_type":"Normal"/' "$pref_file"
            sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' \
                "$pref_file"
        done
        # Remove stale lock files
        find -L "$BASE_PATH" -name "SingletonLock" -delete
    fi
done
```

## Automation Strategy
To ensure the fix is permanent and hands-off, a Desktop Autostart entry was 
created:
- **File**: `~/.config/autostart/fix_browser_shutdown.desktop`
- **Behavior**: Executes the fix script immediately upon user login, ensuring 
  the browser state is clean before the user opens any applications.

## Verification
1.  Verified that `exit_type` in `Default/Preferences` changed from `Crashed` 
    to `Normal` after script execution.
2.  Confirmed that the script successfully traverses symlinked directories 
    to locate the actual configuration files.
3.  Confirmed the autostart entry is correctly placed in the user's config.
