#!/usr/bin/env bash
set -Eeuo pipefail

sudo -n true
echo "hostname=$(hostname)"
echo "java_version=$(java -version 2>&1 | head -n 1)"
echo "besu_version=$(/opt/besu/bin/besu --version | head -n 1)"
echo "besu_target=$(readlink -f /opt/besu)"
echo "besu_user=$(id besu)"

if pgrep -af '[b]esu' >/dev/null; then
  echo 'unexpected_processes=true'
  pgrep -af '[b]esu'
else
  echo 'unexpected_processes=false'
fi

units="$(systemctl list-unit-files --type=service --no-legend --no-pager | awk '$1 ~ /^besu/ {print $1}')"
if [[ -n "$units" ]]; then
  echo 'unexpected_units=true'
  printf '%s\n' "$units"
else
  echo 'unexpected_units=false'
fi
