#!/usr/bin/env bash
set -euo pipefail

readonly BESU=/opt/besu-26.5.0/bin/besu
readonly CONFIG_ROOT=/etc/epoch-auth-r3/i5-besu
readonly DATA_ROOT=/var/lib/epoch-auth-r3/i5-besu
readonly UNIT=epoch-auth-r3-i5-besu.service

test -x "$BESU"
for target in "$CONFIG_ROOT" "$DATA_ROOT" "/etc/systemd/system/$UNIT"; do
  if sudo test -e "$target"; then
    echo "Refusing to overwrite existing I5 target: $target" >&2
    exit 20
  fi
done
for port in 18545 31305; do
  if sudo ss -lnt "sport = :$port" | grep -q LISTEN; then
    echo "Refusing to use occupied TCP port: $port" >&2
    exit 21
  fi
done

sudo install -d -o thesis -g thesis -m 0700 "$DATA_ROOT"
sudo install -d -o thesis -g thesis -m 0700 "$CONFIG_ROOT"
sudo install -d -o thesis -g thesis -m 0700 "$CONFIG_ROOT/node"
sudo install -m 0600 -o thesis -g thesis /tmp/r3-i5-genesis-input.json "$CONFIG_ROOT/genesis-input.json"
sudo "$BESU" operator generate-blockchain-config --config-file="$CONFIG_ROOT/genesis-input.json" --to="$DATA_ROOT/generated" >/dev/null

genesis=$(sudo find "$DATA_ROOT/generated" -type f -name genesis.json -print -quit)
node_key=$(sudo find "$DATA_ROOT/generated" -type f -name key.priv -print -quit)
test -n "$genesis"
test -n "$node_key"
sudo install -m 0644 -o thesis -g thesis "$genesis" "$CONFIG_ROOT/genesis.json"
sudo install -m 0600 -o thesis -g thesis "$node_key" "$CONFIG_ROOT/node/key.priv"
sudo install -m 0644 -o root -g root /tmp/r3-i5-besu.toml "$CONFIG_ROOT/besu.toml"
sudo install -m 0644 -o root -g root /tmp/epoch-auth-r3-i5-besu.service "/etc/systemd/system/$UNIT"
sudo systemctl daemon-reload
sudo systemctl start "$UNIT"
sudo systemctl is-active --quiet "$UNIT"
sudo ss -lntp "sport = :18545" | grep -q '127.0.0.1:18545'
sudo ss -lntp "sport = :31305" | grep -q '127.0.0.1:31305'
sudo sha256sum "$CONFIG_ROOT/genesis.json" | awk '{print $1}'
