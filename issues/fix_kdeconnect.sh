#!/usr/bin/env bash
# ==============================================================================
# Fix & Enable KDE Connect Firewall Configuration and Discovery
# ==============================================================================

set -euo pipefail

# Ensure script is run with sudo/root privileges for ufw modifications
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: Please run this script with sudo or as root."
    exit 1
fi

echo "[*] Configuring UFW rules for KDE Connect (ports 1714:1764 TCP/UDP)..."
ufw allow "KDE Connect" comment 'KDE Connect'
ufw reload

echo "[*] UFW Status:"
ufw status verbose

REAL_USER="${SUDO_USER:-$USER}"
if [ -n "${SUDO_USER:-}" ] && [ "$REAL_USER" != "root" ]; then
    echo "[*] Refreshing KDE Connect device list for user $REAL_USER..."
    sudo -u "$REAL_USER" kdeconnect-cli --refresh || true
    sleep 2
    sudo -u "$REAL_USER" kdeconnect-cli -l || true
fi

echo "[+] KDE Connect firewall setup completed successfully."
