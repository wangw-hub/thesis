#!/usr/bin/env bash
set -Eeuo pipefail

readonly STAGED_GENESIS='/tmp/besu-genesis.json'
readonly STAGED_VALIDATORS='/tmp/besu-validators.json'
if (($# != 1)); then
  echo 'usage: install-public-network-material.sh GENESIS_SHA256' >&2
  exit 2
fi
readonly EXPECTED_GENESIS="${1,,}"

sudo -n true
if [[ -e /etc/besu/genesis.json || -e /etc/besu/validators.json || -e /etc/besu/key ]]; then
  echo 'refusing to overwrite existing RPC network or key material' >&2
  exit 30
fi
[[ -f "$STAGED_GENESIS" && -f "$STAGED_VALIDATORS" ]] || { echo 'missing staged public network material' >&2; exit 31; }
actual_hash="$(sha256sum "$STAGED_GENESIS" | awk '{print $1}')"
[[ "$actual_hash" == "$EXPECTED_GENESIS" ]] || { echo 'genesis hash mismatch' >&2; exit 32; }

sudo -n install -m 0644 -o root -g besu "$STAGED_GENESIS" /etc/besu/genesis.json
sudo -n install -m 0644 -o root -g besu "$STAGED_VALIDATORS" /etc/besu/validators.json
rm -f -- "$STAGED_GENESIS" "$STAGED_VALIDATORS"

echo "hostname=$(hostname)"
echo "genesis_sha256=$(sudo -n sha256sum /etc/besu/genesis.json | awk '{print $1}')"
sudo -n stat -c '%a %U:%G %n' /etc/besu/genesis.json /etc/besu/validators.json
if sudo -n test -e /etc/besu/key; then
  echo 'validator_private_key_present=true'
  exit 33
fi
echo 'validator_private_key_present=false'
