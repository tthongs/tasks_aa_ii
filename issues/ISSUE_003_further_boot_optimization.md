# ISSUE_003_further_boot_optimization.md

# [TASK] Further Boot Optimization: Service Level Bottlenecks

**Status**: Resolved
**Priority**: High
**Affected Directory**: /etc/systemd/system, /etc/default/grub

## Description
Following initial optimizations to the GRUB loader and initramfs compression (which reduced loader time from ~4m to 20s), the userspace boot phase still exhibits significant delays. Analysis of the latest `systemd-analyze blame` (captured in `img/20260529_095952.jpg`) identifies two primary offenders:
1. `cachyos-rate-mirrors.service`: 59.2s
2. `NetworkManager-wait-online.service`: 30.1s

## Analysis
- **cachyos-rate-mirrors.service**: Although the summary suggests this is timer-triggered, it is appearing as a top offender in the boot blame. This indicates it is likely part of the `multi-user.target` or `graphical.target` dependency chain, or the timer is firing immediately on boot and blocking other services.
- **NetworkManager-wait-online.service**: This service waits for a full network connection before allowing the boot to proceed to the next target. On most laptops, this is unnecessary and adds a flat 30s delay if the network is slow to associate.
- **systemd-journal-flush.service**: 15s delay suggests a large journal or slow disk I/O during the flush operation.

## Proposed Solution / Action Items
- [x] Disable `NetworkManager-wait-online.service` as it is typically not required for desktop environments.
- [x] Investigate `cachyos-rate-mirrors.timer`. Change it to `OnBootSec=10min` or `OnUnitInactiveSec=1w` to ensure it doesn't run during the critical boot path.
- [x] Vacuum the systemd journal to reduce flush time: `journalctl --vacuum-time=2d`.
- [x] Check if `cachyos-rate-mirrors.service` can be made `Type=oneshot` with `RemainAfterExit=no` and removed from the boot dependency chain.

## Notes
The fixes were applied via `optimize_boot_services.sh` on May 29, 2026. 26MB of journal data was cleared, and the mirror rating was successfully delayed via a systemd override.
