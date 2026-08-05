from __future__ import annotations

from dataclasses import dataclass
import json

from epoch_auth_r3.keystore.encrypted_ck_record import (
    EncryptedCKRecordV1,
    unwrap_content_key,
    wrap_content_key,
)


@dataclass(frozen=True)
class KeyProtectionServiceV1:
    """Test/prototype software boundary; ROOT_KEK is supplied externally."""

    root_kek: bytes

    def wrap(self, ck: bytes, context: dict, *, created_at: str, test_nonce=None):
        return wrap_content_key(
            self.root_kek, ck, context, created_at=created_at, test_nonce=test_nonce
        )

    def unwrap(self, record: EncryptedCKRecordV1) -> bytes:
        return unwrap_content_key(self.root_kek, record)


class ContentKeyRepositoryV1:
    def __init__(self, connection):
        self.connection = connection

    def put(self, record: EncryptedCKRecordV1) -> bool:
        row = self.connection.execute(
            """INSERT INTO r3_control.content_key_record
               (resource_id,body_version,key_version,protection_key_version,
                nonce,ciphertext,metadata_digest,record_json)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (resource_id,body_version) DO NOTHING RETURNING 1""",
            (
                bytes.fromhex(record.resource_id),
                record.body_version,
                record.key_version,
                record.protection_key_version,
                record.nonce,
                record.ciphertext,
                bytes.fromhex(record.metadata_digest),
                record.to_json().decode("utf-8"),
            ),
        ).fetchone()
        return row is not None

    def get(self, resource_id: str, body_version: int) -> EncryptedCKRecordV1:
        row = self.connection.execute(
            """SELECT record_json FROM r3_control.content_key_record
               WHERE resource_id=%s AND body_version=%s""",
            (bytes.fromhex(resource_id.removeprefix("0x")), body_version),
        ).fetchone()
        if row is None:
            raise KeyError("CONTENT_KEY_RECORD_NOT_FOUND")
        value = row[0]
        if isinstance(value, dict):
            value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        return EncryptedCKRecordV1.from_json(value)
