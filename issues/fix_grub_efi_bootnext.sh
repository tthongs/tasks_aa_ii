#!/bin/bash
# fix_grub_efi_bootnext.sh - Disables automatic EFI BootNext entries in GRUB boot menu
# MUST BE RUN WITH SUDO/ROOT PRIVILEGES.
#
# Usage: sudo ./fix_grub_efi_bootnext.sh

set -e

# 1. Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: Please run this script with sudo or as root."
    echo "    Usage: sudo $0"
    exit 1
fi

echo "[+] Starting EFI BootNext removal from GRUB..."

TIMESTAMP=$(date +%Y%m%d%H%M%S)
GRUB_DEFAULT="/etc/default/grub"
GRUB_BOOTNEXT_SCRIPT="/etc/grub.d/31_efi_bootnext"
GRUB_CFG="/boot/grub/grub.cfg"

# 2. Backup /etc/default/grub
if [ -f "$GRUB_DEFAULT" ]; then
    echo "[+] Backing up $GRUB_DEFAULT to ${GRUB_DEFAULT}.bak.${TIMESTAMP}..."
    cp "$GRUB_DEFAULT" "${GRUB_DEFAULT}.bak.${TIMESTAMP}"

    # Check if GRUB_DISABLE_BOOTNEXT already exists
    if grep -q "^GRUB_DISABLE_BOOTNEXT=" "$GRUB_DEFAULT"; then
        echo "[*] Updating existing GRUB_DISABLE_BOOTNEXT in $GRUB_DEFAULT to true..."
        sed -i 's/^GRUB_DISABLE_BOOTNEXT=.*/GRUB_DISABLE_BOOTNEXT=true/' "$GRUB_DEFAULT"
    elif grep -q "^#GRUB_DISABLE_BOOTNEXT=" "$GRUB_DEFAULT"; then
        echo "[*] Uncommenting and setting GRUB_DISABLE_BOOTNEXT=true in $GRUB_DEFAULT..."
        sed -i 's/^#GRUB_DISABLE_BOOTNEXT=.*/GRUB_DISABLE_BOOTNEXT=true/' "$GRUB_DEFAULT"
    else
        echo "[+] Adding GRUB_DISABLE_BOOTNEXT=true to $GRUB_DEFAULT..."
        echo "" >> "$GRUB_DEFAULT"
        echo "# Disable automatic EFI BootNext menu entries introduced in GRUB 2.16" >> "$GRUB_DEFAULT"
        echo "GRUB_DISABLE_BOOTNEXT=true" >> "$GRUB_DEFAULT"
    fi
else
    echo "[-] Error: $GRUB_DEFAULT not found!"
    exit 1
fi

# 3. Disable execute permission on /etc/grub.d/31_efi_bootnext as an extra safeguard
if [ -f "$GRUB_BOOTNEXT_SCRIPT" ]; then
    echo "[+] Disabling execute permission on $GRUB_BOOTNEXT_SCRIPT..."
    chmod -x "$GRUB_BOOTNEXT_SCRIPT"
fi

# 4. Check if user also wants to restore Windows 11 naming from ISSUE_021
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WINDOWS_FIX="$SCRIPT_DIR/fix_grub_windows_entry.sh"
if [ -f "$WINDOWS_FIX" ] && ! grep -q 'LONGNAME="Windows 11"' /etc/grub.d/30_os-prober 2>/dev/null; then
    echo "[*] Note: /etc/grub.d/30_os-prober was reset by the GRUB update."
    echo "[+] Re-applying Windows 11 boot entry patch..."
    bash "$WINDOWS_FIX" || true
fi

# 5. Regenerate GRUB configuration
echo "[+] Regenerating GRUB configuration ($GRUB_CFG)..."
grub-mkconfig -o "$GRUB_CFG"

# 6. Verification
echo "[+] Verifying configuration..."
if grep -q "EFI BootNext" "$GRUB_CFG" 2>/dev/null; then
    echo "[!] Warning: 'EFI BootNext' entries were still found in $GRUB_CFG."
    exit 1
else
    echo "[✓] Success: All 'EFI BootNext' entries have been removed from GRUB!"
fi
