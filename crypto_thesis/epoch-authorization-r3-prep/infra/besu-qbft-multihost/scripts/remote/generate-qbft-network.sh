#!/usr/bin/env bash
set -Eeuo pipefail

readonly CONFIG_PATH='/tmp/besu-qbftConfigFile-2026072801.json'
readonly OUTPUT_PATH='/tmp/besu-qbft-stage2-2026072801'
readonly ARCHIVE_PATH='/tmp/besu-qbft-stage2-2026072801.tar.gz'

if [[ -e "$OUTPUT_PATH" || -e "$ARCHIVE_PATH" ]]; then
  echo 'refusing to overwrite existing stage2 remote material' >&2
  exit 20
fi
if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "missing configuration: $CONFIG_PATH" >&2
  exit 21
fi

umask 077
/opt/besu/bin/besu operator generate-blockchain-config \
  --config-file="$CONFIG_PATH" \
  --to="$OUTPUT_PATH"

genesis_path="$OUTPUT_PATH/genesis.json"
if [[ ! -f "$genesis_path" ]]; then
  echo 'official generator did not produce genesis.json' >&2
  exit 22
fi
private_count="$(find "$OUTPUT_PATH" -type f -name 'key.priv' | wc -l)"
public_count="$(find "$OUTPUT_PATH" -type f -name 'key.pub' | wc -l)"
if [[ "$private_count" -ne 4 || "$public_count" -ne 4 ]]; then
  echo "unexpected key count: private=$private_count public=$public_count" >&2
  exit 23
fi

extra_data_path="$OUTPUT_PATH/extra-data.json"
python3 - "$genesis_path" "$extra_data_path" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as source:
    extra_data = json.load(source)["extraData"]
with open(sys.argv[2], "w", encoding="utf-8") as target:
    target.write(extra_data)
    target.write("\n")
PY

/opt/besu/bin/besu rlp decode \
  --from="$extra_data_path" \
  --to="$OUTPUT_PATH/decoded-validators.txt" \
  --type=QBFT_EXTRA_DATA

tar -C /tmp -czf "$ARCHIVE_PATH" "$(basename "$OUTPUT_PATH")"
echo "besu_version=$(/opt/besu/bin/besu --version | head -n 1)"
echo "genesis_sha256=$(sha256sum "$genesis_path" | awk '{print $1}')"
echo "archive_sha256=$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"
echo "private_key_count=$private_count"
echo "public_key_count=$public_count"
echo "generated_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
