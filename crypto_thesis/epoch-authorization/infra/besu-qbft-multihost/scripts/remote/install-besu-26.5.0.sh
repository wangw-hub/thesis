#!/usr/bin/env bash
set -Eeuo pipefail

if (($# != 1)); then
  echo 'usage: install-besu-26.5.0.sh EXPECTED_SHA256' >&2
  exit 2
fi

readonly EXPECTED_SHA256="${1,,}"
readonly PACKAGE_PATH='/tmp/besu-26.5.0.zip'
readonly VERSION_PATH='/opt/besu-26.5.0'
readonly CURRENT_PATH='/opt/besu'

sudo -n true

if [[ ! -f "$PACKAGE_PATH" ]]; then
  echo "package missing: $PACKAGE_PATH" >&2
  exit 10
fi

actual_sha256="$(sha256sum "$PACKAGE_PATH" | awk '{print $1}')"
echo "package_sha256=$actual_sha256"
if [[ "$actual_sha256" != "$EXPECTED_SHA256" ]]; then
  echo "package hash mismatch: expected=$EXPECTED_SHA256 actual=$actual_sha256" >&2
  exit 11
fi

for target in "$VERSION_PATH" "$CURRENT_PATH" /etc/besu /var/lib/besu /var/log/besu; do
  if [[ -e "$target" || -L "$target" ]]; then
    echo "refusing to overwrite existing target: $target" >&2
    exit 12
  fi
done
if id besu >/dev/null 2>&1; then
  echo 'refusing to reuse existing besu user' >&2
  exit 13
fi
if pgrep -af '[b]esu' >/dev/null; then
  echo 'refusing installation while a Besu process is running' >&2
  pgrep -af '[b]esu' >&2
  exit 14
fi
if systemctl list-unit-files --type=service --no-legend --no-pager | awk '$1 ~ /^besu/ {found=1} END {exit !found}'; then
  echo 'refusing installation while a Besu systemd unit exists' >&2
  exit 15
fi

temporary_dir="$(mktemp -d)"
trap 'rm -rf -- "$temporary_dir"' EXIT
unzip -q "$PACKAGE_PATH" -d "$temporary_dir"
source_dir="$temporary_dir/besu-26.5.0"
if [[ ! -x "$source_dir/bin/besu" ]]; then
  echo 'archive does not contain the expected Besu launcher' >&2
  exit 16
fi

sudo -n useradd --system --user-group --home-dir /var/lib/besu --shell /usr/sbin/nologin besu
sudo -n install -d -m 0755 -o root -g root "$VERSION_PATH"
sudo -n cp -a "$source_dir/." "$VERSION_PATH/"
sudo -n chown -R root:root "$VERSION_PATH"
sudo -n ln -s "$VERSION_PATH" "$CURRENT_PATH"
sudo -n install -d -m 0750 -o root -g besu /etc/besu
sudo -n install -d -m 0750 -o besu -g besu /var/lib/besu /var/log/besu
sudo -n rm -f -- "$PACKAGE_PATH"

echo "installed_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
java -version 2>&1
"$CURRENT_PATH/bin/besu" --version
readlink -f "$CURRENT_PATH"
id besu
stat -c '%a %U:%G %n' "$VERSION_PATH" /etc/besu /var/lib/besu /var/log/besu
if pgrep -af '[b]esu' >/dev/null; then
  echo 'acceptance failure: unexpected Besu process' >&2
  exit 17
fi
if systemctl list-unit-files --type=service --no-legend --no-pager | awk '$1 ~ /^besu/ {print; found=1} END {exit !found}'; then
  echo 'acceptance failure: unexpected Besu systemd unit' >&2
  exit 18
fi
echo 'besu_processes=none'
echo 'besu_units=none'

