from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_real_besu_semantic_evidence_matches_frozen_expectations():
    report = json.loads(
        (ROOT / "blockchain" / "besu" / "semantic-check.json").read_text("utf-8")
    )
    assert report["chain_id"] == 20260728
    assert report["cap2_accepted"] is True
    assert report["proposed_cap2_accepted"] is True
    assert report["replay_code"] == "NONCE_REPLAY"
    assert report["cross_contract_code"] == "CHAIN_CONTEXT_MISMATCH"
    assert report["stale_policy_code"] == "POLICY_DIGEST_MISMATCH"
    assert report["stale_epoch_code"] == "EPOCH_MISMATCH"
    assert report["stale_user_code"] == "USER_VERSION_MISMATCH"
    assert report["cross_chain_code"] == "CHAIN_CONTEXT_MISMATCH"
    assert report["suspended_user_code"] == "USER_INACTIVE"
    assert report["revoked_resource_code"] == "RESOURCE_INACTIVE"


def test_controlled_fault_evidence_is_functional_not_performance_data():
    report = json.loads(
        (ROOT / "blockchain" / "besu" / "fault-check.json").read_text("utf-8-sig")
    )
    assert report["blocks_progressed_during_fault"] > 0
    assert report["rpc_outage_observed"] is True
    assert report["formal_performance_result"] is False
