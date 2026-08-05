#!/usr/bin/env bash
set -euo pipefail

# Run one ordinal range of the frozen Formal execution order.
# usage: run_block.sh <first> <last> <code> <attempt-root> <attempt-id> <commit>
#                     <env-digest> <accounts> <db-password> <auth> <registry> <manifest> <venv>
FIRST=$1; LAST=$2; CODE=$3; ATTEMPT_ROOT=$4; ATTEMPT_ID=$5; COMMIT=$6
ENV_DIGEST=$7; ACCOUNTS=$8; DBPASS=$9; AUTH=${10}; REGISTRY=${11}; MANIFEST=${12}; VENV=${13}

RESULTS="$ATTEMPT_ROOT/runtime/block-$FIRST-$LAST.json"
: > "$RESULTS"
for ordinal in $(seq "$FIRST" "$LAST"); do
  echo "[run_block] ordinal=$ordinal"
  OUT=$("$VENV/bin/python" "$CODE/src/epoch_auth_r3/formal/run.py" \
    --ordinal "$ordinal" \
    --order-manifest "$MANIFEST" \
    --attempt-id "$ATTEMPT_ID" \
    --attempt-root "$ATTEMPT_ROOT" \
    --commit "$COMMIT" \
    --environment-digest "$ENV_DIGEST" \
    --accounts-file "$ACCOUNTS" \
    --database-password-file "$DBPASS" \
    --auth-address "$AUTH" \
    --registry-address "$REGISTRY" \
    2>> "$ATTEMPT_ROOT/runtime/block-$FIRST-$LAST.stderr") || true
  echo "$OUT" >> "$RESULTS"
  RUNID=$(echo "$OUT" | "$VENV/bin/python" -c 'import sys,json; print(json.loads(sys.stdin.read())["runId"])' 2>/dev/null) || true
  if [ -n "$RUNID" ]; then
    rm -rf "$ATTEMPT_ROOT/local-store/$RUNID"
  fi
  echo >> "$RESULTS"
done
echo "[run_block] completed $FIRST..$LAST -> $RESULTS"
