#!/usr/bin/env bash
set -Eeuo pipefail

service_name="${1:?service name required}"
rpc_url="${2:?RPC URL required}"
block_tag="${3:-latest}"

rpc() {
  local method="$1"
  local params="$2"
  python3 - "$rpc_url" "$method" "$params" <<'PY'
import json
import sys
import urllib.request

url, method, params = sys.argv[1:4]
payload = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": method,
    "params": json.loads(params),
}).encode("utf-8")
request = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(request, timeout=10) as response:
    print(response.read().decode("utf-8"))
PY
}

echo "collected_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "hostname=$(hostname)"
echo "service_name=$service_name"
echo "service_active=$(sudo -n systemctl is-active "$service_name")"
echo "service_enabled=$(sudo -n systemctl is-enabled "$service_name")"
echo "process_user=$(ps -o user= -C java | awk 'NF {print $1; exit}')"
echo "genesis_sha256=$(sudo -n sha256sum /etc/besu/genesis.json | awk '{print $1}')"
echo "static_nodes_sha256=$(sudo -n sha256sum /etc/besu/static-nodes.json | awk '{print $1}')"
echo "private_key_sha256=$(sudo -n sha256sum /etc/besu/key | awk '{print $1}')"
echo "node_id=$(sudo -n cat /etc/besu/key.pub | tr -d '\r\n')"
echo "p2p_listener=$(sudo -n ss -lntp | awk '$4 ~ /:30303$/ {print $4; exit}')"
echo "chain_id=$(rpc eth_chainId '[]')"
echo "block_number=$(rpc eth_blockNumber '[]')"
echo "peer_count=$(rpc net_peerCount '[]')"
echo "validators=$(rpc qbft_getValidatorsByBlockNumber '["latest"]')"
echo "block_at_tag=$(rpc eth_getBlockByNumber "[\"$block_tag\",false]")"
echo "recent_error_count=$(sudo -n journalctl -u "$service_name" --since '-5 minutes' --no-pager -p err..alert | grep -cve '^-- No entries --$' || true)"
