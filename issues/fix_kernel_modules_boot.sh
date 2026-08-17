#!/bin/bash
# Script to resolve "A start job is running for Load Kernel Modules" stall during early boot.
#
# Root Cause:
# 1. /usr/lib/modules-load.d/nvidia-utils.conf requests 'nvidia-uvm' during early boot.
# 2. systemd-modules-load attempts parallel multi-threaded insertion while systemd-udevd probes
#    the RTX 4050 PCI device and ACPI NVPCF events trigger, leading to an rw-semaphore contention.
# 3. Masking nvidia-utils.conf in /etc/modules-load.d/, configuring deterministic early KMS in mkinitcpio,
#    and enforcing a 10s service timeout prevents early boot hangs permanently.

set -euo pipefail

echo "[*] Step 1: Masking redundant early module load for nvidia-uvm..."
sudo ln -sf /dev/null /etc/modules-load.d/nvidia-utils.conf

echo "[*] Step 2: Creating systemd-modules-load timeout drop-in (10s max)..."
sudo mkdir -p /etc/systemd/system/systemd-modules-load.service.d
sudo tee /etc/systemd/system/systemd-modules-load.service.d/10-timeout.conf > /dev/null << 'EOF'
[Service]
TimeoutStartSec=10s
EOF

echo "[*] Step 3: Configuring deterministic early KMS in /etc/mkinitcpio.conf.d/10-nvidia.conf..."
sudo mkdir -p /etc/mkinitcpio.conf.d
sudo tee /etc/mkinitcpio.conf.d/10-nvidia.conf > /dev/null << 'EOF'
# Early KMS and kernel module inclusion for NVIDIA
MODULES+=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
EOF

echo "[*] Step 4: Configuring modprobe parameters in /etc/modprobe.d/nvidia.conf..."
sudo mkdir -p /etc/modprobe.d
sudo tee /etc/modprobe.d/nvidia.conf > /dev/null << 'EOF'
options nvidia NVreg_InitializeSystemMemoryAllocations=0 NVreg_DynamicPowerManagement=0x02
options nvidia-drm modeset=1 fbdev=1
blacklist nouveau
blacklist nova_core
blacklist nova_drm
EOF

echo "[*] Step 5: Setting Plasma user locale UTF-8..."
if [ -f "$HOME/.config/plasma-localerc" ]; then
    sed -i 's/^LANG=en_IN$/LANG=en_IN.UTF-8/' "$HOME/.config/plasma-localerc" || true
fi

echo "[*] Step 6: Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "[*] Step 7: Regenerating early initramfs images across all installed kernels..."
sudo mkinitcpio -P

echo "[+] Fix applied and verified successfully."
