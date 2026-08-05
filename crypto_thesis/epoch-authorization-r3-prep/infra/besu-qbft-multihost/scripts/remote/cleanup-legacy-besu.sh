#!/usr/bin/env bash
set -Eeuo pipefail

# This recovery script is intentionally limited to paths created by a prior Besu deployment.
readonly TARGET_PATHS=(/opt/besu /opt/besu-26.5.0 /etc/besu /var/lib/besu /var/log/besu)

sudo -n true

if pgrep -af '[b]esu' >/dev/null; then
  echo 'REFUSING_CLEANUP: a Besu process is still running.' >&2
  pgrep -af '[b]esu' >&2
  exit 20
fi

mapfile -t BESU_UNITS < <(systemctl list-unit-files --type=service --no-legend --no-pager | awk '$1 ~ /^besu/ {print $1}')
if ((${#BESU_UNITS[@]})); then
  echo "REFUSING_CLEANUP: Besu systemd units exist: ${BESU_UNITS[*]}" >&2
  echo 'Stop and remove the named units through a separately reviewed recovery action.' >&2
  exit 21
fi

echo "cleanup_started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
for target in "${TARGET_PATHS[@]}"; do
  if [[ -e "$target" || -L "$target" ]]; then
    stat -c "before|%F|%a|%U:%G|%n" "$target"
    sudo -n rm -rf -- "$target"
    echo "removed=$target"
  else
    echo "absent=$target"
  fi
done

if id besu >/dev/null 2>&1; then
  sudo -n userdel besu
  echo 'removed_user=besu'
else
  echo 'absent_user=besu'
fi

for target in "${TARGET_PATHS[@]}"; do
  if [[ -e "$target" || -L "$target" ]]; then
    echo "CLEANUP_INVARIANT_FAILED=$target still exists" >&2
    exit 22
  fi
done
if id besu >/dev/null 2>&1; then
  echo 'CLEANUP_INVARIANT_FAILED=besu user still exists' >&2
  exit 23
fi

echo "cleanup_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

