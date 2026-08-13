# [TASK] KDE Connect Availability & Optimal UFW Firewall Configuration

**Status**: Resolved
**Priority**: Medium
**Affected Directory**: System / Network (UFW Firewall & KDE Connect)

## Description
KDE Connect was unable to detect or pair with mobile devices (e.g., Galaxy S25) on the local Wi-Fi network (`wlan0`, 192.168.1.0/24). While `kdeconnectd` was running and bound to UDP/TCP port 1716, the system firewall (`ufw`) was active with a default-deny incoming policy and zero allowed rules for KDE Connect, causing incoming discovery broadcasts and connection handshakes from mobile devices to be dropped.

## Root Cause
The `ufw` firewall service was active with a default policy of `deny (incoming)`. No explicit rules existed for KDE Connect's required port range (1714-1764 TCP/UDP), preventing device discovery broadcasts and bidirectional communication over the local network.

## Solution & Action Items
- [x] Inspected active firewall (`ufw`) status and confirmed active default-deny policy with no active rules.
- [x] Verified `kdeconnectd` daemon listening state on UDP/TCP port 1716.
- [x] Configured UFW to allow incoming traffic for the `KDE Connect` profile (`1714:1764/udp` and `1714:1764/tcp`).
- [x] Reloaded UFW ruleset.
- [x] Executed `kdeconnect-cli --refresh` to initiate device discovery over `wlan0`.
- [x] Created `fix_kdeconnect.sh` automation script.

## Verification
Executed `kdeconnect-cli -l` which immediately confirmed active network discovery:
`- Galaxy S25: 8b04d9a8de934fbb8173cb79a620050b on 192.168.1.11 via LAN (reachable)`
