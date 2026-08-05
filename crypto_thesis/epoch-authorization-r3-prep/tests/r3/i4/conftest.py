import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from epoch_auth_r3.database.connection import connect
from epoch_auth_r3.database.models import SyntheticRevocationEventV1
from epoch_auth_r3.database.schema import apply_migrations

TABLES = (
    "dead_letter_job","recovery_audit","commit_attempt","header_version",
    "storage_object","header_update_job","revocation_event_cursor",
)


def event(n=1, **changes):
    values = dict(
        chain_id=2026072901,
        authorization_contract=bytes([0x11])*20,
        header_registry=bytes([0x22])*20,
        event_signature=bytes([0x33])*32,
        tx_hash=n.to_bytes(32, "big"),
        log_index=n,
        block_number=100+n,
        block_hash=bytes([0x44])*31 + bytes([n % 256]),
        resource_id=n.to_bytes(32, "big"),
        new_epoch=2,
        new_state_version=3,
        new_header_version=1,
        new_key_version=1,
    )
    values.update(changes)
    return SyntheticRevocationEventV1(**values)


@pytest.fixture(scope="session", autouse=True)
def migrated():
    required = os.environ.get("R3_I4_PGPASSFILE")
    if not required:
        pytest.fail("R3_I4_PGPASSFILE external secret path is required")
    apply_migrations()


@pytest.fixture
def db(migrated):
    conn = connect()
    with conn.transaction():
        conn.execute("TRUNCATE " + ",".join("r3_control."+x for x in TABLES) + " RESTART IDENTITY CASCADE")
    yield conn
    conn.close()
