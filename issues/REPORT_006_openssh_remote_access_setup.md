# REPORT 006: OpenSSH Server Deployment, UFW Firewall Integration, Tailscale Mesh Tunnel, and Cross-Platform Client Access

**Date**: 2026-09-06  
**Author**: Antigravity AI  
**Target System**: Acer Aspire A715-79G (`aspire79g`)  
**OS**: CachyOS Linux (Arch Linux derivative), Kernels: `7.1.8-1-cachyos` (Active) | `6.18.42-1-cachyos-lts`  
**Primary Operator**: `tthhongs` (`sanskarsinghss123@gmail.com`)  
**Client Environment**: Windows 11 Pro Laptop (PowerShell, Windows Terminal, VS Code)  
**Location**: `/home/tthhongs/build_tthongs/tasks_aa_ii/issues/REPORT_006_openssh_remote_access_setup.md`  

---

## 1. Executive Summary

This report documents the architectural design, implementation, security hardening, cross-platform client integration, and incident troubleshooting for provisioning headless remote access to the primary Linux development machine (`aspire79g`).

The deployment addresses two access models:
1. **Local Area Network (LAN / Wi-Fi)**: Zero-latency shell and VS Code development via mDNS hostname resolution (`aspire79g.local`) and direct private IP (`192.168.1.12`).
2. **Global Wide Area Network (WAN / Internet)**: Seamless remote access over any internet connection (residential Wi-Fi, mobile hotspots, corporate networks) using an end-to-end encrypted WireGuard mesh tunnel powered by Tailscale, completely bypassing NAT and avoiding risky public port forwarding.

Additionally, this report records the diagnostic analysis and root-cause resolution of an initial authentication failure encountered on the Windows 11 Pro client.

---

## 2. Architecture & Threat Model

```
+-------------------------------------------------------------------------------+
|                             CLIENT ENVIRONMENTS                               |
|                                                                               |
|  [Windows 11 Pro Laptop]                  [Secondary Devices / Mobile]         |
|   - PowerShell / Windows Terminal          - Android / iOS / macOS            |
|   - VS Code (Remote - SSH)                 - Termius / Native Terminal        |
+-----------------------+---------------------------------------+---------------+
                        |                                       |
       [Local Wi-Fi Subnet]                                     | [Internet / Cellular]
      (192.168.1.x / mDNS)                                      | (WireGuard Overlay)
                        |                                       |
                        v                                       v
         +------------------------------+       +-------------------------------+
         |   UFW Firewall (Port 22)     |       |   Tailscale Virtual Network   |
         |   - State: Active            |       |   - Interface: tailscale0     |
         |   - Inbound: 22/tcp ALLOW    |       |   - Mesh encryption: ChaCha20 |
         +--------------+---------------+       +---------------+---------------+
                        |                                       |
                        +-------------------+-------------------+
                                            |
                                            v
                        +---------------------------------------+
                        |      OpenSSH Server Daemon (sshd)     |
                        |      - Drop-in: 10-remote-access.conf |
                        |      - Port: 22 (0.0.0.0 & [::])      |
                        |      - Host Keys: Ed25519, RSA, ECDSA |
                        |      - PAM & Key Authentication       |
                        +-------------------+-------------------+
                                            |
                                            v
                        +---------------------------------------+
                        |       Target User: `tthhongs`         |
                        |       - Shell: /bin/bash              |
                        |       - Home: /home/tthhongs          |
                        |       - Key Store: ~/.ssh/auth_keys   |
                        +---------------------------------------+
```

