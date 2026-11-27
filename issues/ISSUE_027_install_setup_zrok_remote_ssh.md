# [TASK] Install and Configure zrok CLI (v2.0.11) for Remote SSH

**Status**: In Progress  
**Priority**: High  
**Affected Directory**: `~/.local/bin/`, `~/.config/systemd/user/`, `~/.zrok2/`

## Description
Install and configure the `zrok` CLI (`zrok2` v2.0.11) on CachyOS (`aspire79g`) to provide an encrypted, zero-trust private TCP tunnel (`tcpTunnel`) to the local OpenSSH daemon (`localhost:22`) that starts automatically on boot.

## Implementation Details
1. **Binary Installation & Verification**:
   - Downloaded the official `openziti/zrok` release archive (`zrok_2.0.11_linux_amd64.tar.gz`) from GitHub Releases.
   - Verified archive integrity against the official `checksums.sha256.txt` digest (`4db2e2f0be382a9cdd415735520f7d0ac0715b799d54c922d7801cc35803dd8c`).
   - Installed `zrok2` to `~/.local/bin/zrok2` and created symlink `~/.local/bin/zrok -> ~/.local/bin/zrok2`.
2. **Shell PATH Integration**:
   - Added `~/.local/bin` to `$PATH` in `~/.bash_profile`, `~/.bashrc`, and `~/.zshrc` so `zrok` and `zrok2` resolve across login, bash, and zsh sessions.
3. **Boot Auto-Start & Systemd User Units**:
   - Confirmed `sshd.service` is active and enabled on port `22`, `NetworkManager-wait-online.service` is enabled, and `loginctl show-user tthhongs -p Linger` reports `Linger=yes` (so user systemd services start at boot before graphical login).
   - Created `~/.local/bin/zrok2-ssh-run` wrapper script, which auto-provisions and persists `ZROK_SSH_SHARE_TOKEN` in `~/.config/zrok2-ssh.env` (`0600`) on first run if not yet created, and executes `zrok2 share private --headless --force-local --backend-mode tcpTunnel --share-token "$ZROK_SSH_SHARE_TOKEN" localhost:22`.
   - Configured and **enabled** `~/.config/systemd/user/zrok2-ssh.service` (`WantedBy=default.target`, `After=network-online.target sshd.service`, `Restart=always`, `StartLimitIntervalSec=0`, gated by `ConditionPathExists=%h/.zrok2/environment.json`).
   - Configured, **enabled, and started** `~/.config/systemd/user/zrok2-ssh-auto.path` watching `~/.zrok2/environment.json` so running `zrok2 enable <token>` triggers `zrok2-ssh.service` immediately without requiring a manual service start or reboot.
   - Created optional `~/.config/systemd/user/zrok2-agent.service` (gated by `ConditionPathExists=%h/.zrok2/environment.json`).
   - Verified unit files with `systemd-analyze --user verify`.
4. **Automation & Helper Utilities**:
   - Created [`setup_zrok_ssh.sh`](file:///home/tthhongs/build_tthhongs/tasks_aa_ii/issues/setup_zrok_ssh.sh) to enable the `zrok2` environment with an account token, create a persistent `tcpTunnel` share, save the share token to `~/.config/zrok2-ssh.env`, and enable/start `zrok2-ssh.service`.
   - Installed `~/.local/bin/get-zrok-ssh` to display the active tunnel state, share token, and client connection commands.

## Proposed Solution / Action Items
- [x] Download and SHA-256 verify `zrok_2.0.11_linux_amd64.tar.gz`.
- [x] Install `zrok2` binary and `zrok` symlink to `~/.local/bin/`.
- [x] Export `~/.local/bin` in `~/.bash_profile`, `~/.bashrc`, and `~/.zshrc`.
- [x] Create and enable boot-persistent systemd user units (`zrok2-ssh.service`, `zrok2-ssh-auto.path`) and `~/.local/bin/zrok2-ssh-run`.
- [x] Create `setup_zrok_ssh.sh` and `~/.local/bin/get-zrok-ssh`.
- [x] Document Unix commands in [`unix_issues_cmds.txt`](file:///home/tthhongs/build_tthhongs/tasks_aa_ii/issues/unix_issues_cmds.txt) and update [`GEMINI.md`](file:///home/tthhongs/build_tthhongs/tasks_aa_ii/issues/GEMINI.md).
- [ ] Run `zrok2 enable <ZROK_ENABLE_TOKEN>` (or `./setup_zrok_ssh.sh <ZROK_ENABLE_TOKEN>`) using your account token from `https://myzrok.io` or `zrok2 invite` to activate the live tunnel.

## Verification
- `zrok2 version` and `zrok version` both return `v2.0.11 [d8e5316d]`.
- `bash -ic 'which zrok zrok2'` and `zsh -ic 'which zrok zrok2'` resolve to `/home/tthhongs/.local/bin/zrok` and `/home/tthhongs/.local/bin/zrok2`.
- `systemd-analyze --user verify ~/.config/systemd/user/zrok2-ssh.service ~/.config/systemd/user/zrok2-ssh-auto.path` passed with no errors.
- `systemctl --user is-enabled zrok2-ssh.service zrok2-ssh-auto.path` returned `enabled` for both units.
- `systemctl --user status zrok2-ssh-auto.path` shows `active (waiting)` ready to trigger `zrok2-ssh.service`.
- `bash -n setup_zrok_ssh.sh ~/.local/bin/get-zrok-ssh ~/.local/bin/zrok2-ssh-run` passed.
