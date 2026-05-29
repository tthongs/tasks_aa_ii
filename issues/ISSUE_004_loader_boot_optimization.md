# ISSUE_004_loader_boot_optimization.md

# [TASK] Further Boot Optimization: Loader Phase Bottleneck

**Status**: Resolved
**Priority**: High
**Affected Directory**: /boot, /etc/default/grub, /etc/mkinitcpio.conf

## Description
Despite userspace optimizations, the total boot time remained high (~1m 15s). The primary bottleneck was the "loader" phase (52.967s), caused by a massive 231MB initramfs image being loaded via slow EFI disk I/O.

## Analysis
- **Loader (52.967s)**: The delay was primarily due to the size of the initramfs. 
    - The `kms` hook was adding ~126MB of uncompressed NVIDIA GSP firmware and various GPU drivers to the "Early CPIO" segment.
    - The compression was set to `lz4`, which is fast but results in much larger files than `zstd`.
- **Early CPIO**: Contained 126MB of uncompressed assets, which GRUB has to read before decompression even starts.

## Actions Taken
- [x] Switched `mkinitcpio` compression to `zstd` with level `-3` to minimize total file size (reducing slow EFI disk reads) while maintaining extremely fast decompression.
- [x] Removed `kms` and `plymouth` hooks from `/etc/mkinitcpio.conf`.
    - This moved essential modules (NVIDIA, NVMe) to the main compressed CPIO segment and removed redundant/bloated firmware from the early segment.
- [x] Reduced initramfs size from **231MB** to **97MB** (a 58% reduction).
- [x] Reduced "Early CPIO" segment from **126MB** to **9MB** (a 93% reduction).

## Verification
- `lsinitcpio -a` confirms that `nvidia` and `nvme` modules are still present.
- File size reduction verified with `ls -lh`.
- Expected improvement: ~30-40s reduction in the "loader" phase.

## Notes
The fixes were applied on May 29, 2026. The system should now boot significantly faster.
