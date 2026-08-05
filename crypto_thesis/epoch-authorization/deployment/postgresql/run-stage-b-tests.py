from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import uuid

import psycopg


def connect() -> psycopg.Connection:
    password = open("/etc/epoch-auth/postgres-password", encoding="ascii").read()
    return psycopg.connect(
        host="127.0.0.1",
        dbname="epoch_auth",
        user="epoch_auth",
        password=password,
        connect_timeout=3,
    )


def consume(key: tuple[int, bytes, str, int, bytes], verifier: str) -> bool:
    with connect() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO consumed_nonces
              (chain_id, contract_address, resource_id, epoch, nonce, verifier_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING RETURNING 1
            """,
            (*key, verifier),
        )
        return cursor.fetchone() is not None


def reserve(sender: str, pending: int) -> int:
    rid = str(uuid.uuid4())
    with connect() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO ethereum_nonce_state(chain_id, sender, next_nonce)
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
            """,
            (2026072801, sender, pending),
        )
        cursor.execute(
            """
            SELECT next_nonce FROM ethereum_nonce_state
            WHERE chain_id=%s AND sender=%s FOR UPDATE
            """,
            (2026072801, sender),
        )
        nonce = max(int(cursor.fetchone()[0]), pending)
        cursor.execute(
            """
            UPDATE ethereum_nonce_state SET next_nonce=%s
            WHERE chain_id=%s AND sender=%s
            """,
            (nonce + 1, 2026072801, sender),
        )
        cursor.execute(
            """
            INSERT INTO ethereum_nonce_reservations
              (chain_id, sender, nonce, reservation_id, status)
            VALUES (%s, %s, %s, %s, 'RESERVED')
            """,
            (2026072801, sender, nonce, rid),
        )
    return nonce


def main() -> int:
    result: dict[str, object] = {"shared_nonce": [], "transaction_nonce": []}
    contract = bytes.fromhex("11" * 20)
    for concurrency in (50, 100, 500):
        key = (2026072801, contract, f"resource-{concurrency}", 7, os.urandom(16))
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(concurrency, 100)) as pool:
            accepted = sum(pool.map(lambda i: consume(key, f"verifier-{i % 2 + 1}"), range(concurrency)))
        with connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """SELECT count(*) FROM consumed_nonces
                   WHERE chain_id=%s AND contract_address=%s AND resource_id=%s
                     AND epoch=%s AND nonce=%s""",
                key,
            )
            rows = int(cursor.fetchone()[0])
        result["shared_nonce"].append(
            {"concurrency": concurrency, "accepted": accepted, "rejected": concurrency - accepted, "rows": rows}
        )
        if accepted != 1 or rows != 1:
            raise RuntimeError("shared nonce atomicity failed")

    sender = "0x" + hashlib.sha256(b"stage-b-sender").hexdigest()[:40]
    for concurrency in (20, 50):
        unique_sender = sender[:-2] + f"{concurrency:02x}"
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            nonces = list(pool.map(lambda _: reserve(unique_sender, 0), range(concurrency)))
        unique = len(set(nonces))
        result["transaction_nonce"].append(
            {"concurrency": concurrency, "unique": unique, "minimum": min(nonces), "maximum": max(nonces)}
        )
        if unique != concurrency:
            raise RuntimeError("transaction nonce uniqueness failed")

    with connect() as conn, conn.cursor() as cursor:
        reconcile_sender = sender[:-2] + "ff"
        cursor.execute(
            """
            INSERT INTO ethereum_nonce_state(chain_id, sender, next_nonce)
            VALUES (%s, %s, 75)
            ON CONFLICT (chain_id, sender) DO UPDATE SET next_nonce=75
            """,
            (2026072801, reconcile_sender),
        )
    reconciled_nonce = reserve(reconcile_sender, 50)
    result["reconcile"] = {
        "database_next_nonce": 75,
        "rpc_pending_nonce": 50,
        "reserved_nonce": reconciled_nonce,
        "unknown_broadcast_nonce_reused": reconciled_nonce < 75,
    }
    if reconciled_nonce != 75:
        raise RuntimeError("transaction nonce reconciliation failed")

    with connect() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM consumed_nonces")
        result["persisted_nonce_rows"] = int(cursor.fetchone()[0])
    json.dump(result, sys.stdout, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
