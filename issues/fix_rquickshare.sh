#!/bin/bash
# fix_rquickshare.sh - Fix discovery issues for RQuickShare by setting a static port,
# configuring firewall rules, resetting Bluetooth, and restarting the service.

set -e

# Define paths
SETTINGS_FILE="$HOME/.local/share/dev.mandre.rquickshare/.settings.json"
LOG_FILE="$HOME/.local/share/dev.mandre.rquickshare/logs/RQuickShare.log"
PORT=42428

echo "[+] Stopping any running RQuickShare instances..."
pkill -x rquickshare || true
sleep 1

# 1. Update RQuickShare settings to use static port 42428
if [ -f "$SETTINGS_FILE" ]; then
    echo "[+] Setting static port $PORT in settings.json..."
    python3 -c '
import json, sys
path = sys.argv[1]
port = int(sys.argv[2])
with open(path, "r") as f:
    data = json.load(f)
data["port"] = port
# Ensure visibility is set to visible (0 is usually Everyone/Visible in rquickshare)
data["visibility"] = 0
data["autostart"] = False
with open(path, "w") as f:
    json.dump(data, f, indent=2)
' "$SETTINGS_FILE" "$PORT"
    echo "[+] Settings updated successfully."
else
    echo "[-] Warning: Settings file not found at $SETTINGS_FILE."
    echo "    Creating a new one..."
    mkdir -p "$(dirname "$SETTINGS_FILE")"
    cat <<EOF > "$SETTINGS_FILE"
{
  "realclose": false,
  "autostart": false,
  "visibility": 0,
  "startminimized": true,
  "port": 42428
}
EOF
fi

# 2. Check and configure UFW firewall
if which ufw >/dev/null 2>&1 && systemctl is-active --quiet ufw; then
    echo "[+] Configuring UFW rules for port $PORT and mDNS (5353)..."
    sudo ufw allow "$PORT/tcp" comment 'rquickshare data'
    sudo ufw allow "$PORT/udp" comment 'rquickshare data'
    sudo ufw allow 5353/udp comment 'rquickshare mDNS'
    sudo ufw reload
    echo "[+] UFW rules successfully applied."
else
    echo "[*] UFW firewall is not active or not installed. Skipping firewall rules configuration."
fi

# 3. Restart Bluetooth service and power cycle adapter to fix BLE advertisement errors
echo "[+] Restarting Bluetooth system daemon..."
sudo systemctl restart bluetooth
sleep 2

echo "[+] Power cycling the Bluetooth adapter..."
bluetoothctl power off
sleep 1
bluetoothctl power on
sleep 1

# 4. Start RQuickShare in background
echo "[+] Starting RQuickShare..."
nohup /usr/bin/rquickshare >/dev/null 2>&1 &
sleep 2

# 5. Check if RQuickShare successfully started and is listening on the configured port
if pgrep -f rquickshare >/dev/null; then
    echo "[+] RQuickShare is running."
    if [ -f "$LOG_FILE" ]; then
        echo "[+] Recent log entries:"
        tail -n 10 "$LOG_FILE"
    fi
else
    echo "[-] Error: Failed to start RQuickShare."
fi

echo "[+] Fixes completed! Please check if your laptop is visible on your Android phone."
