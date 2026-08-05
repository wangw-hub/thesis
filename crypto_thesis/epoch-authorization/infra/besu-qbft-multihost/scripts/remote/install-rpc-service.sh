#!/usr/bin/env bash
set -Eeuo pipefail

readonly STAGED_CONFIG='/tmp/besu-rpc.toml'
readonly STAGED_STATIC='/tmp/static-nodes-rpc.json'
readonly STAGED_SERVICE='/tmp/besu-rpc.service'

sudo -n true
for target in /etc/besu/key /etc/besu/key.pub /etc/besu/config.toml /etc/besu/static-nodes.json /etc/systemd/system/besu-rpc.service; do
  if sudo -n test -e "$target" || sudo -n test -L "$target"; then
    echo "refusing to overwrite existing RPC material: $target" >&2
    exit 20
  fi
done
if [[ -n "$(sudo -n find /var/lib/besu -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo 'refusing to deploy over non-empty RPC data directory' >&2
  exit 21
fi
for staged in "$STAGED_CONFIG" "$STAGED_STATIC" "$STAGED_SERVICE"; do
  [[ -f "$staged" ]] || { echo "missing staged file: $staged" >&2; exit 22; }
done

sudo -n rm -f -- /tmp/besu-rpc-key /tmp/besu-rpc-key.pub
sudo -n install -d -m 0700 -o besu -g besu /tmp/besu-rpc-home
sudo -n -u besu sh -c 'umask 077; openssl rand -hex 32 > /tmp/besu-rpc-key'
sudo -n -u besu env HOME=/tmp/besu-rpc-home /opt/besu/bin/besu public-key export \
  --node-private-key-file=/tmp/besu-rpc-key \
  --to=/tmp/besu-rpc-key.pub
[[ -s /tmp/besu-rpc-key && -s /tmp/besu-rpc-key.pub ]] || { echo 'Besu did not generate RPC node material' >&2; exit 23; }
public_key="$(tr -d '\r\n' </tmp/besu-rpc-key.pub | sed 's/^0x//')"
[[ "$public_key" =~ ^[0-9a-fA-F]{128}$ ]] || { echo 'Invalid generated RPC public key' >&2; exit 24; }

sudo -n -u besu python3 - "$public_key" /etc/besu/validators.json <<'PY'
import json
import sys

public_key = sys.argv[1].lower()
with open(sys.argv[2], "r", encoding="utf-8-sig") as source:
    validators = json.load(source)
if public_key in {item["node_id"].lower() for item in validators}:
    raise SystemExit("RPC node key duplicates a Validator node ID")
PY

env HOME=/tmp /opt/besu/bin/besu --config-file="$STAGED_CONFIG" --version
python3 -m json.tool "$STAGED_STATIC" >/dev/null
sudo -n install -m 0640 -o root -g besu /tmp/besu-rpc-key /etc/besu/key
sudo -n install -m 0644 -o root -g besu /tmp/besu-rpc-key.pub /etc/besu/key.pub
sudo -n install -m 0640 -o root -g besu "$STAGED_CONFIG" /etc/besu/config.toml
sudo -n install -m 0644 -o root -g besu "$STAGED_STATIC" /etc/besu/static-nodes.json
sudo -n install -m 0644 -o root -g root "$STAGED_SERVICE" /etc/systemd/system/besu-rpc.service
sudo -n rm -f -- /tmp/besu-rpc-key /tmp/besu-rpc-key.pub "$STAGED_CONFIG" "$STAGED_STATIC" "$STAGED_SERVICE"
sudo -n rm -rf -- /tmp/besu-rpc-home
sudo -n systemctl daemon-reload
sudo -n systemctl enable besu-rpc.service
sudo -n systemctl start besu-rpc.service

echo "rpc_node_id=$public_key"
echo "rpc_private_key_sha256=$(sudo -n sha256sum /etc/besu/key | awk '{print $1}')"
echo "service_started_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
