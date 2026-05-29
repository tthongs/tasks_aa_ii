#!/bin/bash

# Script to fix "Chrome didn't shut down properly" message
# It resets the exit_type flag and removes stale lock files.

PATHS=(
    "$HOME/.config/google-chrome"
    "$HOME/.config/BraveSoftware/Brave-Browser"
)

echo "Starting browser shutdown fix..."

for BASE_PATH in "${PATHS[@]}"; do
    if [ -d "$BASE_PATH" ]; then
        echo "Processing $BASE_PATH..."
        
        # 1. Reset exit_type in Preferences files
        find -L "$BASE_PATH" -name "Preferences" | while read -r pref_file; do
            echo "  Checking $pref_file"
            # Replace Crashed or SessionCrashed with Normal
            sed -i 's/"exit_type":"[^"]*"/"exit_type":"Normal"/' "$pref_file"
            # Ensure exited_cleanly is true if it exists
            sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' "$pref_file"
        done
        
        # 2. Remove SingletonLock files
        find "$BASE_PATH" -name "SingletonLock" -delete
        echo "  Stale lock files removed (if any)."
    fi
done

echo "Done. Browsers should now start without the 'restore' prompt."
