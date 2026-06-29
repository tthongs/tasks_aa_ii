# ISSUE_009: [BUG] Bluetooth Firmware Loading Failure (MediaTek MT7922)

**Status**: Resolved
**Priority**: High
**Affected Directory**: /lib/firmware/mediatek

## Description
The MediaTek MT7922 Bluetooth controller (hci0) fails to load its RAM patch
firmware file `BT_RAM_CODE_MT7922_1_1_hdr.bin` during system boot. This causes
the Bluetooth hardware to fallback to a degraded ROM-only mode. In this mode,
standard scanning might work, but advanced Bluetooth functions (such as Low
Energy BLE advertisements needed for RQuickShare/Quick Share discovery) will
fail with errors like `Failed to register advertisement: Invalid Parameters
(0x0d)`.

Kernel dmesg logs show:
```
bluetooth hci0: Direct firmware load for mediatek/BT_RAM_CODE_MT7922_1_1_hdr.bin failed with error -2
Bluetooth: hci0: Failed to load firmware file mediatek/BT_RAM_CODE_MT7922_1_1_hdr.bin (-2)
```

The system has the compressed ZSTD file
`/lib/firmware/mediatek/BT_RAM_CODE_MT7922_1_1_hdr.bin.zst`, but the kernel
firmware loader is unable to locate or load it, likely due to early boot
timing, missing initramfs decompression modules, or driver limitations.

## Steps to Reproduce
1. Check kernel dmesg logs for Bluetooth firmware load errors:
   `sudo dmesg | grep -i hci0`
2. Check if the uncompressed file is missing:
   `ls -l /lib/firmware/mediatek/BT_RAM_CODE_MT7922_1_1_hdr.bin`
3. Attempt BLE advertising in RQuickShare and observe registration failures.

## Proposed Solution / Action Items
- [x] Decompress the firmware patch file from its ZSTD-compressed source to the
      expected plain `.bin` file in `/lib/firmware/mediatek/`.
- [x] Stop the Bluetooth service, reload the `btusb` kernel module to load the
      new firmware, and restart the Bluetooth service.
- [x] Restart RQuickShare to restore full advertisement capabilities.

## Notes
A fix script `fix_bluetooth_firmware.sh` has been created to decompress the
firmware and reload the Bluetooth kernel driver. Run it with root privileges:
```bash
sudo ./fix_bluetooth_firmware.sh
```
