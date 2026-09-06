# [TASK] Configure OpenSSH Server, Firewall, and Remote Access

**Status**: Resolved
**Priority**: High
**Affected Directory**: `/etc/ssh/`, `/etc/ssh/sshd_config.d/`, `~/.ssh/`, System / Network (UFW Firewall)

## Description
Configure OpenSSH server daemon (`sshd`), firewall rules, and Tailscale mesh VPN so that the user can SSH into this machine (`aspire79g`, user `tthhongs`) from anywhere on the internet from their other work laptop, as well as locally from any session or local Wi-Fi device without router port forwarding.

## Current State & Root Cause Analysis
1. **OpenSSH Server Daemon**: OpenSSH 10.5p1 is installed, but `sshd.service` was disabled and inactive.
2. **Missing Host Keys**: Host keys in `/etc/ssh/` were uninitialized.
3. **Firewall Policy**: The system firewall (`ufw`) was active with default-deny incoming policy.
4. **Internet Routing / NAT**: The machine sits behind residential CGNAT / Wi-Fi router, preventing unsolicited inbound WAN connections without an encrypted mesh tunnel.

## Solution & Action Items
- [x] **Configured Local User Keys**: Added user's `~/.ssh/id_ed25519.pub` to `~/.ssh/authorized_keys` with strict permissions (0700 dir, 0600 file) for instant passwordless logins.
- [x] **Executed Automated Setup Script**: Ran [`setup_remote_ssh.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/setup_remote_ssh.sh) with `--tailscale`.
- [x] **Generated Host Keys**: Initialized RSA, ECDSA, Ed25519 host keys in `/etc/ssh/`.
- [x] **Configured OpenSSH Drop-in**: Created `/etc/ssh/sshd_config.d/10-remote-access.conf` enforcing standard secure parameters (Port 22, PubkeyAuthentication yes, PasswordAuthentication yes, KeepAlive intervals).
- [x] **Configured Firewall Rules**: Added rule `ufw allow 22/tcp comment 'OpenSSH Server Remote Access'` and reloaded UFW.
- [x] **Enabled Services**: Started and enabled `sshd.service` and `tailscaled.service`.
- [x] **Initiated Tailscale Authentication**: Launched `tailscale up --ssh --operator=tthhongs` to bind machine to user's private tailnet.
- [x] **Documented Commands**: Added Section 19 to [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt).
- [x] **Updated GEMINI.md**: Marked `ISSUE_022` as `[RESOLVED]`.

## Verification
- Verified `sshd.service` is actively running (`systemctl is-active sshd` -> active).
- Verified `tailscaled.service` is actively running (`systemctl is-active tailscaled` -> active).
- Verified listening TCP sockets on port 22 (`0.0.0.0:22` and `[::]:22`).
- Verified local loopback SSH login: `ssh localhost whoami` succeeded and returned `tthhongs`.
- Verified local mDNS SSH login: `ssh aspire79g.local whoami` succeeded and returned `tthhongs`.
- Verified UFW status: port 22/tcp is allowed for IPv4 and IPv6.
- Tailscale authentication URL generated and ready for node activation: `https://login.tailscale.com/a/598b4750119c2`.

## Windows 11 Pro Client Setup & Usage
1. **Via Tailscale (Anywhere on the Internet)**:
   - Install via PowerShell (Windows Terminal): `winget install tailscale.tailscale` (or download from `tailscale.com/download/windows`).
   - Sign into Tailscale using the same account as `aspire79g`.
   - Open PowerShell or Windows Terminal and run:
     ```powershell
     ssh tthhongs@aspire79g
     ```
2. **Via Local Wi-Fi (Same Network)**:
   - Open PowerShell or Windows Terminal and run:
     ```powershell
     ssh tthhongs@aspire79g.local
     # Or directly via IP:
     ssh tthhongs@192.168.1.12
     ```
3. **VS Code Remote - SSH**:
   - Install the `Remote - SSH` extension on Windows 11.
   - Connect to `tthhongs@aspire79g` to develop directly on this Linux machine.

