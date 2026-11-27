#!/usr/bin/env bash
# Automated idempotent setup for zrok2 CLI + persistent private TCP tunnel for SSH
# Targets: CachyOS / Arch Linux (user-space installation in ~/.local/bin)

set -euo pipefail

ZROK_VERSION="2.0.11"
ZROK_SHA256="4db2e2f0be382a9cdd415735520f7d0ac0715b799d54c922d7801cc35803dd8c"
ZROK_URL="https://github.com/openziti/zrok/releases/download/v${ZROK_VERSION}/zrok_${ZROK_VERSION}_linux_amd64.tar.gz"
ZROK_BIN="$HOME/.local/bin/zrok2"
ENV_FILE="$HOME/.config/zrok2-ssh.env"

ENABLE_TOKEN=""
CUSTOM_SHARE_TOKEN=""

usage() {
    cat <<USAGE
Usage: $0 [OPTIONS] [ENABLE_TOKEN]

Options:
  -t, --token <TOKEN>         zrok2 account enable token (from https://myzrok.io or 'zrok2 invite')
  -s, --share-token <NAME>    Optional custom share token name for the private tcpTunnel share
  -h, --help                  Show this help message

Examples:
  $0 <YOUR_ENABLE_TOKEN>
  $0 --token <YOUR_ENABLE_TOKEN> --share-token aspire79gssh
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--token)
            ENABLE_TOKEN="${2:-}"
            shift 2
            ;;
        -s|--share-token)
            CUSTOM_SHARE_TOKEN="${2:-}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "[-] Unknown option: $1" >&2
            usage
            exit 1
            ;;
        *)
            if [ -z "$ENABLE_TOKEN" ]; then
                ENABLE_TOKEN="$1"
            else
                echo "[-] Unexpected argument: $1" >&2
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

echo "================================================================================"
echo "[*] zrok2 Remote SSH Tunnel Setup (v${ZROK_VERSION})"
echo "================================================================================"

# 1. Ensure zrok2 binary is installed and verified
if [ ! -x "$ZROK_BIN" ]; then
    echo "[*] Downloading zrok2 v${ZROK_VERSION}..."
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    curl -fsSL -o "$TMP_DIR/zrok.tar.gz" "$ZROK_URL"
    echo "${ZROK_SHA256}  ${TMP_DIR}/zrok.tar.gz" | sha256sum -c -
    tar -xzf "$TMP_DIR/zrok.tar.gz" -C "$TMP_DIR"
    install -Dm0755 "$TMP_DIR/zrok2" "$ZROK_BIN"
    ln -sf "$ZROK_BIN" "$HOME/.local/bin/zrok"
    echo "[+] Installed $ZROK_BIN and symlink $HOME/.local/bin/zrok"
else
    echo "[+] Found zrok2 binary: $("$ZROK_BIN" version | tail -n1)"
fi

# 2. Verify local OpenSSH server is running
if systemctl is-active --quiet sshd.service; then
    echo "[+] sshd.service is active (listening on port 22)."
else
    echo "[!] Warning: sshd.service is not active. Start it with: sudo systemctl enable --now sshd.service"
fi

# 3. Enable zrok2 environment if not already enabled
if [ ! -f "$HOME/.zrok2/environment.json" ]; then
    if [ -z "$ENABLE_TOKEN" ] && [ -t 0 ]; then
        echo ""
        echo "No active zrok2 environment found (~/.zrok2/environment.json)."
        echo "Get your account enable token from https://myzrok.io (or run 'zrok2 invite')."
        read -r -p "Enter your zrok2 enable token: " ENABLE_TOKEN
    fi
    if [ -z "$ENABLE_TOKEN" ]; then
        echo "[-] Cannot enable zrok2 without an account token." >&2
        echo "    Run: $0 <YOUR_ENABLE_TOKEN>" >&2
        exit 1
    fi
    echo "[*] Enabling zrok2 environment..."
    "$ZROK_BIN" enable --headless "$ENABLE_TOKEN"
    echo "[+] zrok2 environment enabled."
else
    echo "[+] zrok2 environment is already enabled."
fi

# 4. Create or reuse persistent private tcpTunnel share
mkdir -p "$HOME/.config"
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
fi

if [ -z "${ZROK_SSH_SHARE_TOKEN:-}" ]; then
    echo "[*] Creating persistent private tcpTunnel share..."
    if [ -n "$CUSTOM_SHARE_TOKEN" ]; then
        SHARE_OUT=$("$ZROK_BIN" create share --backend-mode tcpTunnel --share-token "$CUSTOM_SHARE_TOKEN" 2>&1)
        ZROK_SSH_SHARE_TOKEN="$CUSTOM_SHARE_TOKEN"
    else
        BEFORE_TOKENS=$("$ZROK_BIN" list shares --json 2>/dev/null | jq -r '.[].shareToken // empty' | sort -u || true)
        SHARE_OUT=$("$ZROK_BIN" create share --backend-mode tcpTunnel 2>&1)
        AFTER_TOKENS=$("$ZROK_BIN" list shares --json 2>/dev/null | jq -r '.[] | select(.shareMode=="private" and .backendMode=="tcpTunnel") | .shareToken // empty' | sort -u || true)
        ZROK_SSH_SHARE_TOKEN=$(comm -13 <(printf '%s\n' "$BEFORE_TOKENS") <(printf '%s\n' "$AFTER_TOKENS") | head -n1 || true)
        if [ -z "$ZROK_SSH_SHARE_TOKEN" ]; then
            ZROK_SSH_SHARE_TOKEN=$(printf '%s\n' "$SHARE_OUT" | grep -oE '[a-z0-9]{12}' | head -n1 || true)
        fi
    fi

    if [ -z "${ZROK_SSH_SHARE_TOKEN:-}" ]; then
        echo "[-] Failed to determine share token from zrok2 output:" >&2
        echo "$SHARE_OUT" >&2
        exit 1
    fi

    printf 'ZROK_SSH_SHARE_TOKEN=%s\n' "$ZROK_SSH_SHARE_TOKEN" > "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo "[+] Saved share token '$ZROK_SSH_SHARE_TOKEN' to $ENV_FILE"
else
    echo "[+] Reusing existing share token '$ZROK_SSH_SHARE_TOKEN' from $ENV_FILE"
fi

# 5. Enable lingering and start persistent systemd user service
loginctl enable-linger "$USER" 2>/dev/null || true
systemctl --user daemon-reload
systemctl --user enable --now zrok2-ssh.service
sleep 2
systemctl --user status zrok2-ssh.service --no-pager || true

echo ""
"$HOME/.local/bin/get-zrok-ssh"
