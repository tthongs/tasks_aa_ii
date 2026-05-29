#!/bin/bash
# optimize_boot_services.sh
# Addresses bottlenecks identified in systemd-analyze blame

echo "Starting service-level boot optimization..."

# 1. Disable NetworkManager-wait-online.service
# This service often adds a 30s delay on laptops waiting for Wi-Fi.
echo "[1/3] Disabling NetworkManager-wait-online.service..."
sudo systemctl disable NetworkManager-wait-online.service

# 2. Delay cachyos-rate-mirrors.timer
# Move mirror rating to 10 minutes after boot to clear the startup path.
TIMER_CONF="/etc/systemd/system/cachyos-rate-mirrors.timer.d/override.conf"
echo "[2/3] Delaying cachyos-rate-mirrors.timer..."
sudo mkdir -p "$(dirname "$TIMER_CONF")"
echo -e "[Timer]\nOnBootSec=10min\nOnUnitInactiveSec=1w" | sudo tee "$TIMER_CONF" > /dev/null
sudo systemctl daemon-reload

# 3. Vacuum systemd journal
# Reduces time spent in systemd-journal-flush.service.
echo "[3/3] Vacuuming systemd journal (keeping 2 days)..."
sudo journalctl --vacuum-time=2d

echo "Optimization complete. Please reboot to verify the changes with 'systemd-analyze'."
