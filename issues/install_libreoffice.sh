#!/bin/bash
# install_libreoffice.sh - Automated installer and verifier for LibreOffice suite on Arch/CachyOS
#
# Usage: sudo ./install_libreoffice.sh

set -e

# 1. Root privilege validation
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: Please run this script with sudo or as root."
    echo "    Usage: sudo $0"
    exit 1
fi

echo "[+] Starting LibreOffice suite installation and environment configuration..."

# 2. Package list definitions
PACKAGES=(
    "libreoffice-fresh"
    "hunspell-en_us"
    "hunspell-en_gb"
    "hyphen-en"
    "mythes-en"
    "libmythes"
)

echo "[+] Target packages to install/verify: ${PACKAGES[*]}"

# 3. Synchronize and install packages via pacman
echo "[+] Running pacman installation..."
pacman -S --needed --noconfirm "${PACKAGES[@]}"

# 4. Verify binary availability
echo "[+] Verifying LibreOffice binary..."
if command -v libreoffice >/dev/null 2>&1; then
    SOFFICE_VER=$(libreoffice --version 2>/dev/null || true)
    echo "[✓] LibreOffice installed successfully: ${SOFFICE_VER}"
else
    echo "[-] Error: libreoffice binary not found in PATH."
    exit 1
fi

# 5. Verify desktop application entries for KDE Plasma / Wayland
DESKTOP_DIR="/usr/share/applications"
APPS=(
    "libreoffice-writer.desktop"
    "libreoffice-calc.desktop"
    "libreoffice-impress.desktop"
    "libreoffice-draw.desktop"
    "libreoffice-math.desktop"
    "libreoffice-base.desktop"
    "libreoffice-startcenter.desktop"
)

echo "[+] Verifying desktop launcher entries..."
for app in "${APPS[@]}"; do
    if [ -f "${DESKTOP_DIR}/${app}" ]; then
        echo "  [✓] Found launcher: ${app}"
    else
        echo "  [!] Warning: Missing launcher: ${app}"
    fi
done

# 6. Update desktop database and MIME cache
echo "[+] Updating desktop MIME and icon caches..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    echo "[+] Updating KDE Sycoca6 cache..."
    kbuildsycoca6 --noincremental 2>/dev/null || true
fi

echo "[✓] LibreOffice suite setup completed successfully."
