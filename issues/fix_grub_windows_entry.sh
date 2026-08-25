#!/bin/bash
# fix_grub_windows_entry.sh - Renames GRUB boot entry from 'Windows Boot Manager' to 'Windows 11'
# MUST BE RUN WITH SUDO/ROOT PRIVILEGES.
#
# Usage: sudo ./fix_grub_windows_entry.sh

set -e

# 1. Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: Please run this script with sudo or as root."
    echo "    Usage: sudo $0"
    exit 1
fi

echo "[+] Starting GRUB Windows entry renaming..."

TIMESTAMP=$(date +%Y%m%d%H%M%S)
GRUB_OS_PROBER="/etc/grub.d/30_os-prober"
OS_PROBE_EFI_MS="/usr/lib/os-probes/mounted/efi/20microsoft"
GRUB_CFG="/boot/grub/grub.cfg"

# 2. Patch /etc/grub.d/30_os-prober
if [ -f "$GRUB_OS_PROBER" ]; then
    echo "[+] Backing up $GRUB_OS_PROBER to ${GRUB_OS_PROBER}.bak.${TIMESTAMP}..."
    cp "$GRUB_OS_PROBER" "${GRUB_OS_PROBER}.bak.${TIMESTAMP}"

    # Check if already patched
    if grep -q 'LONGNAME="Windows 11"' "$GRUB_OS_PROBER"; then
        echo "[*] $GRUB_OS_PROBER already contains Windows 11 override rule."
    else
        echo "[+] Patching $GRUB_OS_PROBER to map 'Windows Boot Manager' -> 'Windows 11'..."
        python3 -c '
file_path = "/etc/grub.d/30_os-prober"
with open(file_path, "r") as f:
    content = f.read()

target = """  if [ -z "${LONGNAME}" ] ; then
    LONGNAME="${LABEL}"
  fi"""

replacement = """  if [ -z "${LONGNAME}" ] ; then
    LONGNAME="${LABEL}"
  fi

  if [ "${LONGNAME}" = "Windows Boot Manager" ]; then
    LONGNAME="Windows 11"
  fi"""

if target in content:
    new_content = content.replace(target, replacement, 1)
    with open(file_path, "w") as f:
        f.write(new_content)
    print("    [+] Successfully patched /etc/grub.d/30_os-prober.")
else:
    print("    [!] Warning: Target anchor not found in /etc/grub.d/30_os-prober. Skipping python patch.")
'
        chmod 755 "$GRUB_OS_PROBER"
    fi
else
    echo "[-] Error: $GRUB_OS_PROBER not found."
    exit 1
fi

# 3. Patch /usr/lib/os-probes/mounted/efi/20microsoft if present
if [ -f "$OS_PROBE_EFI_MS" ]; then
    echo "[+] Backing up $OS_PROBE_EFI_MS to ${OS_PROBE_EFI_MS}.bak.${TIMESTAMP}..."
    cp "$OS_PROBE_EFI_MS" "${OS_PROBE_EFI_MS}.bak.${TIMESTAMP}"

    if grep -q 'long="Windows 11"' "$OS_PROBE_EFI_MS"; then
        echo "[*] $OS_PROBE_EFI_MS already configured for 'Windows 11'."
    elif grep -q 'long="Windows Boot Manager"' "$OS_PROBE_EFI_MS"; then
        echo "[+] Updating default EFI probe description in $OS_PROBE_EFI_MS..."
        sed -i 's/long="Windows Boot Manager"/long="Windows 11"/' "$OS_PROBE_EFI_MS"
        chmod 755 "$OS_PROBE_EFI_MS"
        echo "    [+] Updated $OS_PROBE_EFI_MS."
    fi
fi

# 4. Regenerate GRUB Configuration
echo "[+] Regenerating GRUB configuration (/boot/grub/grub.cfg)..."
grub-mkconfig -o "$GRUB_CFG"

# 5. Verification
echo "[+] Verifying GRUB configuration for 'Windows 11'..."
if grep -i "menuentry.*Windows 11" "$GRUB_CFG"; then
    echo "[+] SUCCESS: Verified Windows 11 boot entry in $GRUB_CFG:"
    grep -n -C 2 -i "menuentry.*Windows 11" "$GRUB_CFG"
else
    echo "[!] Warning: 'Windows 11' string was not found in generated $GRUB_CFG."
    echo "    Check if os-prober is enabled in /etc/default/grub (GRUB_DISABLE_OS_PROBER=false)."
fi

echo "[+] GRUB Windows entry update completed successfully."
