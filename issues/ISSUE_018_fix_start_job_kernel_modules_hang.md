# [BUG] Systemd Modules Load Stall & Early Boot Start Job Hang

**Status**: Resolved
**Priority**: High
**Affected Directory**: `/etc/modules-load.d/`, `/etc/systemd/system/systemd-modules-load.service.d/`, `/etc/mkinitcpio.conf.d/`, `/etc/modprobe.d/`

## Description
During system startup, the boot sequence frequently stalled or hung on the message:
```text
A start job is running for Load Kernel Modules (Xs / 1min 30s)
```
In severe instances, `systemd-modules-load.service` hit the 90-second timeout and failed with `status=15/TERM`, delaying system startup and causing downstream graphical initialization stalls.

## Root Cause
1. **Unnecessary Early Module Probe**: Package `nvidia-utils` automatically placed `nvidia-uvm` into `/usr/lib/modules-load.d/nvidia-utils.conf`. During early boot, `systemd-modules-load.service` spawned 4 parallel probe threads to load `nvidia-uvm` (and its dependencies `nvidia`, `nvidia_modeset`, `nvidia_drm`).
2. **Race Condition & Lock Contention**: While `systemd-modules-load` was attempting parallel module insertion, `systemd-udevd` was concurrently probing PCI device `0000:01:00.0` (RTX 4050) and the ACPI NVPCF notification handler (`rm_acpi_nvpcf_notify`) was receiving SBIOS events. Both threads contested the internal Resource Manager rw-semaphore (`os_acquire_rwlock_write` in `rmapiLockAcquire`), leading to uninterruptible sleep (D-state) hangs.
3. **No Service Timeout Clamp**: `systemd-modules-load.service` defaulted to systemd's global 90-second timeout (`DefaultTimeoutStartSec=90s`), forcing the system to freeze for 1.5 minutes before recovering.

## Proposed Solution / Action Items
- [x] **Masked `nvidia-utils.conf`**: Created mask symlink `/etc/modules-load.d/nvidia-utils.conf -> /dev/null` so `systemd-modules-load` no longer loads CUDA UVM at early boot. (UVM is dynamically loaded on-demand by CUDA runtimes when required).
- [x] **Configured Deterministic Early KMS**: Added `/etc/mkinitcpio.conf.d/10-nvidia.conf` with `MODULES+=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)` to ensure early, sequential driver loading inside initramfs before userspace services start.
- [x] **Configured Modprobe Options**: Updated `/etc/modprobe.d/nvidia.conf` with `options nvidia-drm modeset=1 fbdev=1` and `NVreg_DynamicPowerManagement=0x02`.
- [x] **Service Timeout Drop-In**: Created `/etc/systemd/system/systemd-modules-load.service.d/10-timeout.conf` setting `TimeoutStartSec=10s` to prevent any future 90-second stalls.
- [x] **Fixed Plasma Localerc**: Updated `~/.config/plasma-localerc` to `LANG=en_IN.UTF-8` to eliminate lingering KWin Wayland compose table warnings.
- [x] **Rebuilt Initramfs**: Regenerated initramfs images across both active (`7.1.8-1-cachyos`) and LTS (`6.18.42-1-cachyos-lts`) kernels via `sudo mkinitcpio -P`.
- [x] **Automated Fix Script**: Created `fix_kernel_modules_boot.sh` for one-command reapplication.

## Verification
- Verified `mkinitcpio -P` built cleanly with `0 errors` across all installed kernels.
- Verified `systemctl is-active systemd-modules-load.service` reports `active`.
- Verified `nvidia-smi` communicates with RTX 4050 GPU and KWin Wayland is rendering smoothly.
