# [TASK] Add Custom Power Off Menu Entry to GRUB Bootloader

**Status**: Resolved
**Priority**: Low
**Affected Directory**: `/etc/grub.d/99_poweroff`, `/boot/grub/grub.cfg`

## Description
Added a custom 'Power Off' menu entry to GRUB so that the machine can be shut down directly from the GRUB boot menu without booting into an OS.

## Solution & Action Items
- [x] Created executable script `/etc/grub.d/99_poweroff` containing GRUB `halt` command within menuentry `'Power Off'`.
- [x] Set permission mode `0755` (`chmod +x`) on `/etc/grub.d/99_poweroff`.
- [x] Regenerated GRUB configuration via `sudo grub-mkconfig -o /boot/grub/grub.cfg`.
- [x] Verified `menuentry 'Power Off'` is correctly appended as the final menu item in `/boot/grub/grub.cfg`.

## Verification
Executed `sudo grep -A 5 "menuentry 'Power Off'" /boot/grub/grub.cfg`:
```
menuentry 'Power Off' --class shutdown {
	halt
}
```
Confirmed entry is properly included at the bottom of GRUB menu choices.
