#!/usr/bin/env bash
set -Eeuo pipefail

service_name="${1:?service name required}"
rpc_url="${2:?RPC URL required}"

rpc() {
  local method="$1"
  python3 - "$rpc_url" "$method" <<'PY'
import json
import sys
import urllib.request

url, method = sys.argv[1:3]
payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":[]}).encode()
request = urllib.request.Request(url, data=payload, headers={"Content-Type":"application/json"})
with urllib.request.urlopen(request, timeout=10) as response:
    print(response.read().decode())
PY
}

echo "collected_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "hostname=$(hostname)"
echo "service=$(sudo -n systemctl is-active "$service_name" 2>/dev/null || true)"
echo "block_number=$(rpc eth_blockNumber)"
echo "peer_count=$(rpc net_peerCount)"
