#!/usr/bin/env bash
set -Eeuo pipefail

# FUNDING_REVIEW_ONLY=true. This probe creates no formal-chain files.
ROOT="${1:?isolated runtime root required}"
CHAIN_ID="${2:?isolated chain id required}"
BENEFICIARY="${3:?public test beneficiary address required}"
BESU=/opt/besu/bin/besu
mkdir -p "$ROOT"/{configs,generated,logs,evidence}
cat >"$ROOT/configs/base.json" <<JSON
{"genesis":{"config":{"chainId":$CHAIN_ID,"berlinBlock":0,"londonBlock":0,"qbft":{"blockperiodseconds":2,"epochlength":30000,"requesttimeoutseconds":4}},"nonce":"0x0","timestamp":"0x0","gasLimit":"0x1fffffffffffff","difficulty":"0x1","mixHash":"0x63746963616c2062797a616e74696e65206661756c7420726576696577","coinbase":"0x0000000000000000000000000000000000000000","alloc":{}},"blockchain":{"nodes":{"generate":true,"count":4}}}
JSON
"$BESU" operator generate-blockchain-config --config-file="$ROOT/configs/base.json" --to="$ROOT/generated" >"$ROOT/logs/generate.log" 2>&1
cp "$ROOT/generated/genesis.json" "$ROOT/configs/genesis-v1.json"
python3 - "$ROOT/configs/genesis-v1.json" "$ROOT/configs/genesis-transition.json" "$BENEFICIARY" <<'PY'
import json, sys
source, target, beneficiary = sys.argv[1:]
obj=json.load(open(source, encoding='utf-8'))
obj['config']['transitions']=[
  {'block': 10, 'qbft': {'blockreward':'0x64','miningbeneficiary':beneficiary}},
  {'block': 12, 'qbft': {'blockreward':'0x0','miningbeneficiary':beneficiary}}
]
json.dump(obj, open(target,'w',encoding='utf-8'), indent=2)
PY
set +e
timeout 20 "$BESU" --data-path="$ROOT/data-transition" --genesis-file="$ROOT/configs/genesis-transition.json" --node-private-key-file="$(find "$ROOT/generated" -name key.priv | head -n 1)" --p2p-host=127.0.0.1 --p2p-port=41991 >"$ROOT/logs/transition-start.log" 2>&1
code=$?
set -e
sha256sum "$ROOT/configs/genesis-v1.json" "$ROOT/configs/genesis-transition.json" >"$ROOT/evidence/config-sha256.txt"
python3 - "$ROOT" "$code" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1]); code=int(sys.argv[2]); log=root.joinpath('logs/transition-start.log').read_text(errors='replace')
result={'FUNDING_REVIEW_ONLY':True,'transition_probe_exit_code':code,'transition_contains_blockreward':True,'accepted':code in (124,0),'log_mentions_error': any(x in log.lower() for x in ('error','invalid','unknown','unsupported'))}
root.joinpath('evidence/transition-probe.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
PY
