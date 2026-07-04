# ISSUE_008: [BUG] RQuickShare Discovery Failure on Android Devices

**Status**: Resolved
**Priority**: High
**Affected Directory**: /issues, ~/.local/share/dev.mandre.rquickshare

## Description
The Linux laptop running `rquickshare` is not visible on the Android
Quick Share (formerly Nearby Share) screen. This prevents files from being
transferred from Android to Linux.

Investigation reveals two primary root causes:
1. **Firewall Blocking**: The `ufw` service is active and blocks all incoming
   traffic. Since `rquickshare` defaults to a dynamic, OS-assigned TCP port for
   each execution, the firewall blocks these random ports and the mDNS multicast
   (UDP 5353) discovery packets.
2. **Bluetooth Advertisement Failure**: The `rquickshare` Bluetooth advertiser
   service fails to start, reporting:
   `Couldn't start BleAdvertiser: Bluetooth operation failed: Failed to register advertisement`
   with BlueZ reporting:
   `Failed to add advertisement: Invalid Parameters (0x0d)`.
   Android Quick Share requires discovering the Bluetooth advertisement before
   it attempts local network connection/discovery.

Additionally, running RQuickShare continuously in the background causes its BLE advertising/discovery mechanism to block BlueZ from reconnecting or pairing other Bluetooth devices (such as OnePlus Nord Buds 2R), leading to connection failures and timeouts.

## Steps to Reproduce
1. Start `rquickshare` on the laptop.
2. Open Quick Share on an Android device on the same local network.
3. Observe that the laptop does not appear in the discoverable devices list.
4. Check `~/.local/share/dev.mandre.rquickshare/logs/RQuickShare.log` and note
   the Bluetooth advertisement registration failure.

## Proposed Solution / Action Items
- [x] Configure `rquickshare` to use a static TCP/UDP port (`42428`) in
      `~/.local/share/dev.mandre.rquickshare/.settings.json`.
- [x] Open the static port (`42428/tcp` and `42428/udp`) in the UFW firewall.
- [x] Open the mDNS port (`5353/udp`) in the UFW firewall to allow network
      discovery.
- [x] Restart the Bluetooth daemon and power cycle the Bluetooth adapter to
      clear any stale advertisements and fix the registration error.
- [x] Set `"autostart": false` in settings to prevent RQuickShare from running automatically in the background on startup, avoiding interference with other Bluetooth devices.

## Notes
A resolution script `fix_rquickshare.sh` has been created to perform all of
these operations. Run the script from the `issues/` directory:
```bash
sudo ./fix_rquickshare.sh
```
This will set the static port, open the firewall rules, restart Bluetooth,
and launch the application in the background.
