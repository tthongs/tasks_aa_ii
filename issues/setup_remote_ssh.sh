#!/usr/bin/env bash
# ==============================================================================
# setup_remote_ssh.sh - Configure OpenSSH Server, Firewall, and Remote Access
# ==============================================================================
# Usage:
#   sudo ./setup_remote_ssh.sh [--tailscale]
# ==============================================================================

set -euo pipefail

# 1. Root Privilege Verification
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: Please run this script with sudo or as root:"
    echo "    sudo $0 $*"
    exit 1
fi

TARGET_USER="${SUDO_USER:-$USER}"
if [ "$TARGET_USER" = "root" ]; then
    TARGET_USER="tthhongs"
fi
USER_HOME=$(eval echo "~$TARGET_USER")

INSTALL_TAILSCALE=false
for arg in "$@"; do
    if [ "$arg" = "--tailscale" ]; then
        INSTALL_TAILSCALE=true
    fi
done

echo "================================================================================"
echo "[+] Starting OpenSSH Server & Remote Access Configuration for '$TARGET_USER'"
echo "================================================================================"

# 2. Verify OpenSSH Installation
if ! command -v sshd &>/dev/null; then
    echo "[*] OpenSSH is not installed. Installing openssh via pacman..."
    pacman -S --needed --noconfirm openssh
else
    echo "[+] OpenSSH package is already installed."
fi

# 3. Generate Host Keys if Missing
echo "[*] Ensuring SSH host keys exist..."
ssh-keygen -A
echo "[+] SSH host keys verified in /etc/ssh/."

# 4. Configure Drop-in OpenSSH Daemon Settings
SSHD_CONFIG_DIR="/etc/ssh/sshd_config.d"
CONFIG_FILE="$SSHD_CONFIG_DIR/10-remote-access.conf"

mkdir -p "$SSHD_CONFIG_DIR"
cat << 'CONFIG_EOF' > "$CONFIG_FILE"
# ------------------------------------------------------------------------------
# OpenSSH Server Remote Access Configuration (Automated Setup)
# ------------------------------------------------------------------------------
Port 22
ListenAddress 0.0.0.0
ListenAddress ::

# Authentication
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication yes
KbdInteractiveAuthentication yes
UsePAM yes

# Session & Connection Health
X11Forwarding yes
TCPKeepAlive yes
ClientAliveInterval 60
ClientAliveCountMax 3
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/ssh/sftp-server
CONFIG_EOF

chmod 644 "$CONFIG_FILE"
echo "[+] Dropped configuration to $CONFIG_FILE."

# 5. Validate SSH Daemon Configuration Syntax
echo "[*] Testing sshd configuration syntax..."
sshd -t
echo "[+] Configuration syntax valid."

# 6. Enable and Start SSH Daemon
echo "[*] Enabling and starting sshd.service..."
systemctl daemon-reload
systemctl enable sshd.service
systemctl restart sshd.service
echo "[+] sshd.service is active and enabled."

# 7. Configure UFW Firewall (if present)
if command -v ufw &>/dev/null; then
    UFW_STATUS=$(ufw status | head -n 1)
    echo "[*] Detected UFW ($UFW_STATUS)."
    echo "[*] Adding firewall rule to allow SSH (port 22/tcp)..."
    ufw allow 22/tcp comment 'OpenSSH Server Remote Access'
    ufw reload || true
    echo "[+] Firewall rules updated."
fi

# 8. Ensure Avahi (mDNS) is active for hostname.local resolution
if command -v avahi-daemon &>/dev/null; then
    echo "[*] Ensuring avahi-daemon is running for mDNS (local hostname resolution)..."
    systemctl enable --now avahi-daemon.service || true
fi

# 9. Configure User SSH Authorized Keys for Localhost & Remote Access
USER_SSH_DIR="$USER_HOME/.ssh"
mkdir -p "$USER_SSH_DIR"
chmod 700 "$USER_SSH_DIR"
chown "$TARGET_USER:$TARGET_USER" "$USER_SSH_DIR"

if [ -f "$USER_SSH_DIR/id_ed25519.pub" ]; then
    PUB_KEY=$(cat "$USER_SSH_DIR/id_ed25519.pub")
    AUTH_KEYS="$USER_SSH_DIR/authorized_keys"
    touch "$AUTH_KEYS"
    if ! grep -qF "$PUB_KEY" "$AUTH_KEYS"; then
        echo "$PUB_KEY" >> "$AUTH_KEYS"
        echo "[+] Added user's local ed25519 key to authorized_keys."
    fi
    chmod 600 "$AUTH_KEYS"
    chown "$TARGET_USER:$TARGET_USER" "$AUTH_KEYS"
fi

# 10. Tailscale Integration (Optional / "From Anywhere Outside LAN")
if [ "$INSTALL_TAILSCALE" = true ]; then
    echo "--------------------------------------------------------------------------------"
    echo "[*] Setting up Tailscale for secure internet access from anywhere..."
    pacman -S --needed --noconfirm tailscale
    systemctl enable --now tailscaled.service
    echo "[+] Tailscaled service is active."
    echo "[!] To authenticate this machine to your Tailscale mesh, run:"
    echo "      sudo tailscale up --ssh"
    echo "--------------------------------------------------------------------------------"
fi

# 11. Print Connection Information
LOCAL_IP=$(ip -4 addr show wlan0 2>/dev/null | awk '/inet / {print $2}' | cut -d/ -f1 || hostname -I | awk '{print $1}')
HOSTNAME_STR=$(hostname)

echo "================================================================================"
echo "[+] SSH Remote Access is fully configured and READY!"
echo "================================================================================"
echo "Connection Details:"
echo "  - User:          $TARGET_USER"
echo "  - Machine Host:  $HOSTNAME_STR"
echo "  - Local IP:      ${LOCAL_IP:-'Unknown'}"
echo "  - mDNS Domain:   ${HOSTNAME_STR}.local"
echo "  - Port:          22"
echo ""
echo "How to connect:"
echo "  1. From this machine (terminal / test):"
echo "       ssh $TARGET_USER@localhost"
echo "       ssh localhost"
echo ""
echo "  2. From any device on the same local Wi-Fi / LAN:"
echo "       ssh $TARGET_USER@${HOSTNAME_STR}.local"
echo "       ssh $TARGET_USER@${LOCAL_IP:-'<MACHINE_IP>'}"
echo ""
echo "  3. From anywhere in the world (over the internet):"
echo "     Run 'sudo tailscale up --ssh' to join your private Tailscale network,"
echo "     then connect securely from any phone, laptop, or PC via:"
echo "       ssh $TARGET_USER@$HOSTNAME_STR"
echo "================================================================================"
