#!/usr/bin/env bash
set -Eeuo pipefail

readonly CONFIG_PATH='/tmp/besu-qbftConfigFile-2026072801.json'
readonly OUTPUT_PATH='/tmp/besu-qbft-stage2-2026072801'
readonly ARCHIVE_PATH='/tmp/besu-qbft-stage2-2026072801.tar.gz'

rm -rf -- "$OUTPUT_PATH"
rm -f -- "$ARCHIVE_PATH" "$CONFIG_PATH"

for target in "$OUTPUT_PATH" "$ARCHIVE_PATH" "$CONFIG_PATH"; do
  if [[ -e "$target" || -L "$target" ]]; then
    echo "stage2 cleanup failed: $target remains" >&2
    exit 30
  fi
done
echo 'stage2_remote_staging=absent'
