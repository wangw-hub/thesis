#!/usr/bin/env bash
set -euo pipefail

# I11 formal minimum environment provisioning on experiment-client.
# Creates ONLY the minimum independent Formal assets required by E1-E5:
#   - PostgreSQL cluster 16/formal_r3 on 127.0.0.1:55433 (db/role/schema r3_formal)
#   - Kubo repo /var/lib/epoch-auth-r3/formal/kubo/repo (API 15998, no peers)
#   - Besu single-node QBFT chain (chainId 2026080201, RPC 18546, P2P 31306)
#   - runtime secrets (0700/0600, never in Git)
# Never touches r3_i5 Pilot, RC2 formal chain, PostgreSQL 16/main or 16/r3_i4.

ROOT=/var/lib/epoch-auth-r3/formal
CODE_DIR="$1"
FORMAL_CHAIN_ID=2026080201
PY="$ROOT/venv/bin/python"

echo "[provision] root=$ROOT code=$CODE_DIR"
sudo -n mkdir -p "$ROOT"/{attempts,local-store,kubo,besu,runtime-secrets,code,contracts}
sudo -n chown -R thesis:thesis "$ROOT"
chmod 0700 "$ROOT/runtime-secrets"

# ---------- runtime secrets (fresh, non-Git) ----------
if [ ! -f "$ROOT/runtime-secrets/database-password.txt" ]; then
  openssl rand -hex 24 > "$ROOT/runtime-secrets/database-password.txt"
  chmod 0600 "$ROOT/runtime-secrets/database-password.txt"
fi
if [ ! -f "$ROOT/runtime-secrets/accounts.json" ]; then
  "$PY" "$CODE_DIR/scripts/r3_i11/gen_formal_accounts.py" \
    > "$ROOT/runtime-secrets/accounts.json"
  chmod 0600 "$ROOT/runtime-secrets/accounts.json"
fi

# ---------- PostgreSQL cluster 16/formal_r3 (port 55433) ----------
if ! pg_lsclusters | grep -q "16[[:space:]]*formal_r3"; then
  sudo -n pg_createcluster 16 formal_r3 --port 55433 --start
fi
DBPASS=$(cat "$ROOT/runtime-secrets/database-password.txt")
sudo -n -u postgres psql -p 55433 -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='epoch_auth_r3_formal') THEN
    CREATE ROLE epoch_auth_r3_formal LOGIN PASSWORD '$DBPASS';
  END IF;
END \$\$;
SQL
if ! sudo -n -u postgres psql -p 55433 -tAc "SELECT 1 FROM pg_database WHERE datname='epoch_auth_r3_formal'" | grep -q 1; then
  sudo -n -u postgres createdb -p 55433 -O epoch_auth_r3_formal epoch_auth_r3_formal
fi
PGPASSWORD="$DBPASS" psql -h 127.0.0.1 -p 55433 -U epoch_auth_r3_formal \
  -d epoch_auth_r3_formal -v ON_ERROR_STOP=1 \
  -f "$CODE_DIR/migrations/r3_formal/0001_formal_schema.sql"
echo "[provision] PostgreSQL 16/formal_r3 ready (port 55433)"

# ---------- Kubo (independent IPFS_PATH, API 15998, no bootstrap/peers) ----------
KUBO_BIN=/opt/epoch-auth-r3/i8-kubo/bin/ipfs
IPFS_PATH="$ROOT/kubo/repo"
export IPFS_PATH
if [ ! -f "$IPFS_PATH/config" ]; then
  mkdir -p "$ROOT/kubo"
  "$KUBO_BIN" init --profile=server --empty-repo=true
fi
mkdir -p "$ROOT/kubo/home"
"$KUBO_BIN" config Addresses.API --json '"/ip4/127.0.0.1/tcp/15998"'
"$KUBO_BIN" config Addresses.Gateway --json '"/ip4/127.0.0.1/tcp/15999"'
"$KUBO_BIN" config Addresses.Swarm --json '[]'
"$KUBO_BIN" config Bootstrap --json '[]'
"$KUBO_BIN" config Discovery.MDNS.Enabled --json 'false'
"$KUBO_BIN" config AutoTLS.Enabled --json 'false'
sudo -n tee /etc/systemd/system/epoch-auth-r3-formal-kubo.service >/dev/null <<UNIT
[Unit]
Description=Epoch Authorization R3 Formal isolated Kubo
After=network.target
[Service]
Type=simple
User=thesis
Group=thesis
Environment=IPFS_PATH=$IPFS_PATH
Environment=HOME=$ROOT/kubo/home
ExecStart=$KUBO_BIN daemon --routing=none --enable-gc=false
Restart=on-failure
RestartSec=2s
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$ROOT/kubo
CapabilityBoundingSet=
AmbientCapabilities=
[Install]
WantedBy=multi-user.target
UNIT
sudo -n systemctl daemon-reload
sudo -n systemctl enable --now epoch-auth-r3-formal-kubo.service
for i in $(seq 1 30); do
  if curl -s -X POST "http://127.0.0.1:15998/api/v0/id" | grep -q ID; then break; fi
  sleep 1
