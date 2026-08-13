# [TASK] Update GRUB Bootloader Timeout to 50 Seconds

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: `/etc/default/grub`, `/boot/grub/grub.cfg`

## Description
Requested to increase the GRUB bootloader timeout to 50 seconds (from 5 seconds) to allow sufficient time for boot menu selection during system startup.

## Solution & Action Items
- [x] Inspected `/etc/default/grub` and confirmed initial setting `GRUB_TIMEOUT='5'`.
- [x] Updated `GRUB_TIMEOUT='50'` in `/etc/default/grub`.
- [x] Regenerated active GRUB config via `sudo grub-mkconfig -o /boot/grub/grub.cfg`.
- [x] Verified `set timeout=50` is active in `/boot/grub/grub.cfg`.
- [x] Committed and auto-pushed updated issue documentation to GitHub.

## Verification
- Executed `grep "GRUB_TIMEOUT=" /etc/default/grub` which confirmed `GRUB_TIMEOUT='50'`.
- Executed `sudo grep "set timeout=" /boot/grub/grub.cfg` which confirmed `set timeout=50`.