### Security Considerations & Design Decisions
- **No Inbound Port Forwarding on Border Router**: Opening port 22 on consumer routers exposes SSH daemons to continuous automated brute-force botnets across the globe. Tailscale utilizes outbound NAT traversal (STUN/DERP) to establish direct point-to-point WireGuard peers, completely hiding port 22 from the public internet.
- **Drop-in Configuration Paradigm**: Rather than modifying package-managed files like `/etc/ssh/sshd_config`, all custom server parameters are isolated in `/etc/ssh/sshd_config.d/10-remote-access.conf` ensuring resilience across pacman system upgrades.
- **File & Directory Permissions**: Enforced strict POSIX access controls: `0700` on `~/.ssh` and `0600` on `authorized_keys` to satisfy OpenSSH strict modes.

---

## 3. Step-by-Step Implementation Breakdown

### 3.1 Host Key Generation & Directory Setup
Ensured host keys existed and initialized local user key authentication:
```bash
# Generate missing host keys if uninitialized
sudo ssh-keygen -A

# Enforce secure permission structure on user SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Authorize local Ed25519 public key for passwordless loopback access
if [ -f ~/.ssh/id_ed25519.pub ]; then
    grep -q -F "$(cat ~/.ssh/id_ed25519.pub)" ~/.ssh/authorized_keys || cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
fi
```

### 3.2 OpenSSH Server Configuration
Configured drop-in `/etc/ssh/sshd_config.d/10-remote-access.conf`:
```ini
# /etc/ssh/sshd_config.d/10-remote-access.conf
# Managed by Antigravity AI - Remote Access Configuration

Port 22
ListenAddress 0.0.0.0
ListenAddress ::

# Authentication
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication yes
KbdInteractiveAuthentication yes

# Keep-alive intervals to avoid disconnections on dormant sessions
ClientAliveInterval 60
ClientAliveCountMax 3

# Environment and forwarding
X11Forwarding yes
AllowTcpForwarding yes
```

### 3.3 UFW Firewall Configuration
Permitted incoming SSH traffic through the kernel netfilter via UFW:
```bash
sudo ufw allow 22/tcp comment 'OpenSSH Server Remote Access'
sudo ufw reload
```

### 3.4 Service Daemon Enablement
Activated and enabled the OpenSSH daemon and Tailscale service across system reboots:
```bash
sudo systemctl enable --now sshd.service
sudo systemctl enable --now tailscaled.service
```

