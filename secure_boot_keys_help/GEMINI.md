# Project Overview: Secure Boot Keys Help

This directory serves as a central reference and workspace for managing Linux Secure Boot keys. It provides instructions and command references for enrolling custom keys (MOK), using automated tools like `sbctl`, and signing bootloader components or kernel modules.

## Key Concepts

*   **PK (Platform Key):** The hardware root of trust.
*   **KEK (Key Exchange Key):** Used to sign updates for the signature database.
*   **db (Signature Database):** Whitelist of trusted binaries.
*   **dbx (Forbidden Database):** Revocation list (blacklist).
*   **MOK (Machine Owner Key):** User-managed keys for Linux environments.

## Common Operations

### Checking Status
```bash
# Verify Secure Boot state
mokutil --sb-state

# List enrolled MOKs
mokutil --list-enrolled
```

### Using `sbctl` (Recommended for modern setups)
1.  **Check Status:** `sudo sbctl status`
2.  **Create Keys:** `sudo sbctl create-keys`
3.  **Enroll Keys:** `sudo sbctl enroll-keys -m` (include Microsoft keys for dual-boot)
4.  **Sign Binaries:** `sudo sbctl sign -s /boot/vmlinuz-linux`

### Manual MOK Enrollment (For DKMS/NVIDIA drivers)
1.  **Generate Key:**
    ```bash
    openssl req -new -x509 -newkey rsa:2048 -nodes -days 36500 \
      -outform DER -keyout MOK.priv -out MOK.der \
      -subj "/CN=My Custom Key/"
    ```
2.  **Import to NVRAM:** `sudo mokutil --import MOK.der`
3.  **Reboot:** Complete enrollment in the UEFI "MokManager" screen.

## Safety Guidelines

*   **Always backup your BIOS/UEFI settings.**
*   **Dual-Booting:** Ensure Microsoft keys are enrolled if Windows is installed.
*   **Setup Mode:** Most custom enrollments (except MOK) require the BIOS to be in "Setup Mode" (Keys cleared).

## Usage
Add scripts, keys (securely), and specific platform notes to this directory as needed for your local environment.
