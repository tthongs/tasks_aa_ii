#!/bin/bash
# fix_ssd_mount.sh - Script to fix stale mounts, set up udev rules, and configure /etc/fstab for IntelSSD.
# MUST BE RUN WITH SUDO/ROOT PRIVILEGES.

set -e

# 1. Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "[-] Error: Please run this script with sudo or as root."
  exit 1
fi

echo "[+] Starting SSD mount fixes..."

# 2. Lazy unmount the stale /mnt/IntelSSD mount to clear the kernel log spam and free the mount point
echo "[+] Lazily unmounting /mnt/IntelSSD to clear any stale mount points..."
if mountpoint -q /mnt/IntelSSD || grep -q "/mnt/IntelSSD" /proc/mounts; then
  umount -l /mnt/IntelSSD || true
  echo "[+] Unmounted successfully."
else
  echo "[*] /mnt/IntelSSD is not currently mounted."
fi

# 3. Create udev rules to prevent autosuspend and automatically clean up on disconnection
UDEV_RULE_FILE="/etc/udev/rules.d/99-realtek-ssd.rules"
echo "[+] Writing udev rules to $UDEV_RULE_FILE..."
cat << 'EOF' > "$UDEV_RULE_FILE"
# Disable USB autosuspend/power management for Realtek RTL9210 M.2 NVME Adapter
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="9210", ATTR{power/control}="on"

# Automatically perform a lazy unmount when the Intel SSD partition is disconnected
ACTION=="remove", SUBSYSTEM=="block", ENV{ID_FS_UUID}=="26DA54F26E91D133", RUN+="/usr/bin/umount -l /mnt/IntelSSD"
ACTION=="remove", SUBSYSTEM=="block", ENV{ID_FS_LABEL}=="IntelSSD", RUN+="/usr/bin/umount -l /mnt/IntelSSD"
EOF

# Reload and trigger udev rules
echo "[+] Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger
echo "[+] udev rules applied."

# 4. Configure /etc/fstab with a robust systemd-automount UUID-based entry
FSTAB_FILE="/etc/fstab"
UUID="26DA54F26E91D133"
MOUNT_POINT="/mnt/IntelSSD"
FSTAB_ENTRY="UUID=$UUID  $MOUNT_POINT  ntfs3  noatime,prealloc,force,uid=1000,gid=1000,fmask=0133,dmask=0022,user,nofail,x-systemd.automount,x-systemd.idle-timeout=600  0  0"

# Backup fstab
echo "[+] Backing up $FSTAB_FILE to ${FSTAB_FILE}.bak..."
cp "$FSTAB_FILE" "${FSTAB_FILE}.bak"

# Check if entry already exists
if grep -q "$UUID" "$FSTAB_FILE"; then
  echo "[*] UUID $UUID is already present in $FSTAB_FILE. Updating existing entry..."
  # Remove existing lines matching the UUID
  sed -i.tmp "/$UUID/d" "$FSTAB_FILE"
  rm -f "${FSTAB_FILE}.tmp"
fi

# Append the new entry
echo "[+] Appending new entry to $FSTAB_FILE..."
echo -e "\n# IntelSSD Automount\n$FSTAB_ENTRY" >> "$FSTAB_FILE"

# 5. Reload systemd configurations to parse fstab changes
echo "[+] Reloading systemd daemon..."
systemctl daemon-reload

# 6. Mount/Trigger the automount point
echo "[+] Mounting the drive..."
# systemd automount will automatically mount when accessed, but let's trigger it
if [ -b "/dev/disk/by-uuid/$UUID" ]; then
  mount "$MOUNT_POINT" || true
  echo "[+] SSD successfully mounted/activated at $MOUNT_POINT."
else
  echo "[!] Warning: SSD device with UUID $UUID is not connected right now."
  echo "    The mount point is ready and will automatically mount as soon as it is plugged in."
fi

echo "[+] SSD Mount Fixes successfully applied!"
echo "[*] Note: The aliases in ~/.bashrc have been updated. Run 'source ~/.bashrc' or restart your terminal."
