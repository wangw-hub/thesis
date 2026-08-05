import hashlib
from .models import SyntheticRevocationEventV1

DOMAIN = b"EPOCH_AUTH_R3_HEADER_UPDATE_OPERATION_V1"


def _field(value: bytes) -> bytes:
    return len(value).to_bytes(4, "big") + value


def operation_id_v1(event: SyntheticRevocationEventV1) -> bytes:
    encoded = b"".join((
        _field(DOMAIN),
        event.chain_id.to_bytes(8, "big"),
        event.authorization_contract,
        event.header_registry,
        event.event_signature,
        event.tx_hash,
        event.log_index.to_bytes(4, "big"),
        event.resource_id,
        event.new_epoch.to_bytes(8, "big"),
        event.new_state_version.to_bytes(8, "big"),
        event.new_key_version.to_bytes(8, "big"),
    ))
    return hashlib.sha256(encoded).digest()
