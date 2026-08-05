import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CLOSURE = json.loads(
    (ROOT / "experiments/r3/i6-revocation-agent/raw/revocation-closure.json").read_text()
)
SCAN = json.loads(
    (ROOT / "experiments/r3/i6-revocation-agent/raw/event-scan.json").read_text()
)
SCAN2 = json.loads(
    (ROOT / "experiments/r3/i6-revocation-agent/raw/event-scan-idempotent.json").read_text()
)
DB = json.loads(
    (ROOT / "experiments/r3/i6-revocation-agent/raw/database-chain-closure.json").read_text()
)


def test_real_chain_identity():
    assert CLOSURE["chainId"] == 2026073005


def test_header_only_body_digest_unchanged():
    assert CLOSURE["headerOnly"]["bodyDigestUnchanged"]


def test_header_only_version_rules():
    assert CLOSURE["headerOnly"]["bodyVersion"] == CLOSURE["headerOnly"]["keyVersion"] == 2


def test_revoked_recipient_absent():
    assert CLOSURE["headerOnly"]["revokedRecipientAbsent"]


def test_legal_recipient_retained():
    assert CLOSURE["headerOnly"]["legalRecipientRetained"]


def test_body_rotation_versions():
    assert CLOSURE["bodyRotation"]["bodyVersion"] == CLOSURE["bodyRotation"]["keyVersion"] == 3


def test_old_ck_cannot_open_new_body():
    assert CLOSURE["bodyRotation"]["oldCkCannotOpenNewBody"]


def test_old_ck_old_body_limitation_is_explicit():
    assert CLOSURE["bodyRotation"]["oldCkCanOpenOldBodyAcceptedLimitation"]


def test_ck_record_is_ciphertext_plus_tag():
    assert CLOSURE["bodyRotation"]["encryptedCkRecordBytes"] == 48


def test_scan_is_bounded_and_reads_state_at_event_block():
    assert SCAN["startBlock"] <= SCAN["endBlock"]
    assert SCAN["observed"] == len(SCAN["stateReadsAtEventBlock"]) + 0


def test_scan_idempotency():
    assert SCAN2["inserted"] == 0 and SCAN2["duplicates"] == SCAN2["observed"]


def test_database_real_receipts():
    assert DB["realIsolatedChainReceipts"] == 4


def test_database_invariants():
    assert DB["invariantViolations"] == DB["partialTransactions"] == DB["prematureCommitted"] == 0


@pytest.mark.parametrize("field", ["partialSuccesses", "staleOverwrites", "prematureCommitted"])
def test_no_partial_or_stale_success(field):
    assert CLOSURE[field] == 0


def test_no_formal_assets_used():
    assert not CLOSURE["formalChainAccessed"]
    assert not CLOSURE["formalDatabaseModified"]
    assert not CLOSURE["privateKeysPersisted"]