done
echo "[provision] Formal Kubo ready (IPFS_PATH=$IPFS_PATH, API 15998)"

# ---------- Besu single-node QBFT formal chain (Besu operator generator) ----------
rm -rf "$ROOT/besu/generated-input" "$ROOT/besu/generated"
mkdir -p "$ROOT/besu/generated-input" "$ROOT/besu/generated"
"$PY" "$CODE_DIR/scripts/r3_i11/gen_formal_genesis.py" \
  --chain-id "$FORMAL_CHAIN_ID" \
  --accounts "$ROOT/runtime-secrets/accounts.json" \
  --out "$ROOT/besu/generated-input/genesis-input.json"
sudo -n rm -rf "$ROOT/besu/data"
/opt/besu-26.5.0/bin/besu operator generate-blockchain-config \
  --config-file="$ROOT/besu/generated-input/genesis-input.json" \
  --to="$ROOT/besu/generated" >/dev/null
GENESIS=$(find "$ROOT/besu/generated" -type f -name genesis.json -print -quit)
NODE_KEY=$(find "$ROOT/besu/generated" -type f -name key.priv -print -quit)
test -n "$GENESIS"
test -n "$NODE_KEY"
sudo -n mkdir -p /etc/epoch-auth-r3/formal-besu/node
sudo -n cp "$GENESIS" /etc/epoch-auth-r3/formal-besu/genesis.json
sudo -n cp "$NODE_KEY" /etc/epoch-auth-r3/formal-besu/node/key.priv
sudo -n chown thesis:thesis /etc/epoch-auth-r3/formal-besu/node/key.priv
sudo -n chmod 0600 /etc/epoch-auth-r3/formal-besu/node/key.priv
sudo -n chmod 0600 /etc/epoch-auth-r3/formal-besu/node/key.priv
sudo -n tee /etc/epoch-auth-r3/formal-besu/besu.toml >/dev/null <<TOML
data-path="$ROOT/besu/data"
genesis-file="/etc/epoch-auth-r3/formal-besu/genesis.json"
node-private-key-file="/etc/epoch-auth-r3/formal-besu/node/key.priv"
p2p-host="127.0.0.1"
p2p-interface="127.0.0.1"
p2p-port=31306
network-id=$FORMAL_CHAIN_ID
discovery-enabled=false
rpc-http-enabled=true
rpc-http-host="127.0.0.1"
rpc-http-port=18546
rpc-http-api=["ETH","NET","WEB3","QBFT","TXPOOL"]
host-allowlist=["localhost","127.0.0.1"]
rpc-ws-enabled=false
graphql-http-enabled=false
metrics-enabled=false
min-gas-price=0
sync-min-peers=0
TOML
sudo -n tee /etc/systemd/system/epoch-auth-r3-formal-besu.service >/dev/null <<UNIT
[Unit]
Description=Epoch Authorization R3 Formal isolated QBFT chain
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
User=thesis
Group=thesis
ExecStart=/opt/besu-26.5.0/bin/besu --config-file=/etc/epoch-auth-r3/formal-besu/besu.toml
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ReadWritePaths=$ROOT/besu
[Install]
WantedBy=multi-user.target
UNIT
sudo -n systemctl daemon-reload
sudo -n systemctl enable --now epoch-auth-r3-formal-besu.service
for i in $(seq 1 90); do
  if curl -s -X POST -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
      http://127.0.0.1:18546 | grep -q result; then break; fi
  sleep 1
done
echo "[provision] Formal Besu ready (chainId=$FORMAL_CHAIN_ID, RPC 18546)"

# ---------- deploy contracts (idempotent: only when absent) ----------
if [ ! -f "$ROOT/contracts/formal-contracts.json" ]; then
  "$PY" "$CODE_DIR/scripts/r3_i11/deploy_formal_contracts.py" \
    --rpc http://127.0.0.1:18546 \
    --chain-id "$FORMAL_CHAIN_ID" \
    --accounts "$ROOT/runtime-secrets/accounts.json" \
    --code "$CODE_DIR" \
    --out "$ROOT/contracts/formal-contracts.json"
  echo "[provision] formal-contracts.json written"
  cat "$ROOT/contracts/formal-contracts.json"
else
  echo "[provision] contracts already deployed; skipping"
fi
