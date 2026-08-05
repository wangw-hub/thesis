import pytest

from epoch_auth_r3.revocation.events import normalize_event


def make(name="EpochAdvanced", args=None):
    return normalize_event(
        chain_id=2026073005,
        contract_address="0x" + "12" * 20,
        event_name=name,
        event_signature=b"\x01" * 32,
        transaction_hash=b"\x02" * 32,
        log_index=3,
        block_number=9,
        block_hash=b"\x03" * 32,
        args=args or {"resourceId": b"\x04" * 32, "newEpoch": 2},
    )


def test_identity_is_chain_contract_tx_log():
    event = make()
    assert event.identity == (2026073005, "0x" + "12" * 20, "02" * 32, 3)


def test_payload_digest_is_deterministic():
    assert make(args={"newEpoch": 2, "resourceId": b"\x04" * 32}).payload_digest == make(
        args={"resourceId": b"\x04" * 32, "newEpoch": 2}
    ).payload_digest


def test_payload_change_changes_digest():
    assert make().payload_digest != make(args={"resourceId": b"\x04" * 32, "newEpoch": 3}).payload_digest


def test_unknown_event_fails_closed():
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        make("Unknown")
