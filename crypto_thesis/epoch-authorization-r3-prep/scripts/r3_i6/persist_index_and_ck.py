"""Persist complete test recipient index and encrypted CK record in r3_i4."""
import hashlib
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.revocation.key_repository import ContentKeyRepositoryV1, KeyProtectionServiceV1

CHAIN_ID = 2026073005
AUTH = "0x12BA996711Db58897A525b5a718225bD085A3c5f"
REGISTRY = "0x280b757a16525AdAef8ED88EE158e0c6F924B35F"
RESOURCE = hashlib.sha256(b"R3-I5-RESOURCE-V1" + bytes.fromhex(AUTH[2:])).digest()


def d(label): return hashlib.sha256(b"I6:" + label).digest()


def main():
    root = Path(os.environ["R3_I6_ROOT_KEK_FILE"]).read_bytes()
    conn = connect()
    try:
        header_digest = conn.execute(
            """select header_digest from r3_control.header_version
               where resource_id=%s and status='COMMITTED'""", (RESOURCE,)
        ).fetchone()[0]
        with conn.transaction():
            for user, key, active in (
                (d(b"USER-A"), d(b"USER-A-KEY"), False),
                (d(b"USER-B"), d(b"USER-B-KEY"), True),
            ):
                conn.execute(
                    """insert into r3_control.resource_recipient_index
                       (resource_id,user_id,recipient_key_id,user_version,active,source_header_digest)
                       values (%s,%s,%s,%s,%s,%s)
                       on conflict(resource_id,user_id) do update set
                        recipient_key_id=excluded.recipient_key_id,user_version=excluded.user_version,
                        active=excluded.active,source_header_digest=excluded.source_header_digest""",
                    (RESOURCE, user, key, 2 if not active else 1, active, header_digest),
                )
            conn.execute(
                """insert into r3_control.resource_recipient_index_state
                   (resource_id,completeness,source_header_digest)
                   values (%s,'COMPLETE',%s)
                   on conflict(resource_id) do update set completeness='COMPLETE',
                   source_header_digest=excluded.source_header_digest""",
                (RESOURCE, header_digest),
            )
        record = KeyProtectionServiceV1(root).wrap(
            d(b"NEW-CK"),
            {
                "chainId": CHAIN_ID, "authorizationContract": AUTH,
                "headerRegistry": REGISTRY, "resourceId": RESOURCE.hex(),
                "bodyVersion": 3, "keyVersion": 3, "protectionKeyVersion": 1,
            },
            created_at="2026-07-30T00:00:00Z",
        )
        with conn.transaction():
            ContentKeyRepositoryV1(conn).put(record)
        row = conn.execute(
            """select count(*),count(*) filter(where active) from
               r3_control.resource_recipient_index where resource_id=%s""",
            (RESOURCE,),
        ).fetchone()
        conn.commit()
        print(f"index={row[0]} active={row[1]} encrypted_ck=1")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
