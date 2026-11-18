# [TASK] Verify and Fix OS Drive Read/Write Permissions

**Status**: Resolved  
**Priority**: Medium  
**Affected Directory**: `/mnt/OS`, `/mnt/OS/Games`, `/mnt/OS/Users`

## Description
The user requested to ensure that the Windows `OS` drive (`/dev/nvme1n1p3`, mounted at `/mnt/OS`) is fully writable.

## Investigation & Root Cause
1. **Drive Mount State**:
   - The partition `UUID=D494677F9467634A` was mounted as `ntfs3` with options `rw,relatime,uid=1000,gid=1000,dmask=0022,fmask=0133,windows_names,acl`.
   - File creation and modification directly under `/mnt/OS` succeeded as expected.
2. **Permission Bottlenecks Identified**:
   - Several directories (such as `/mnt/OS/Games`, `/mnt/OS/Users`, `/mnt/OS/Program Files`, and `/mnt/OS/Program Files (x86)`) had directory permissions set to `dr-xr-xr-x` (`555` read-only) due to Windows ACL / attribute inheritance when synced or mounted under `ntfs3` with ACL support enabled.
   - Specifically inside `/mnt/OS/Games`, attempts to write or create files were blocked with `Permission denied`.
3. **Resolution**:
   - Updated directory mode permissions (`chmod 755 /mnt/OS/Games`, `chmod 755 /mnt/OS/Users`, etc.) directly on the mount point.
   - Verified that directory creation, file creation, modification, and deletion work cleanly for user `tthhongs` (`uid=1000`).

## Proposed Solution / Action Items
- [x] Inspect current mount status, options, and filesystem driver for `/mnt/OS`.
- [x] Test write permissions at root level of `/mnt/OS`.
- [x] Identify directories blocked by read-only mode bits (`555` / `dr-xr-xr-x`).
- [x] Grant read/write/execute permissions (`755` / `777`) on user directories including `/mnt/OS/Games`.
- [x] Validate file creation and removal without permission errors.
- [x] Document Unix commands and update task tracking (`GEMINI.md`).

## Verification
- Created and removed test file `/mnt/OS/test_write.tmp` at root level.
- Created and removed test file `/mnt/OS/Games/test.txt` inside `/mnt/OS/Games`.
- Verified user directory write access under `/mnt/OS/Users/tthhongs`.
