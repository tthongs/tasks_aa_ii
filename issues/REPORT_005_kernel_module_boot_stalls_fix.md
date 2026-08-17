# REPORT 005: Resolution of Early Boot Kernel Module Load Hangs & Service Timeout Optimization

**Date**: 2026-08-18  
**Author**: Antigravity AI  
**Target System**: Acer Aspire A715-79G (CachyOS Linux / Arch Linux)  
**Kernels**: `7.1.8-1-cachyos` (Active) | `6.18.42-1-cachyos-lts`  
**Location**: `/home/tthhongs/build_tthongs/tasks_aa_ii/issues/REPORT_005_kernel_module_boot_stalls_fix.md`

---

## 1. Executive Summary

This report provides the complete architectural diagnosis, remediation steps, and verification logs for resolving boot stalls associated with:
```text
A start job is running for Load Kernel Modules (Xs / 1min 30s)
```

The issue stemmed from an asynchronous race condition between `systemd-modules-load.service` multi-threaded probe workers and `systemd-udevd` PCI device enumeration during early boot, aggravated by default 90-second systemd service timeouts.

---

## 2. Technical Root-Cause Analysis

1. **Distro Default File `/usr/lib/modules-load.d/nvidia-utils.conf`**:
   The package `nvidia-utils` ships with a default configuration containing `nvidia-uvm`.
   When `systemd-modules-load.service` runs, it invokes `modprobe nvidia-uvm`.
2. **Concurrent Lock Contention**:
   Loading `nvidia-uvm` triggers modprobe on `nvidia`, `nvidia_modeset`, and `nvidia_drm`.
   Because this ran simultaneously with `systemd-udevd` PCI initialization of the RTX 4050 Laptop GPU (`0000:01:00.0`) and ACPI NVPCF events (`rm_acpi_nvpcf_notify`), both execution contexts attempted to acquire the Resource Manager rw-semaphore (`rmapiLockAcquire -> os_acquire_rwlock_write`).
3. **90-Second System Freeze**:
   The thread was placed into uninterruptible sleep (`D-state`), blocking `systemd-modules-load.service` until the full 90s systemd timeout elapsed, producing the console error.

---

## 3. Implemented Fixes

### 3.1 Mask Early Userspace `nvidia-uvm` Loading
Masked the redundant modules-load file by creating a symlink in `/etc/modules-load.d/`:
```bash
sudo ln -sf /dev/null /etc/modules-load.d/nvidia-utils.conf
```
*Rationale*: CUDA applications and `nvidia-modprobe` autoload `nvidia-uvm` on demand when `/dev/nvidia-uvm` is accessed. It does not belong in early boot.

### 3.2 Add Systemd Drop-in Timeout Protection
Configured a 10-second timeout clamp in `/etc/systemd/system/systemd-modules-load.service.d/10-timeout.conf`:
```ini
[Service]
TimeoutStartSec=10s
```

### 3.3 Configure Deterministic Early KMS
Added `/etc/mkinitcpio.conf.d/10-nvidia.conf`:
```ini
MODULES+=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
```

### 3.4 Modprobe Parameters
Configured `/etc/modprobe.d/nvidia.conf`:
```ini
options nvidia NVreg_InitializeSystemMemoryAllocations=0 NVreg_DynamicPowerManagement=0x02
options nvidia-drm modeset=1 fbdev=1
blacklist nouveau
blacklist nova_core
blacklist nova_drm
```

### 3.5 KDE Plasma User Locale Fix
Updated `~/.config/plasma-localerc` from `LANG=en_IN` to `LANG=en_IN.UTF-8` to eliminate remaining compose table warnings.

### 3.6 Rebuilt Initramfs
Recompiled early initramfs across all kernels using `sudo mkinitcpio -P`.

---

## 4. Verification Matrix

| Component | Check | Result | Status |
| :--- | :--- | :--- | :--- |
| **Modules-Load Mask** | `/etc/modules-load.d/nvidia-utils.conf` | Points to `/dev/null` | ✅ Verified |
| **Service Timeout** | `systemd-modules-load.service` drop-in | `TimeoutStartSec=10s` | ✅ Verified |
| **Early KMS Modules** | `10-nvidia.conf` in mkinitcpio.conf.d | `MODULES+=(nvidia ...)` | ✅ Verified |
| **Initramfs Compilation** | `mkinitcpio -P` | `7.1.8-1-cachyos` & `6.18.42-1-cachyos-lts` Clean | ✅ Verified |
| **GPU Health** | `nvidia-smi` | GPU active, KWin Wayland rendering | ✅ Verified |
| **Service Status** | `systemctl is-active systemd-modules-load` | `active` | ✅ Verified |
