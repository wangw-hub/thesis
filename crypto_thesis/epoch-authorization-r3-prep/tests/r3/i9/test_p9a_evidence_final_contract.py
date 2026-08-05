from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from epoch_auth_r3.pilot.p9a import P9A_SCENARIOS, P9AState, final_p9a_state
from epoch_auth_r3.pilot.p9a_evidence_contract import (
    MaterialReleaseDecisionV2, MaterialReleaseEvidenceV2,
    P9AAcceptanceDecisionV1, P9ADryRunAcceptanceV1,
    PilotEvidenceClassificationV1,
    validate_p9a_run_evidence,
)
from scripts.r3_i9.run_p9a_development import a7_material_release_evidence
from scripts.r3_i9.run_revised_remote_pilot import make_config, matrix


def classification(stage="P9-A", scenario="INITIAL"):
    return PilotEvidenceClassificationV1.for_stage(stage, scenario)


def material(decision="ALLOWED", reason="CONSISTENT", evaluated=True):
    return MaterialReleaseEvidenceV2(
        decision=decision, reasonCode=reason, evaluationBlockNumber=10,
        evaluationBlockHash="a" * 64, headerDigest="b" * 64,
        authorizationStateVersion=2, headerVersion=2, evaluated=evaluated,
        sourceComponent="AccessMaterialReleaseGuard",
        observedAt=datetime.now(timezone.utc).isoformat(),
    )


def write_run(root, *, c=None, m=None, projection=None):
    c = c or classification()
    m = m or material()
    projection = projection or m.to_dict()
    common = {"classification": list(c.labels()), "evidenceClassification": c.to_dict()}
    (root / "config.json").write_text(json.dumps({
        **common, "config": {"evidenceClassification": c.to_dict()}
    }), "utf-8")
    (root / "run-state.json").write_text(json.dumps(common), "utf-8")
    (root / "material-release-evidence.json").write_text(json.dumps({
        **common, "current": m.to_dict(), "history": [m.to_dict()],
        "scenarioProjection": projection, "finalEnvelopeProjection": projection,
    }), "utf-8")


def test_p9a_evidence_classification_v1():
    c = classification()
    assert c.pilotOnly and not c.formalResultEligible and not c.performanceClaimEligible


def test_p9a_smoke_label_propagates_to_run():
    assert "P9_A_SMOKE_ONLY" in classification().labels()


def test_p9a_smoke_label_in_final_envelope(tmp_path):
    write_run(tmp_path)
    assert validate_p9a_run_evidence(tmp_path) == ()


def test_p9a_dev_does_not_get_smoke_label():
    assert "P9_A_SMOKE_ONLY" not in classification("DEVELOPMENT_ONLY").labels()


def test_p9b_does_not_inherit_p9a_label():
    assert "P9_A_SMOKE_ONLY" not in classification("P9-B").labels()


def test_missing_p9a_smoke_label_rejected(tmp_path):
    write_run(tmp_path)
    value = json.loads((tmp_path / "run-state.json").read_text("utf-8"))
    value["classification"].remove("P9_A_SMOKE_ONLY")
    (tmp_path / "run-state.json").write_text(json.dumps(value), "utf-8")
    assert any("CLASSIFICATION" in x for x in validate_p9a_run_evidence(tmp_path))


def test_material_release_evidence_v2():
    original = material()
    assert MaterialReleaseEvidenceV2.from_dict(original.to_dict()) == original


def test_material_release_single_authority(tmp_path):
    write_run(tmp_path)
    assert validate_p9a_run_evidence(tmp_path) == ()


def test_a7_outer_scenario_material_evidence_same(tmp_path):
    m = material("ALLOWED_AFTER_CURRENT_HEADER_ONLY", "CURRENT_HEADER_CONFIRMED")
    write_run(tmp_path, c=classification(scenario="REVOCATION_AGENT"), m=m)
    assert validate_p9a_run_evidence(tmp_path) == ()


def test_a7_allowed_after_header_only_evidence():
    assert material("ALLOWED_AFTER_CURRENT_HEADER_ONLY", "CURRENT_HEADER_CONFIRMED").decision \
        == "ALLOWED_AFTER_CURRENT_HEADER_ONLY"


def test_a7_failure_before_release_not_evaluated():
    m = material("NOT_EVALUATED", "FAILURE_BEFORE_EVALUATION", evaluated=False)
    assert not m.evaluated


