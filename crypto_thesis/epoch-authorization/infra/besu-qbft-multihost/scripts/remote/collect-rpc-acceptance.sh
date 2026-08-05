#!/usr/bin/env bash
set -Eeuo pipefail

sudo -n true
echo "hostname=$(hostname)"
echo "service_active=$(sudo -n systemctl is-active besu-rpc.service)"
echo "service_enabled=$(sudo -n systemctl is-enabled besu-rpc.service)"
echo "genesis_sha256=$(sudo -n sha256sum /etc/besu/genesis.json | awk '{print $1}')"
echo "node_id=$(sudo -n cat /etc/besu/key.pub | tr -d '\r\n' | sed 's/^0x//')"
echo "process_user=$(ps -o user= -p "$(sudo -n systemctl show -p MainPID --value besu-rpc.service)" | xargs)"
echo "p2p_listener=$(ss -lnt | awk '$4 ~ /:30303$/ {print $4; exit}')"
echo "rpc_listener=$(ss -lnt | awk '$4 ~ /192.168.6.133.*:8545$/ {print $4; exit}')"
python3 - <<'PY'
import json
import urllib.request

URL = "http://192.168.6.133:8545"
for method, params in [
    ("web3_clientVersion", []),
    ("eth_chainId", []),
    ("eth_blockNumber", []),
    ("net_peerCount", []),
    ("qbft_getValidatorsByBlockNumber", ["latest"]),
]:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        print(method + "=" + json.dumps(json.load(response), separators=(",", ":")))
PY
sudo -n journalctl -u besu-rpc.service -n 100 --no-pager
