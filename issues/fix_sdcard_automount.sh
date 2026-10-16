#!/bin/bash
# fix_sdcard_automount.sh - Automate /etc/fstab and udev rules for SanDisk SD Card
# MUST BE RUN WITH SUDO/ROOT PRIVILEGES.
#
# Usage: sudo ./fix_sdcard_automount.sh

set -e

# 1. Root privilege verification
if [ "$EUID" -ne 0 ]; then
  echo "[-] Error: Please run this script with sudo or as root."
  echo "    Usage: sudo $0"
  exit 1
fi

UUID="9C33-6BBD"
LABEL="SanDiskSD"
MOUNT_POINT="/mnt/SanDiskSD"
FSTAB_FILE="/etc/fstab"
UID_VAL="1000"
GID_VAL="1000"
UDEV_RULE_FILE="/etc/udev/rules.d/99-sdcard.rules"

echo "[+] Starting SanDisk SD Card automount configuration..."

# 2. Verify target partition exists via UUID or label
if ! blkid | grep -q "$UUID"; then
  echo "[!] Notice: Partition with UUID $UUID was not detected by blkid at this moment."
  echo "    Configuring fstab and udev rules for persistent automounting on plug-in/boot..."
else
  DEV_NAME=$(blkid -U "$UUID" 2>/dev/null || true)
  echo "[+] Detected target partition ${DEV_NAME:-device} with UUID $UUID and label $LABEL."
fi

# 3. Create persistent mount directory
if [ ! -d "$MOUNT_POINT" ]; then
  echo "[+] Creating mount directory $MOUNT_POINT..."
  mkdir -p "$MOUNT_POINT"
  chown "${UID_VAL}:${GID_VAL}" "$MOUNT_POINT"
  chmod 755 "$MOUNT_POINT"
  echo "[+] Mount point $MOUNT_POINT created successfully."
else
  echo "[*] Mount point $MOUNT_POINT already exists. Ensuring correct permissions..."
  chown "${UID_VAL}:${GID_VAL}" "$MOUNT_POINT"
  chmod 755 "$MOUNT_POINT"
fi

# 4. Backup fstab
BACKUP_FILE="${FSTAB_FILE}.bak.$(date +%Y%m%d%H%M%S)"
echo "[+] Creating timestamped backup: $BACKUP_FILE..."
cp "$FSTAB_FILE" "$BACKUP_FILE"

# 5. Clean up any existing duplicate entries or broken multiline lines in /etc/fstab
echo "[+] Sanitizing and updating $FSTAB_FILE..."
# Remove any prior entries for this UUID or mount point
sed -i "\#$UUID#d" "$FSTAB_FILE"
sed -i "\#$MOUNT_POINT#d" "$FSTAB_FILE"

# Clean up any fragmented lines (e.g., from old multiline formatting)
sed -i '/^[[:space:]]*device-timeout=/d' "$FSTAB_FILE"
sed -i 's/x-systemd\.$/x-systemd.device-timeout=10s  0  0/' "$FSTAB_FILE"

# 6. Append new fstab entry
# Configuration Breakdown:
# - UUID=9C33-6BBD: Persistent across device node shifts (/dev/sdb1, /dev/sdc1, etc.)
# - /mnt/SanDiskSD: Fixed system mount location
# - exfat: In-tree native Linux exFAT kernel module
# - defaults: Standard read/write, suid, dev, exec, auto, async flags
# - uid=1000,gid=1000: User tthhongs direct read/write ownership
# - dmask=022,fmask=133: Standard directory (755) and file (644) permissions
# - iocharset=utf8: Full international UTF-8 file and folder name encoding
# - nofail: Prevents boot stalls/emergency drops if SD card is unplugged at boot
# - x-systemd.automount: Establishes kernel autofs on-demand mount unit at boot with 0ms boot delay
# - x-systemd.device-timeout=5s: Restricts block device detection wait timeout to 5 seconds
FSTAB_ENTRY="UUID=$UUID  $MOUNT_POINT  exfat  defaults,uid=${UID_VAL},gid=${GID_VAL},dmask=022,fmask=133,iocharset=utf8,nofail,x-systemd.automount,x-systemd.device-timeout=5s  0  0"

echo "[+] Appending new entry to $FSTAB_FILE..."
echo -e "\n# SanDisk SD Card Automount\n$FSTAB_ENTRY" >> "$FSTAB_FILE"

# 7. Configure udev rules for hotplug add and safe removal
echo "[+] Writing udev rules to $UDEV_RULE_FILE..."
cat << 'EOF' > "$UDEV_RULE_FILE"
# 99-sdcard.rules - Automount and clean disconnect for SanDisk SD card
ACTION=="add", SUBSYSTEM=="block", ENV{ID_FS_UUID}=="9C33-6BBD", TAG+="systemd", ENV{SYSTEMD_WANTS}+="mnt-SanDiskSD.mount"
ACTION=="remove", SUBSYSTEM=="block", ENV{ID_FS_UUID}=="9C33-6BBD", RUN+="/usr/bin/umount -l /mnt/SanDiskSD"
ACTION=="remove", SUBSYSTEM=="block", ENV{ID_FS_LABEL}=="SanDiskSD", RUN+="/usr/bin/umount -l /mnt/SanDiskSD"
EOF

# 8. Reload udev rules
echo "[+] Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger --subsystem-match=block || true

# 9. Reload systemd daemon to generate mount & automount units
echo "[+] Reloading systemd daemon..."
systemctl daemon-reload

# 10. Start and enable automount unit
echo "[+] Starting mnt-SanDiskSD.automount unit..."
systemctl restart mnt-SanDiskSD.automount

# 11. Handle current desktop/udisks2 session mount if active
DEV_NODE=$(blkid -U "$UUID" 2>/dev/null || true)
if [ -n "$DEV_NODE" ]; then
  CURRENT_MOUNT=$(findmnt -n -o TARGET "$DEV_NODE" | head -n 1 || true)
  if [ -n "$CURRENT_MOUNT" ] && [ "$CURRENT_MOUNT" != "$MOUNT_POINT" ]; then
    echo "[*] Notice: Partition $DEV_NODE is currently mounted at $CURRENT_MOUNT."
    # Check if active files are open
    if command -v fuser >/dev/null 2>&1 && fuser -m "$CURRENT_MOUNT" >/dev/null 2>&1; then
      echo "[*] Files are currently in use on $CURRENT_MOUNT (e.g. media player)."
      echo "[*] Leaving active mount unharmed. The partition will cleanly automount to $MOUNT_POINT"
      echo "    upon reboot or whenever the current mount is unmounted."
    else
      echo "[+] Unmounting previous temporary mount $CURRENT_MOUNT..."
      umount "$CURRENT_MOUNT" || true
      echo "[+] Triggering access to $MOUNT_POINT..."
      ls "$MOUNT_POINT" >/dev/null 2>&1 || true
    fi
  fi
fi

# 12. Final verification
echo "=================================================="
echo "Verification Summary:"
echo "--------------------------------------------------"
echo "[*] Systemd automount unit status:"
systemctl status mnt-SanDiskSD.automount --no-pager || true
echo "--------------------------------------------------"
echo "[*] Active mount points for UUID $UUID:"
findmnt -S "UUID=$UUID" || echo "Mount point will activate on next directory access or system boot."
echo "=================================================="
echo "[✓] SanDisk SD Card automount configuration completed successfully!"
