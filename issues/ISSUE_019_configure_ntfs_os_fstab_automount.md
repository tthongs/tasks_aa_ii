# [TASK] Configure /etc/fstab for OS-Labelled NTFS Partition Automount

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: `/etc/fstab`, `/mnt/OS`

## Description
The internal NVMe drive contains an NTFS partition labelled `OS` (`/dev/nvme0n1p3`, UUID `D494677F9467634A`). The user requested configuring `/etc/fstab` so this partition automatically mounts at system boot without manual intervention, while guaranteeing fail-safe protections against boot hangs or permission conflicts.

## Target Partition Details
- **Device Path**: `/dev/nvme0n1p3`
- **Filesystem**: `ntfs` (kernel `ntfs3`)
- **Partition Label**: `OS`
- **UUID**: `D494677F9467634A`
- **Mount Point**: `/mnt/OS`
- **Target User**: `tthhongs` (`uid=1000`, `gid=1000`)

## Proposed Solution / Action Items
- [x] **Identified Partition UUID & Properties**: Used `lsblk -f` to identify UUID `D494677F9467634A` and filesystem type `ntfs`.
- [x] **Created Mount Directory**: Prepared `/mnt/OS` with permissions for user `tthhongs` (`uid=1000`, `gid=1000`).
- [x] **Designed Robust /etc/fstab Configuration**:
  - `UUID=D494677F9467634A`: Disk-order independent persistent matching.
  - `ntfs3`: High-performance Linux in-tree NTFS kernel driver.
  - `defaults,uid=1000,gid=1000`: Grants full read/write permissions directly to the non-root user.
  - `dmask=022,fmask=133`: Sets standard directory permissions (`755`, `rwxr-xr-x`) and file permissions (`644`, `rw-r--r--`).
  - `iocharset=utf8`: Ensures full UTF-8 character encoding support.
  - `windows_names`: Enforces Windows-compatible naming constraints.
  - `nofail`: Crucial boot protection that prevents system boot stalls or drops into systemd emergency mode if the filesystem encounters a dirty bit or hibernation lock.
  - `x-systemd.device-timeout=10s`: Bounds the device wait timeout during boot to 10 seconds.
- [x] **Created Automated Setup Script**: Wrote `fix_os_ntfs_automount.sh` to safely backup `/etc/fstab`, write the entry, reload systemd, and mount the partition.
- [x] **Documented Commands**: Added Section 16 to `unix_issues_cmds.txt`.
- [x] **Updated GEMINI.md**: Reflected `ISSUE_019` in the master task log.

## Verification
- Validated partition UUID and driver compatibility using kernel `ntfs3`.
- Tested fstab entry structure against systemd fstab generator specifications.
