#!/usr/bin/env bash
set -Eeuo pipefail

readonly STAGED_CONFIG='/tmp/besu-validator.toml'
readonly STAGED_STATIC='/tmp/static-nodes.json'
readonly STAGED_SERVICE='/tmp/besu.service'

sudo -n true
for target in /etc/besu/config.toml /etc/besu/static-nodes.json /etc/systemd/system/besu.service; do
  if sudo -n test -e "$target" || sudo -n test -L "$target"; then
    echo "refusing to overwrite existing deployment file: $target" >&2
    exit 20
  fi
done
if [[ -n "$(sudo -n find /var/lib/besu -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo 'refusing to deploy over non-empty Besu data directory' >&2
  exit 21
fi
for staged in "$STAGED_CONFIG" "$STAGED_STATIC" "$STAGED_SERVICE"; do
  [[ -f "$staged" ]] || { echo "missing staged file: $staged" >&2; exit 22; }
done

/opt/besu/bin/besu --config-file="$STAGED_CONFIG" --version
python3 -m json.tool "$STAGED_STATIC" >/dev/null
sudo -n install -m 0640 -o root -g besu "$STAGED_CONFIG" /etc/besu/config.toml
sudo -n install -m 0644 -o root -g besu "$STAGED_STATIC" /etc/besu/static-nodes.json
sudo -n install -m 0644 -o root -g root "$STAGED_SERVICE" /etc/systemd/system/besu.service
rm -f -- "$STAGED_CONFIG" "$STAGED_STATIC" "$STAGED_SERVICE"
sudo -n systemctl daemon-reload
sudo -n systemctl enable besu.service
sudo -n systemctl start besu.service
echo "service_started_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
