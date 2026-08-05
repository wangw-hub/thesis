#!/usr/bin/env bash
set -Eeuo pipefail

if (($# != 3)); then
  echo 'usage: install-validator-material.sh GENESIS_SHA256 PRIVATE_SHA256 PUBLIC_SHA256' >&2
  exit 2
fi
readonly EXPECTED_GENESIS="${1,,}"
readonly EXPECTED_PRIVATE="${2,,}"
readonly EXPECTED_PUBLIC="${3,,}"
readonly STAGED_GENESIS='/tmp/besu-genesis.json'
readonly STAGED_PRIVATE='/tmp/besu-validator-key.priv'
readonly STAGED_PUBLIC='/tmp/besu-validator-key.pub'
readonly STAGED_VALIDATORS='/tmp/besu-validators.json'

sudo -n true
existing_count=0
for target in /etc/besu/genesis.json /etc/besu/key /etc/besu/key.pub /etc/besu/validators.json; do
  if sudo -n test -e "$target" || sudo -n test -L "$target"; then
    ((existing_count += 1))
  fi
done
if ((existing_count != 0 && existing_count != 4)); then
  echo "refusing partial existing material set: count=$existing_count" >&2
  exit 20
fi
for staged in "$STAGED_GENESIS" "$STAGED_PRIVATE" "$STAGED_PUBLIC" "$STAGED_VALIDATORS"; do
  [[ -f "$staged" ]] || { echo "missing staged file: $staged" >&2; exit 21; }
done

genesis_hash="$(sha256sum "$STAGED_GENESIS" | awk '{print $1}')"
private_hash="$(sha256sum "$STAGED_PRIVATE" | awk '{print $1}')"
public_hash="$(sha256sum "$STAGED_PUBLIC" | awk '{print $1}')"
[[ "$genesis_hash" == "$EXPECTED_GENESIS" ]] || { echo 'genesis hash mismatch' >&2; exit 22; }
[[ "$private_hash" == "$EXPECTED_PRIVATE" ]] || { echo 'private key hash mismatch' >&2; exit 23; }
[[ "$public_hash" == "$EXPECTED_PUBLIC" ]] || { echo 'public key hash mismatch' >&2; exit 24; }

if ((existing_count == 0)); then
  sudo -n install -m 0644 -o root -g besu "$STAGED_GENESIS" /etc/besu/genesis.json
  sudo -n install -m 0640 -o root -g besu "$STAGED_PRIVATE" /etc/besu/key
  sudo -n install -m 0644 -o root -g besu "$STAGED_PUBLIC" /etc/besu/key.pub
  sudo -n install -m 0644 -o root -g besu "$STAGED_VALIDATORS" /etc/besu/validators.json
else
  [[ "$(sudo -n sha256sum /etc/besu/genesis.json | awk '{print $1}')" == "$EXPECTED_GENESIS" ]] || { echo 'existing genesis mismatch' >&2; exit 25; }
  [[ "$(sudo -n sha256sum /etc/besu/key | awk '{print $1}')" == "$EXPECTED_PRIVATE" ]] || { echo 'existing private key mismatch' >&2; exit 26; }
  [[ "$(sudo -n sha256sum /etc/besu/key.pub | awk '{print $1}')" == "$EXPECTED_PUBLIC" ]] || { echo 'existing public key mismatch' >&2; exit 27; }
  echo 'existing_material_reused_after_exact_hash_verification=true'
fi
rm -f -- "$STAGED_GENESIS" "$STAGED_PRIVATE" "$STAGED_PUBLIC" "$STAGED_VALIDATORS"

echo "hostname=$(hostname)"
echo "genesis_sha256=$(sudo -n sha256sum /etc/besu/genesis.json | awk '{print $1}')"
echo "private_key_sha256=$(sudo -n sha256sum /etc/besu/key | awk '{print $1}')"
echo "public_key_sha256=$(sudo -n sha256sum /etc/besu/key.pub | awk '{print $1}')"
sudo -n stat -c '%a %U:%G %n' /etc/besu/genesis.json /etc/besu/key /etc/besu/key.pub /etc/besu/validators.json
echo "public_key=$(sudo -n cat /etc/besu/key.pub | tr -d '\r\n' | sed 's/^0x//')"
