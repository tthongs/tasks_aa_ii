# [TASK] Configure OpenSSH Server, Firewall, and Remote Access

**Status**: In Progress
**Priority**: High
**Affected Directory**: `/etc/ssh/`, `/etc/ssh/sshd_config.d/`, `~/.ssh/`, System / Network (UFW Firewall)

## Description
Configure OpenSSH server daemon (`sshd`) and firewall rules so that the user can SSH into this machine (`aspire79g`, user `tthhongs`) from anywhere—including locally from any session on this machine, from any device connected to the local Wi-Fi / LAN, and optionally from anywhere across the internet via Tailscale mesh VPN without risky router port forwarding.

## Current State & Root Cause Analysis
1. **OpenSSH Server Daemon**: OpenSSH 10.5p1 is installed, but `sshd.service` is `disabled` and `inactive (dead)`.
2. **Missing Host Keys**: Host keys in `/etc/ssh/` have not yet been generated (`sshd: no hostkeys available`).
3. **Firewall Policy**: The system firewall (`ufw`) is active with a default-deny incoming policy, blocking incoming traffic on port 22 (SSH).
4. **Authorized Keys**: User `tthhongs` had an active Ed25519 keypair in `~/.ssh/id_ed25519` but no `~/.ssh/authorized_keys` file configured for passwordless loopback/local authentication.

## Proposed Solution / Action Items
- [x] **Configured Local User Keys**: Added user's `~/.ssh/id_ed25519.pub` to `~/.ssh/authorized_keys` with strict permissions (0700 dir, 0600 file) to enable instant passwordless loopback/local authentication.
- [x] **Created Automated Setup Script**: Built [`setup_remote_ssh.sh`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/setup_remote_ssh.sh) to handle host key generation, daemon drop-in configuration, UFW firewall allowance, and service enablement.
- [x] **Configured OpenSSH Drop-in**: Created `/etc/ssh/sshd_config.d/10-remote-access.conf` enforcing standard secure parameters (Port 22, PubkeyAuthentication yes, PasswordAuthentication yes, KeepAlive intervals).
- [x] **Configured Firewall Rules**: Included `ufw allow 22/tcp comment 'OpenSSH Server Remote Access'` in the setup pipeline.
- [x] **Prepared Tailscale VPN Option**: Added seamless `--tailscale` switch for secure access from anywhere on the global internet without CGNAT/router port forwarding hurdles.
- [x] **Documented Commands**: Added Section 19 to [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt).
- [x] **Updated GEMINI.md**: Added `ISSUE_022` to the issue tracking index.

## Verification
- Validated script syntax with `bash -n setup_remote_ssh.sh`.
- Verified `~/.ssh/authorized_keys` contains `id_ed25519.pub`.
- Script performs `sshd -t` configuration validation before activating the service.
- Local and network connection commands documented for immediate execution.
