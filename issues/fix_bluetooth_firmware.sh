#!/bin/bash
# fix_bluetooth_firmware.sh - Decompress MediaTek MT7922 Bluetooth firmware
# and reload the driver to restore full BLE functionality.
#
# MUST BE RUN WITH SUDO/ROOT PRIVILEGES.

set -e

# 1. Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: Please run this script with sudo or as root."
    exit 1
fi

echo "[+] Starting Bluetooth firmware fixes..."

FIRMWARE_DIR="/lib/firmware/mediatek"
ZST_FILE="$FIRMWARE_DIR/BT_RAM_CODE_MT7922_1_1_hdr.bin.zst"
BIN_FILE="$FIRMWARE_DIR/BT_RAM_CODE_MT7922_1_1_hdr.bin"

# 2. Decompress firmware if missing
if [ -f "$ZST_FILE" ]; then
    if [ ! -f "$BIN_FILE" ]; then
        echo "[+] Decompressing $ZST_FILE..."
        zstd -d --keep "$ZST_FILE" -o "$BIN_FILE"
        chmod 644 "$BIN_FILE"
        echo "[+] Firmware successfully decompressed to $BIN_FILE."
    else
        echo "[*] Uncompressed firmware file already exists at $BIN_FILE."
    fi
else
    echo "[-] Error: ZSTD firmware file not found at $ZST_FILE."
    exit 1
fi

# 3. Stop Bluetooth system service
echo "[+] Stopping Bluetooth system service..."
systemctl stop bluetooth
sleep 1

# 4. Unload and reload kernel modules to load the new firmware
echo "[+] Reloading btusb kernel module..."
if lsmod | grep -q "^btusb"; then
    modprobe -r btusb
    sleep 1
fi
modprobe btusb
sleep 1

# 5. Start Bluetooth system service
echo "[+] Starting Bluetooth system service..."
systemctl start bluetooth
sleep 1

# 6. Restart RQuickShare if it was running
if pgrep -x rquickshare >/dev/null; then
    echo "[+] Restarting RQuickShare..."
    pkill -x rquickshare || true
    sleep 1
    
    # Run RQuickShare as the original user who ran sudo
    REAL_USER="${SUDO_USER:-$USER}"
    if [ -n "$SUDO_USER" ] && [ "$REAL_USER" != "root" ]; then
        echo "[+] Launching RQuickShare as user '$REAL_USER'..."
        USER_UID=$(id -u "$REAL_USER")
        sudo -u "$REAL_USER" \
            DISPLAY=:0 \
            DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_UID/bus" \
            nohup /usr/bin/rquickshare >/dev/null 2>&1 &
    else
        echo "[+] Launching RQuickShare..."
        nohup /usr/bin/rquickshare >/dev/null 2>&1 &
    fi
else
    echo "[*] RQuickShare is not currently running. Skipping restart."
fi

echo "[+] Fixes completed! You can check status with: systemctl status bluetooth"
echo "[*] Check dmesg logs: sudo dmesg | grep -i -E 'blue|hci'"
