# [TASK] Rename GRUB Boot Entry from Windows Boot Manager to Windows 11

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: `/etc/grub.d/30_os-prober`, `/usr/lib/os-probes/mounted/efi/20microsoft`, `/boot/grub/grub.cfg`

## Description
When dual-booting Linux and Windows on UEFI systems, `os-prober` detects the Microsoft EFI bootloader executable (`\EFI\Microsoft\Boot\bootmgfw.efi`) and labels it as `Windows Boot Manager`. Consequently, the generated GRUB boot menu lists the boot entry as `Windows Boot Manager (on /dev/nvme0n1p1)` instead of the explicit operating system name `Windows 11`.

The objective of this task is to configure the GRUB os-prober generator and EFI probe scripts so that GRUB displays `Windows 11` in the startup boot menu.

## Technical Details & Root Cause
1. **UEFI os-prober Behavior**: In `/usr/lib/os-probes/mounted/efi/20microsoft`, the EFI probe script hardcodes `long="Windows Boot Manager"` upon detecting `bootmgfw.efi` and `BCD`. Unlike legacy BIOS probing (which parses BCD strings to detect specific Windows versions), the EFI probe defaults to generic manager naming.
2. **GRUB os-prober Menu Generator**: `/etc/grub.d/30_os-prober` consumes the output string from `os-prober` and formats the menuentry title as `'$(echo "${LONGNAME} $onstr" | grub_quote)'`. Because `LONGNAME` contains `Windows Boot Manager`, the resulting GRUB entry is named `Windows Boot Manager`.
3. **Resolution**:
   - Patch `/etc/grub.d/30_os-prober` to remap `LONGNAME="Windows Boot Manager"` to `LONGNAME="Windows 11"`. Placing this in `/etc/grub.d/` ensures persistent behavior across os-prober package upgrades.
   - Update default EFI probing in `/usr/lib/os-probes/mounted/efi/20microsoft` to report `long="Windows 11"`.
   - Regenerate the active GRUB menu via `grub-mkconfig -o /boot/grub/grub.cfg`.

## Proposed Solution / Action Items
- [x] **Analyzed GRUB Generation Pipeline**: Inspected `/etc/grub.d/30_os-prober` and `/usr/lib/os-probes/mounted/efi/20microsoft`.
- [x] **Created Automated Fix Script**: Built [`fix_grub_windows_entry.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/fix_grub_windows_entry.sh) with backup safeguards, in-place python/sed patches, and automatic verification.
- [x] **Configured Transformation Logic**:
  - `/etc/grub.d/30_os-prober`: Intercepted `LONGNAME` assignment and converted `"Windows Boot Manager"` to `"Windows 11"`.
  - `/usr/lib/os-probes/mounted/efi/20microsoft`: Replaced default `long="Windows Boot Manager"` with `long="Windows 11"`.
- [x] **Documented Commands**: Added Section 18 to [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt).
- [x] **Updated GEMINI.md**: Added `ISSUE_021` to the issue tracking index.

## Verification
- Validated shell syntax for [`fix_grub_windows_entry.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/fix_grub_windows_entry.sh) via `bash -n`.
- Verified string transformation logic on `/etc/grub.d/30_os-prober` and `/usr/lib/os-probes/mounted/efi/20microsoft`.
- Output menu entry in `/boot/grub/grub.cfg` generates as `Windows 11 (on /dev/nvme0n1p1)` with class `windows`.
