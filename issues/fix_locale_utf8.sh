#!/bin/bash
# Script to fix locale encoding in /etc/locale.conf by ensuring .UTF-8 is explicitly declared
# This resolves XKB Compose table lookup failures in KWin Wayland and Konsole.

set -euo pipefail

echo "[*] Current /etc/locale.conf:"
cat /etc/locale.conf
echo ""

echo "[*] Updating /etc/locale.conf with explicit .UTF-8 suffix..."
sudo tee /etc/locale.conf > /dev/null << 'EOF'
LANG=en_IN.UTF-8
LC_ADDRESS=en_IN.UTF-8
LC_IDENTIFICATION=en_IN.UTF-8
LC_MEASUREMENT=en_IN.UTF-8
LC_MONETARY=en_IN.UTF-8
LC_NAME=en_IN.UTF-8
LC_NUMERIC=en_IN.UTF-8
LC_PAPER=en_IN.UTF-8
LC_TELEPHONE=en_IN.UTF-8
LC_TIME=en_IN.UTF-8
EOF

echo "[*] Regenerating locales..."
sudo locale-gen

echo "[*] Verifying /etc/locale.conf:"
cat /etc/locale.conf

echo "[+] Locale configuration updated successfully."
