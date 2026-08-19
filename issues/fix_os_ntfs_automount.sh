#!/bin/bash
# fix_os_ntfs_automount.sh - Script to configure /etc/fstab for OS-labelled NTFS partition
# MUST BE RUN WITH SUDO/ROOT PRIVILEGES.

set -e

# 1. Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "[-] Error: Please run this script with sudo or as root."
  echo "    Usage: sudo ./fix_os_ntfs_automount.sh"
  exit 1
fi

UUID="D494677F9467634A"
MOUNT_POINT="/mnt/OS"
FSTAB_FILE="/etc/fstab"
UID_VAL="1000"
GID_VAL="1000"

echo "[+] Starting OS NTFS partition automount configuration..."

# 2. Verify target partition exists
if ! blkid | grep -q "$UUID"; then
  echo "[!] Warning: Partition with UUID $UUID was not detected by blkid."
  echo "    Proceeding with fstab configuration anyway..."
else
  DEV_NAME=$(blkid -U "$UUID")
  echo "[+] Found target partition $DEV_NAME with UUID $UUID."
fi

# 3. Create mount point directory
if [ ! -d "$MOUNT_POINT" ]; then
  echo "[+] Creating mount directory $MOUNT_POINT..."
  mkdir -p "$MOUNT_POINT"
  chown "${UID_VAL}:${GID_VAL}" "$MOUNT_POINT"
  chmod 755 "$MOUNT_POINT"
  echo "[+] Directory $MOUNT_POINT created."
else
  echo "[*] Mount directory $MOUNT_POINT already exists."
fi

# 4. Backup fstab
BACKUP_FILE="${FSTAB_FILE}.bak.$(date +%Y%m%d%H%M%S)"
echo "[+] Backing up $FSTAB_FILE to $BACKUP_FILE..."
cp "$FSTAB_FILE" "$BACKUP_FILE"

# 5. Clean existing entries for this UUID or mount point if present
if grep -q "$UUID" "$FSTAB_FILE" || grep -q "$MOUNT_POINT" "$FSTAB_FILE"; then
  echo "[*] Existing entry found for $UUID or $MOUNT_POINT. Removing old entry..."
  sed -i.tmp "\#$UUID#d" "$FSTAB_FILE"
  sed -i.tmp "\#$MOUNT_POINT#d" "$FSTAB_FILE"
  rm -f "${FSTAB_FILE}.tmp"
fi

# 6. Append new fstab entry
# Options breakdown:
# - ntfs3: in-tree high-performance kernel driver
# - defaults: rw, suid, dev, exec, auto, nouser, async
# - uid=1000,gid=1000: gives user tthhongs read/write ownership
# - dmask=022,fmask=133: safe directory (755) and file (644) permissions
# - iocharset=utf8: ensures UTF-8 character encoding support
# - windows_names: enforces Windows-compatible filenames
# - nofail: prevents boot hangs or emergency mode drops if disk isn't ready
# - x-systemd.device-timeout=10s: bounds device wait timeout during boot
FSTAB_ENTRY="UUID=$UUID  $MOUNT_POINT  ntfs3  defaults,uid=${UID_VAL},gid=${GID_VAL},dmask=022,fmask=133,iocharset=utf8,windows_names,nofail,x-systemd.device-timeout=10s  0  0"

echo "[+] Appending new entry to $FSTAB_FILE..."
echo -e "\n# OS NTFS Partition Automount\n$FSTAB_ENTRY" >> "$FSTAB_FILE"

# 7. Reload systemd daemon
echo "[+] Reloading systemd daemon to process fstab changes..."
systemctl daemon-reload

# 8. Mount partition
echo "[+] Mounting $MOUNT_POINT..."
if mountpoint -q "$MOUNT_POINT"; then
  echo "[*] $MOUNT_POINT is already mounted. Remounting..."
  mount -o remount "$MOUNT_POINT" || true
else
  mount "$MOUNT_POINT" || true
fi

# 9. Verify mount status
if mountpoint -q "$MOUNT_POINT" || grep -q "$MOUNT_POINT" /proc/mounts; then
  echo "[+] SUCCESS: $MOUNT_POINT is actively mounted!"
  findmnt "$MOUNT_POINT"
else
  echo "[!] Warning: Mount attempt did not register. If partition was dirty or Windows was hibernated, check 'dmesg | grep ntfs3'."
fi

echo "[+] NTFS OS Drive automount configuration complete."
