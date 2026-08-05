#!/usr/bin/env bash
set -Eeuo pipefail

sudo -n true
echo "hostname=$(hostname)"
echo "service_active=$(sudo -n systemctl is-active besu.service)"
echo "service_enabled=$(sudo -n systemctl is-enabled besu.service)"
echo "genesis_sha256=$(sudo -n sha256sum /etc/besu/genesis.json | awk '{print $1}')"
echo "node_id=$(sudo -n cat /etc/besu/key.pub | tr -d '\r\n' | sed 's/^0x//')"
echo "process_user=$(ps -o user= -p "$(sudo -n systemctl show -p MainPID --value besu.service)" | xargs)"
echo "p2p_listener=$(ss -lnt | awk '$4 ~ /:30303$/ {print $4; exit}')"
echo "rpc_listener=$(ss -lnt | awk '$4 ~ /127.0.0.1.*:8545$/ {print $4; exit}')"
python3 - <<'PY'
import json
import urllib.request

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request("http://127.0.0.1:8545", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)

print("eth_blockNumber=" + json.dumps(rpc("eth_blockNumber", []), separators=(",", ":")))
print("net_peerCount=" + json.dumps(rpc("net_peerCount", []), separators=(",", ":")))
print("qbft_validators=" + json.dumps(rpc("qbft_getValidatorsByBlockNumber", ["latest"]), separators=(",", ":")))
PY
sudo -n journalctl -u besu.service -n 80 --no-pager
