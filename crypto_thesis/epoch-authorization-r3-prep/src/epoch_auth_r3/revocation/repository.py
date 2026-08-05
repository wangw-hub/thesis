from __future__ import annotations

import uuid
from psycopg.types.json import Jsonb

from .events import NormalizedAuthorizationEventV1


class ConflictingAuthorizationEvent(RuntimeError):
    pass


class AuthorizationEventRepository:
    def __init__(self, connection):
        self.connection = connection

    def insert(self, event: NormalizedAuthorizationEventV1) -> tuple[uuid.UUID, bool]:
        existing = self.connection.execute(
            """SELECT event_id,payload_digest,block_hash
               FROM r3_control.authorization_event
               WHERE chain_id=%s AND authorization_contract=%s
                 AND transaction_hash=%s AND log_index=%s""",
            (
                event.chain_id,
                bytes.fromhex(event.contract_address.removeprefix("0x")),
                bytes.fromhex(event.transaction_hash),
                event.log_index,
            ),
        ).fetchone()
        if existing:
            if bytes(existing[1]).hex() != event.payload_digest or bytes(existing[2]).hex() != event.block_hash:
                raise ConflictingAuthorizationEvent("CONFLICTING_DUPLICATE_EVENT")
            return existing[0], False
        event_id = uuid.uuid4()
        self.connection.execute(
            """INSERT INTO r3_control.authorization_event
               (event_id,chain_id,authorization_contract,event_name,event_signature,
                transaction_hash,log_index,block_number,block_hash,event_class,
                resource_id,user_id,payload,payload_digest,status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                event_id,
                event.chain_id,
                bytes.fromhex(event.contract_address.removeprefix("0x")),
                event.event_name,
                bytes.fromhex(event.event_signature),
                bytes.fromhex(event.transaction_hash),
                event.log_index,
                event.block_number,
                bytes.fromhex(event.block_hash),
                event.event_class.value,
                bytes.fromhex(event.resource_id) if event.resource_id else None,
                bytes.fromhex(event.user_id) if event.user_id else None,
                Jsonb(event.payload),
                bytes.fromhex(event.payload_digest),
                "AUDIT_ONLY" if event.event_class.value == "AUDIT_ONLY" else "OBSERVED",
            ),
        )
        return event_id, True
