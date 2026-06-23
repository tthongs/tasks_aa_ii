# ISSUE_007: [BUG] SSD Mount Issues and Intermittent Disconnections

**Status**: In Progress
**Priority**: High
**Affected Directory**: /etc, /home/tthongs/.bashrc

## Description
The external SSD (`IntelSSD`) regularly disconnects due to power management / 
link power management (LPM) transitions of the Realtek RTL9210 M.2 NVMe 
adapter. When it disconnects and reconnects:
1. The partition node shifts (e.g., from `/dev/sda1` to `/dev/sdb1`).
2. The mount `/mnt/IntelSSD` becomes stale and dangling, causing the kernel 
   to endlessly loop attempting to read the missing device node, spamming logs 
   with `ntfs3(sda1): failed to read volume at offset...` messages.
3. The hardcoded user aliases `ssd` (bound to `/dev/sda1`) and `ssd2` (bound to 
   `/dev/sdb1`) fail because the device node changes dynamically and the mount 
   point remains blocked by the stale mount.

## Steps to Reproduce
1. Connect the Realtek RTL9210 external SSD enclosure.
2. Mount the drive using the `ssd` alias (mounts `/dev/sda1` via `ntfs3`).
3. Allow the link to idle or drop due to LPM, which forces the device to 
   disconnect and reconnect as `/dev/sdb1`.
4. Observe the kernel log spam in `journalctl -b` and the failure of subsequent 
   mount commands.

## Proposed Solution / Action Items
- [x] Update the user's `ssd` and `ssd2` aliases in `~/.bashrc` to point to a 
      unified UUID-based mount point rather than hardcoding device nodes.
- [x] Create a udev rule to disable USB autosuspend for the RTL9210 adapter 
      (VID `0bda`, PID `9210`) to prevent idle disconnections.
- [x] Create udev rules to automatically perform a lazy unmount (`umount -l`) of 
      `/mnt/IntelSSD` when the device is disconnected, preventing log spam.
- [x] Add a robust entry for `IntelSSD` in `/etc/fstab` using its UUID 
      (`26DA54F26E91D133`) and systemd automount options.
- [ ] Run the automated setup script `fix_ssd_mount.sh` with root privileges.

## Notes
To fully resolve this issue, run the provided setup script:
```bash
sudo ./fix_ssd_mount.sh
```
This script will safely clean up the stale mount, configure `/etc/fstab`, 
install the udev rules, and apply all settings.
