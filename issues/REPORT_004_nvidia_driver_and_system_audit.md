# REPORT 004: NVIDIA Driver Recovery, DKMS Migration, Locale UTF-8 Calibration & Power Management Audit

**Date**: 2026-08-18  
**Author**: Antigravity AI  
**Target System**: Acer Aspire A715-79G (CachyOS Linux / Arch Linux)  
**Kernels**: `7.1.8-1-cachyos` (Active) | `6.18.42-1-cachyos-lts`  
**GPUs**: NVIDIA GeForce RTX 4050 Laptop GPU (`10de:28a0`) + Intel Raptor Lake-P UHD Graphics (`8086:a7ab`)  
**Location**: `/home/tthhongs/build_tthongs/tasks_aa_ii/issues/REPORT_004_nvidia_driver_and_system_audit.md`  

---

## Executive Summary

This comprehensive incident report and system audit log documents the root-cause diagnosis, resolution, and health audit across three key areas:

1. **NVIDIA Driver Deadlock & Boot Hang Recovery**: Resolved early boot hangs (`Load Kernel Modules 1min 30s`) and SDDM/KWin Wayland crashes caused by an `rw-semaphore` deadlock in precompiled binary modules (`linux-cachyos-nvidia-open`). Migrated to locally compiled `nvidia-open-dkms 610.57.04-1` with full header support for both active and LTS kernels.
2. **Locale Character Encoding Calibration**: Resolved XKB and Konsole compose table lookup failures (`kwin_wayland: couldn't find a Compose file for locale "en_IN"`) by generating explicit `.UTF-8` declarations in `/etc/locale.conf` and provisioning `fix_locale_utf8.sh`.
3. **GPU Power Management & Suspend Architecture Audit**: Evaluated runtime power management (`NVreg_DynamicPowerManagement=0x02`) versus system suspend VRAM retention (`NVreg_PreserveVideoMemoryAllocations=1`). Confirmed that with suspend features unused by the operator, maintaining the default configuration maximizes runtime performance with zero RAM/disk dumping overhead.

---

## Part 1: NVIDIA Open Kernel Module Deadlock Diagnostics & Fix

### 1.1 Deadlock Mechanism
During early boot (session `-3`), `systemd-modules-load.service` initiated driver insertion for `nvidia`, `nvidia_modeset`, `nvidia_uvm`, and `nvidia_drm`. A hard kernel deadlock occurred:
* `kworker/2:1:129` executing ACPI NVPCF notification (`rm_acpi_nvpcf_notify -> rmapiLockAcquire -> os_acquire_rwlock_write`) blocked on an `rw-semaphore`.
* The semaphore was held by `(udev-worker):186` executing device initialization (`nv_drm_register_drm_device -> nv_drm_dev_load -> RmInitAdapter -> kgspInitRm_IMPL`).
* Because `udev-worker` was blocked in uninterruptible sleep state (`D`), `systemd-udevd` killed the worker after 122 seconds, leaving the DRM device node unregistered.
* SDDM / KWin Wayland failed to find a valid display platform backend, dropping to a black screen with a frozen cursor.
* During shutdown, `nvidia-powerd` hung attempting to communicate with the deadlocked driver until forced kill timeouts expired.

### 1.2 Remediation & Commands
```bash
# 1. Install kernel headers and dynamic module build infrastructure
sudo pacman -S --needed linux-cachyos-headers linux-cachyos-lts-headers nvidia-open-dkms dkms

# 2. Verify DKMS module compilation across both kernels
dkms status

# 3. Regenerate early initramfs images
sudo mkinitcpio -P

# 4. Verify GPU communication & KMS registration on active boot
nvidia-smi
lsmod | grep -iE "nvidia|drm"
journalctl -b 0 -p 3 --no-pager
```

---

## Part 2: Locale UTF-8 Encoding & XKB Compose Table Calibration

### 2.1 Problem Diagnosis
KWin Wayland and Konsole logged repeated warnings:
```text
kwin_wayland: XKB: [XKB-679] No Compose file for locale "en_IN.ISO8859-1": locale is either invalid or not installed
kwin_wayland: XKB: [XKB-679] couldn't find a Compose file for locale "en_IN" (mapped to "en_IN.ISO8859-1")
konsole: failed to create compose table
```
Because `/etc/locale.conf` specified `LANG=en_IN` without `.UTF-8`, XKB/libxkbcommon defaulted to legacy `ISO8859-1`, for which no compose table mapping exists.

### 2.2 Solution & Automation Script
Created and provisioned `fix_locale_utf8.sh` to update `/etc/locale.conf`:
```ini
LANG=en_IN.UTF-8
LC_ADDRESS=en_IN.UTF-8
LC_IDENTIFICATION=en_IN.UTF-8
LC_MEASUREMENT=en_IN.UTF-8
LC_MONETARY=en_IN.UTF-8
LC_NAME=en_IN.UTF-8
LC_NUMERIC=en_IN.UTF-8
LC_PAPER=en_IN.UTF-8
LC_TELEPHONE=en_IN.UTF-8
LC_TIME=en_IN.UTF-8
```
Regenerated locales via `sudo locale-gen`.

---

## Part 3: GPU Power Management Architecture & Suspend Evaluation

### 3.1 Runtime Power Management vs Suspend Memory Preservation
* **Dynamic Runtime Power Management (`NVreg_DynamicPowerManagement=0x02`):**
  Active on the system. When idle, the RTX 4050 enters low-power RTD3 (Runtime D3) states and powers on dynamically when PRIME offload workloads (e.g., Tekken 8, Vulkan/CUDA applications) are invoked.
* **System Suspend VRAM Preservation (`NVreg_PreserveVideoMemoryAllocations`):**
  Engages only when the entire system enters S3 or `s2idle` sleep states (`systemctl suspend`). When enabled, `nvidia-suspend.service` dumps VRAM allocations to `/var/tmp` before sleep and `nvidia-resume.service` restores them upon wake.
* **Operational Assessment:**
  Because the operator does not utilize system suspend/sleep, leaving sleep hooks disabled is optimal:
  - Zero disk I/O overhead on shutdown or sleep transitions.
  - Zero reserved memory in `/var/tmp`.
  - Full stability and maximum hardware utilization during active desktop and gaming sessions.

---

## Part 4: Health Verification Matrix

| Subsystem / Metric | Target Status | Observed Status | Verdict |
| :--- | :--- | :--- | :--- |
| **Active Kernel** | `7.1.8-1-cachyos` | `7.1.8-1-cachyos` | ✅ Healthy |
| **NVIDIA DKMS (7.1.8)** | `installed` | `nvidia/610.57.04, 7.1.8-1-cachyos: installed` | ✅ Healthy |
| **NVIDIA DKMS (6.18.42)** | `installed` | `nvidia/610.57.04, 6.18.42-1-cachyos-lts: installed` | ✅ Healthy |
| **Kernel Headers** | Verified clean | `0 missing files` (headers installed) | ✅ Healthy |
| **Initramfs DRM Hooks** | `nvidia*` modules in initramfs | `/etc/mkinitcpio.conf.d/10-chwd.conf` active | ✅ Healthy |
| **GPU Communication** | `nvidia-smi` active | Driver `610.57.04`, CUDA `13.3`, PID 1103 Wayland active | ✅ Healthy |
| **Current Boot Errors** | Zero deadlocks / zero failed units | `journalctl -b 0 -p 3` clean, `0 failed units` | ✅ Healthy |
