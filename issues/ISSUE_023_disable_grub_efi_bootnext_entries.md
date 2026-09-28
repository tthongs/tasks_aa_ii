# [TASK] Disable Automatic EFI BootNext Entries in GRUB Menu

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: `/etc/default/grub`, `/etc/grub.d/31_efi_bootnext`, `/boot/grub/grub.cfg`

## Description
Following a CachyOS / Arch Linux system upgrade (`pacman -Syu`), GRUB was updated to version `2:2.16-1.1`. After this update, several unwanted boot entries appeared directly beneath the `UEFI Firmware Settings` menu entry on the GRUB boot screen:
- `Windows Boot Manager (EFI BootNext)`
- `cachyos (EFI BootNext)`
- `EFI Hard Drive (BTKA21620RHU512A-INTEL SSDPEKNU512GZ) (EFI BootNext)`
- `EFI USB Device (EFI BootNext)`
- `EFI DVD/CDROM (EFI BootNext)`
- `EFI Network (EFI BootNext)`

The objective of this task is to remove these redundant NVRAM BootNext entries and restore a clean GRUB bootloader menu.

## Technical Details & Root Cause
1. **New Menu Generator Script (`31_efi_bootnext`)**: Upstream GRUB 2.16 introduced a new helper script at `/etc/grub.d/31_efi_bootnext`.
2. **NVRAM Enumeration**: This script runs `efibootmgr -v` to probe all motherboard UEFI NVRAM boot targets and generates a `menuentry '<label> (EFI BootNext)'` stanza for every discovered device and boot manager.
3. **Execution Ordering**: Because it is numbered `31_efi_bootnext`, it executes immediately after `30_uefi-firmware` (`UEFI Firmware Settings`) and before `40_custom` / `99_poweroff` (`Power Off`). Hence, all these entries appear between `UEFI Firmware Settings` and `Power Off`.
4. **Configuration Override**:
   - Lines 33–35 of `/etc/grub.d/31_efi_bootnext` explicitly support an opt-out configuration flag:
     ```sh
     if [ "${GRUB_DISABLE_BOOTNEXT}" = "true" ]; then
         exit 0
     fi
     ```
   - `/usr/bin/grub-mkconfig` (line 280) exports `GRUB_DISABLE_BOOTNEXT` from `/etc/default/grub`.
   - Setting `GRUB_DISABLE_BOOTNEXT=true` in `/etc/default/grub` cleanly suppresses the generation of all `(EFI BootNext)` entries.
   - De-executing `/etc/grub.d/31_efi_bootnext` (`chmod -x`) provides an additional defense against execution.

## Proposed Solution / Action Items
- [x] **Root Cause Investigation**: Identified new `/etc/grub.d/31_efi_bootnext` script introduced in GRUB `2:2.16-1.1`.
- [x] **Created Automated Fix Script**: Built [`fix_grub_efi_bootnext.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/fix_grub_efi_bootnext.sh) to automate `/etc/default/grub` updating, permission tightening, Windows 11 re-patching, and GRUB regeneration.
- [x] **Configured GRUB Parameter**: Added `GRUB_DISABLE_BOOTNEXT=true` to `/etc/default/grub`.
- [x] **Toggled Permissions**: Removed executable permissions (`chmod -x`) on `/etc/grub.d/31_efi_bootnext`.
- [x] **Documented Commands**: Added Section 20 to [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt).
- [x] **Updated GEMINI.md**: Added `ISSUE_023` to the issue tracking index.

## Verification
- Validated shell syntax for [`fix_grub_efi_bootnext.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/fix_grub_efi_bootnext.sh) via `bash -n`.
- Confirmed `GRUB_DISABLE_BOOTNEXT` logic inside `/usr/bin/grub-mkconfig` and `/etc/grub.d/31_efi_bootnext`.
- Tested script execution logic to ensure complete suppression of `(EFI BootNext)` entries in `/boot/grub/grub.cfg`.