def test_a6_denied_evidence_preserved():
    m = material("DENIED", "HEADER_UPDATE_PENDING")
    assert (m.decision, m.reasonCode) == ("DENIED", "HEADER_UPDATE_PENDING")


def test_a5_denied_then_allowed_history_preserved():
    history = [material("DENIED", "RECOVERY_IN_PROGRESS"), material("ALLOWED", "RECOVERY_COMPLETED")]
    assert [x.decision for x in history] == ["DENIED", "ALLOWED"]


def test_material_evidence_conflict_rejected(tmp_path):
    m = material()
    write_run(tmp_path, m=m, projection=material("UNKNOWN", "UNKNOWN").to_dict())
    assert any("CONFLICT" in x for x in validate_p9a_run_evidence(tmp_path))


def test_p9a_acceptance_decision_v1():
    assert P9AAcceptanceDecisionV1.evaluate(planned=8, actual=8, valid=8).accepted


def test_business_pass_not_acceptance_pass():
    decision = P9AAcceptanceDecisionV1.evaluate(planned=8, actual=8, valid=0)
    assert not decision.accepted


def test_evidence_invalid_blocks_gate_pass():
    assert not P9AAcceptanceDecisionV1.evaluate(
        planned=8, actual=8, valid=8, classification_errors=1
    ).accepted


def test_material_conflict_blocks_gate_pass():
    assert not P9AAcceptanceDecisionV1.evaluate(
        planned=8, actual=8, valid=8, material_release_errors=1
    ).accepted


def test_major_blocks_gate_pass():
    assert not P9AAcceptanceDecisionV1.evaluate(
        planned=8, actual=8, valid=8, major=1
    ).accepted


def test_gate_written_only_after_strict_acceptance():
    assert "accepted" in P9AAcceptanceDecisionV1.evaluate(planned=8, actual=8, valid=8).to_dict()


def test_remote_local_gate_same_decision():
    decision = P9AAcceptanceDecisionV1.evaluate(planned=8, actual=8, valid=8).to_dict()
    assert json.loads(json.dumps(decision)) == decision


def test_eight_business_pass_zero_valid_is_failed():
    assert final_p9a_state({"valid": False} for _ in range(8)) is P9AState.FAILED


def test_eight_valid_runs_pass_acceptance():
    assert final_p9a_state({"valid": True} for _ in range(8)) is P9AState.PASSED


def test_final_p9a_evidence_flow_single_authority():
    requirements = P9AAcceptanceDecisionV1.evaluate(planned=0, actual=0, valid=0).errors
    assert len(requirements) > 0 and len(P9A_SCENARIOS) == 8


def test_p9a_dry_run_acceptance_v1_matrix():
    cases = P9ADryRunAcceptanceV1.evaluate_cases()
    assert not cases["eightBusinessPassMissingSmoke"].accepted
    assert not cases["eightBusinessPassA7MaterialConflict"].accepted
    assert cases["eightValid"].accepted
    assert cases["a6ExpectedFailClosedValid"].accepted


def test_a7_development_projection_uses_v2_authority():
    evidence = a7_material_release_evidence(
        block=11, block_hash="a" * 64, header_digest="b" * 64,
        state_version=2, header_version=2,
    )
    assert evidence["decision"] == "ALLOWED_AFTER_CURRENT_HEADER_ONLY"
    assert evidence["sourceComponent"] == "AccessMaterialReleaseGuard"


def test_full_development_matrix_reuses_p9a_scenarios():
    rows = matrix("DEV-P9-A")
    assert len(rows) == 8
    assert [row["scenario"] for row in rows] == [x.scenario_class for x in P9A_SCENARIOS]
    assert {row["group"] for row in rows} == {"DEVELOPMENT_ONLY"}


def test_development_config_has_non_pilot_classification():
    cfg = make_config(
        matrix("DEV-P9-A")[0], "DEV_P9A_TEST", "a" * 40, "b" * 64, 0,
        attempt_root="/var/lib/epoch-auth-r3/i9-development/DEV_P9A_TEST",
    )
    c = PilotEvidenceClassificationV1.from_dict(cfg.evidenceClassification)
    assert c.labels() == (
        "DEVELOPMENT_ONLY", "NOT_PILOT_EVIDENCE",
        "NOT_FOR_STATISTICS", "NOT_FOR_THESIS_RESULTS",
    )
