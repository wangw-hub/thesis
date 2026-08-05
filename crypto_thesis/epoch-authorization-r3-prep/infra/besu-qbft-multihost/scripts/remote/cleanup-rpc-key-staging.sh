#!/usr/bin/env bash
set -Eeuo pipefail

sudo -n true
if sudo -n test -d /var/lib/besu/.cache; then
  unexpected="$(sudo -n find /var/lib/besu/.cache -mindepth 1 -maxdepth 3 ! -type d -print -quit)"
  if [[ -n "$unexpected" ]]; then
    echo "refusing to remove non-directory cache content: $unexpected" >&2
    exit 40
  fi
  sudo -n rm -rf -- /var/lib/besu/.cache
fi
sudo -n rm -f -- /tmp/besu-rpc-key /tmp/besu-rpc-key.pub
sudo -n rm -rf -- /tmp/besu-rpc-home
echo 'rpc_key_staging_cleanup=complete'
if [[ -n "$(sudo -n find /var/lib/besu -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo 'RPC data directory is still non-empty after cleanup' >&2
  exit 41
fi
