# [TASK] Configure /etc/fstab and Udev for SanDisk SD Card Automount

**Status**: Resolved  
**Priority**: Medium  
**Affected Directory**: `/etc/fstab`, `/etc/udev/rules.d/99-sdcard.rules`, `/mnt/SanDiskSD`

## Description
The user attached an SD card labelled `SanDiskSD` (`UUID=9C33-6BBD`, exFAT filesystem) and requested that it automatically mount on or after system boot without requiring manual intervention. A critical constraint is that if the SD card is detached, missing, or fails to mount, the system boot process must not be delayed, blocked, or dropped into emergency recovery mode.

## Target Partition Details
- **Device Node**: `/dev/sdb1` (dynamic; tracked via UUID)
- **Filesystem**: `exfat` (in-tree Linux kernel driver)
- **Partition Label**: `SanDiskSD`
- **Filesystem UUID**: `9C33-6BBD`
- **Mount Point**: `/mnt/SanDiskSD`
- **Target User / Group**: `tthhongs` (`uid=1000`, `gid=1000`)

## Technical Architecture & Design Decisions
1. **Persistent Device Identification**:
   - Uses `UUID=9C33-6BBD` instead of raw `/dev/sdb1` to remain resilient against kernel device enumeration changes (e.g., when plugging in external SSDs or USB flash drives).
2. **Boot Hang & Emergency Mode Prevention (`nofail`)**:
   - Standard `/etc/fstab` entries without `nofail` become hard dependencies (`Requires=`) of `local-fs.target`. If a removable card is absent, systemd stalls for 90 seconds and drops the entire system into an emergency maintenance shell.
   - Adding `nofail` demotes the dependency to a soft requirement (`Wants=`) and unbinds ordering from `local-fs.target`, guaranteeing that system boot finishes cleanly and quickly even without the SD card.
3. **Zero Boot Delay via Autofs (`x-systemd.automount`)**:
   - `x-systemd.automount` instructs `systemd-fstab-generator` to create a virtual `autofs` mount unit at `/mnt/SanDiskSD` at early boot with zero blocking delay (0ms).
   - As soon as the user, desktop environment (KDE Plasma), file manager, or application accesses `/mnt/SanDiskSD`, systemd mounts the underlying partition transparently in milliseconds.
4. **Device Timeout Guard (`x-systemd.device-timeout=5s`)**:
   - Bounds any device detection or access wait timeout to 5 seconds (instead of systemd's default 90 seconds) if an application queries the mount path while the card is missing.
5. **Ownership and Permissions (`uid=1000,gid=1000,dmask=022,fmask=133`)**:
   - Because exFAT lacks native POSIX filesystem permissions, mount flags assign read/write ownership to `tthhongs` (`uid=1000`, `gid=1000`) with standard directory permissions (`755`, `rwxr-xr-x`) and file permissions (`644`, `rw-r--r--`).
6. **UTF-8 Character Support (`iocharset=utf8`)**:
   - Ensures correct encoding for multilingual filenames and media tags.
7. **Dynamic Hotplug & Clean Ejection (`99-sdcard.rules`)**:
   - A dedicated udev rule triggers `mnt-SanDiskSD.mount` via `ENV{SYSTEMD_WANTS}` as soon as the card is physically inserted after boot.
   - On removal, udev runs a lazy unmount (`umount -l /mnt/SanDiskSD`) to instantly release the mount point and prevent kernel read error loops.

## Proposed Solution / Action Items
- [x] **Probed Block Devices**: Identified `sdb1` as `exfat`, `SanDiskSD`, `UUID=9C33-6BBD` via `lsblk -f` and `udisksctl info`.
- [x] **Verified Systemd Unit Generation**: Tested `systemd-fstab-generator` in dry-run with test fstab to verify that `local-fs.target.wants` correctly generates `mnt-SanDiskSD.automount` and `JobRunningTimeoutSec=5s`.
- [x] **Created Automated Setup Script**: Authored [`fix_sdcard_automount.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/fix_sdcard_automount.sh) with timestamped backup, `/etc/fstab` sanitization, udev rules creation, and systemd reloading.
- [x] **Authored Hotplug Rules**: Implemented `/etc/udev/rules.d/99-sdcard.rules` for automated hotplug mounting and lazy disconnection cleanup.
- [x] **Documented Unix Commands**: Appended Section 22 to [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt).
- [x] **Updated GEMINI.md**: Added `ISSUE_025` to the master issue index.

## Verification
- Validated script syntax with `bash -n issues/fix_sdcard_automount.sh`.
- Executed `systemd-fstab-generator` against simulated configuration to verify correct unit generation without syntax warnings or errors.
- Verified active open file handles using `lsof` to ensure safety of running media applications prior to partition reconfiguration.