### 3.5 Automation Script Deployment
Created [`setup_remote_ssh.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/setup_remote_ssh.sh) in `issues/` containing self-healing checks, automatic dependency installation, status reporting, and key provisioning flags.

---

## 4. Client Integration & Connection Guide (Windows 11 Pro)

### Mode A: Local Wi-Fi Connection (Same Router / Subnet)
Windows 11 includes native mDNS support (`avahi`/Bonjour protocol):
```powershell
# Option 1: Via local mDNS hostname (Recommended)
ssh tthhongs@aspire79g.local

# Option 2: Via local IPv4 address
ssh tthhongs@192.168.1.12
```

### Mode B: Anywhere on the Internet (Tailscale Mesh VPN)
1. **One-Time Machine Link (Linux)**:
   Authenticate the Linux machine by signing in at:
   ```text
   https://login.tailscale.com/a/598b4750119c2
   ```
2. **Install Tailscale on Windows 11**:
   In PowerShell (Admin or User):
   ```powershell
   winget install tailscale.tailscale
   ```
   Or install via [tailscale.com/download/windows](https://tailscale.com/download/windows).
3. **Sign In**:
   Click the Tailscale system tray icon and log in using the exact same identity provider (Google/GitHub/Microsoft).
4. **Connect from Anywhere**:
   ```powershell
   ssh tthhongs@aspire79g
   ```

### Mode C: Visual Studio Code Remote Development
To edit files, run debugging sessions, and run terminal tasks inside `tasks_aa_ii` directly from the Windows 11 laptop:
1. Install **Remote - SSH** (`ms-vscode-remote.remote-ssh`) from the VS Code Extensions Marketplace on Windows 11.
2. Press `Ctrl + Shift + P` -> Select **Remote-SSH: Connect to Host...**
3. Enter `tthhongs@aspire79g` (or `tthhongs@aspire79g.local` on local Wi-Fi).
4. Select `Linux` as the remote platform.
5. Open `/home/tthhongs/build_tthongs/tasks_aa_ii/` to begin developing seamlessly.

---

## 5. Diagnostic Incident Analysis (Windows 11 Client)

### Incident Description
During initial connection verification from the Windows 11 Pro client over local Wi-Fi, the user reported an authentication rejection:
```text
Permission denied (publickey,password).
```
The terminal snapshot was captured in `20260906_135246.jpg`.

### Diagnostic Investigation & Log Inspection
Querying `journalctl -u sshd -n 30` revealed:
```text
Sep 06 13:52:45 aspire79g sshd-session[4130]: Invalid user tthhhongs from 192.168.1.9 port 60234
Sep 06 13:52:45 aspire79g sshd-session[4130]: error: PAM: User not known to the underlying authentication module for illegal user tthhhongs
Sep 06 13:52:48 aspire79g sshd-session[4130]: Failed password for invalid user tthhhongs from 192.168.1.9 port 60234 ssh2
Sep 06 13:52:48 aspire79g sshd-session[4130]: Connection closed by invalid user tthhhongs 192.168.1.9 port 60234 [preauth]
```

### Root Cause
- The networking path, Wi-Fi routing, ARP resolution, and UFW firewall rule were completely functioning: packet traffic from `192.168.1.9` reached port 22 on `192.168.1.12`.
- The failure was strictly an **identity typo**: the client invoked `ssh tthhhongs@192.168.1.12` containing **three 'h' characters** instead of the valid system account **`tthhongs`** (two 'h' characters).
- Because `tthhhongs` does not exist in `/etc/passwd`, Linux PAM rejected authentication outright.

### Resolution
Executing the command with the correct username:
```powershell
ssh tthhongs@192.168.1.12
# or
ssh tthhongs@aspire79g.local
```
allows successful password entry and shell initialization.

---

## 6. Verification Matrix

| Checkpoint | Target / Service | Method / Command | Expected Value | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Daemon Health** | OpenSSH Server | `systemctl is-active sshd` | `active` | ✅ PASS |
| **Mesh VPN Health** | Tailscale Daemon | `systemctl is-active tailscaled` | `active` | ✅ PASS |
| **Port Binding** | IPv4 & IPv6 Port 22 | `ss -tln \| grep :22` | `0.0.0.0:22` & `[::]:22` LISTEN | ✅ PASS |
| **Firewall Netfilter** | UFW Rule | `ufw status \| grep 22/tcp` | `22/tcp ALLOW In` | ✅ PASS |
| **Loopback SSH** | Local Session | `ssh -o BatchMode=yes localhost whoami` | `tthhongs` | ✅ PASS |
| **mDNS Resolution** | Local Avahi/Bonjour | `ssh -o BatchMode=yes aspire79g.local whoami`| `tthhongs` | ✅ PASS |
| **Network Reachability**| Windows 11 Client | Inbound connection from `192.168.1.9` | Handshake established | ✅ PASS |
| **Configuration Files** | Drop-in configuration | `sshd -t` | Syntax valid | ✅ PASS |

---

## 7. Recommended Next Optimization: Passwordless Key Authentication

To eliminate password prompts entirely when connecting from Windows 11:

1. On the Windows 11 laptop, check for an existing SSH key in PowerShell:
   ```powershell
   Get-Content ~\.ssh\id_ed25519.pub
   ```
   *(If not present, generate one via `ssh-keygen -t ed25519`)*.
2. Append the public key string to `/home/tthhongs/.ssh/authorized_keys` on `aspire79g`:
   ```bash
   echo "<PASTED_WINDOWS_PUBLIC_KEY>" >> ~/.ssh/authorized_keys
   ```
3. Future connections from Windows 11 will log in instantly and securely without manual password entry.
