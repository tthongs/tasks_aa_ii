# [BUG] NVIDIA Open Kernel Module Deadlock, Early Boot Freeze & SDDM Display Failure

**Status**: Resolved
**Priority**: High
**Affected Directory**: `/etc/mkinitcpio.conf.d/10-chwd.conf`, `/usr/lib/modules/`, `/etc/modprobe.d/`

## Description
During system startup on kernels `7.1.8-1-cachyos` and `6.18.42-1-cachyos-lts`, an early boot hang (90s-122s) occurred during `systemd-modules-load.service` (`Load Kernel Modules`). The boot process dropped to a black screen with an unresponsive, non-blinking cursor (`_`), followed by SDDM and Plasma Wayland greeter crashes and a shutdown transaction loop.

## Root Cause Analysis
Kernel journal diagnostics (`journalctl -b -3 -p 3`) revealed a kernel deadlock in the out-of-tree precompiled NVIDIA open kernel module (`linux-cachyos-nvidia-open` 610.57.04):
- `kworker/2:1:129` executing ACPI NVPCF notification (`rm_acpi_nvpcf_notify -> rmapiLockAcquire -> os_acquire_rwlock_write`) blocked on an `rw-semaphore`.
- The semaphore was held by `(udev-worker):186` / `kworker/2:2:159` executing device initialization (`nv_drm_register_drm_device -> nv_drm_dev_load -> RmInitAdapter -> kgspInitRm_IMPL`).
- Because `udev-worker` was blocked in uninterruptible sleep state (`D`), `systemd-udevd` timed out after 120s and terminated worker 472 with `SIGKILL`.
- The DRM device node failed to initialize in time, causing SDDM/KWin Wayland to crash due to a missing/unresponsive display platform backend.
- During system shutdown/poweroff, `nvidia-powerd` hung waiting on the deadlocked driver module until forced kill timeouts elapsed.

## Steps to Reproduce
1. Boot with pre-packaged binary NVIDIA open modules (`linux-cachyos-nvidia-open`) on Linux kernel 7.1.8 / 6.18.42.
2. Observe systemd module loading hang for 90-120 seconds (`A start job is running for Load Kernel Modules`).
3. System drops to black screen with frozen cursor; SDDM greeter crashes.
4. Short press of power button triggers systemd shutdown loop with `nvidia-powerd` timeout (`A stop job is running for User Manager for UID 956`).

## Solution & Action Items
- [x] Analyzed boot journals and call traces across historical boots (`journalctl -b -3`, `-b -2`, `-b -1`, `-b 0`).
- [x] Removed precompiled binary kernel module packages (`linux-cachyos-nvidia-open` and `linux-cachyos-lts-nvidia-open`).
- [x] Installed dynamic kernel module support (`dkms`), kernel development headers (`linux-cachyos-headers`, `linux-cachyos-lts-headers`), and `nvidia-open-dkms`.
- [x] Recompiled NVIDIA open kernel modules cleanly against both host kernels (`7.1.8-1-cachyos` and `6.18.42-1-cachyos-lts`).
- [x] Rebuilt early initramfs images with `mkinitcpio` containing `nvidia`, `nvidia_modeset`, `nvidia_uvm`, and `nvidia_drm` early loading hooks.
- [x] Verified clean module load, DRM KMS initialization (`nvidia-drm` on minor 1, `i915` on minor 2), and active Wayland compositor (`kwin_wayland`) running without deadlocks.
- [x] Evaluated potential secondary risks (Dynamic Boost SBIOS notifications, power management, Wayland compositor hooks) to confirm no recurring failure paths remain.

## Verification
- Running `uname -r` confirmed active kernel `7.1.8-1-cachyos`.
- Running `nvidia-smi` verified functional driver communication with RTX 4050 Laptop GPU (Driver: `610.57.04`, CUDA: `13.3`, KMD: `610.57.04`).
- Running `dkms status` confirmed clean installation for both `7.1.8-1-cachyos` and `6.18.42-1-cachyos-lts`.
- Running `journalctl -b 0 -p 3` confirmed zero driver deadlocks or udev worker timeouts on current boot.
