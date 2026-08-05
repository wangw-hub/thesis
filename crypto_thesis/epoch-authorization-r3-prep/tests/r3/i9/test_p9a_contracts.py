from dataclasses import replace

from epoch_auth_r3.pilot.p9a import (
    P9A_LABELS,
    P9A_SCENARIOS,
    P9AState,
    final_p9a_state,
    run_p9a_serially,
    validate_p9a_matrix,
)


ATTEMPT = "I9_P9A_20260731T000000Z_deadbee"


def test_p9a_exactly_eight_configs():
    assert len(validate_p9a_matrix(P9A_SCENARIOS, attempt_id=ATTEMPT)) == 8


def test_p9a_one_seed_per_config():
    assert len({row.seed for row in P9A_SCENARIOS}) == 8


def test_p9a_attempt_isolation():
    current = {row.run_id(ATTEMPT) for row in P9A_SCENARIOS}
    old = {
        row.run_id("I9_P9A_20260731T000001Z_deadbee")
        for row in P9A_SCENARIOS
    }
    assert current.isdisjoint(old)


def test_p9a_no_p9b_tasks():
    assert all("P9_B" not in row.scenario_id for row in P9A_SCENARIOS)


def test_p9a_scenario_matrix():
    assert [row.scenario_class for row in P9A_SCENARIOS] == [
        "INITIAL",
        "HEADER_ONLY",
        "BODY_ROTATION",
        "IPFS_REPLICATION",
        "IPFS_RESTORE",
        "HEADER_UPDATE_PENDING",
        "REVOCATION_AGENT",
        "RECOVERY_RECONCILIATION",
    ]
    assert [row.expected_outcome_class for row in P9A_SCENARIOS].count(
        "FAIL_CLOSED_EXPECTED"
    ) == 1
    assert [row.expected_outcome_class for row in P9A_SCENARIOS].count(
        "RECOVERY_EXPECTED"
    ) == 2


def test_p9a_stage_gate_stops_on_failure():
    called = []

    def execute(row):
        called.append(row.scenario_id)
        return {"valid": len(called) < 3}

    results = run_p9a_serially(P9A_SCENARIOS, execute)
    assert len(results) == 3
    assert final_p9a_state(results) is P9AState.FAILED


def test_p9a_pass_requires_all_eight():
    assert final_p9a_state({"valid": True} for _ in range(7)) is P9AState.FAILED
    assert final_p9a_state({"valid": True} for _ in range(8)) is P9AState.PASSED


def test_p9a_no_formal_claims():
    assert "P9_A_SMOKE_ONLY" in P9A_LABELS
    assert "NOT_FOR_FORMAL_THESIS_RESULTS" in P9A_LABELS
    assert "NOT_FOR_PERFORMANCE_CLAIMS" in P9A_LABELS


def test_p9a_duplicate_seed_rejected():
    rows = list(P9A_SCENARIOS)
    rows[1] = replace(rows[1], seed=rows[0].seed)
    try:
        validate_p9a_matrix(rows, attempt_id=ATTEMPT)
    except ValueError as exc:
        assert str(exc) == "P9A_SEED_DUPLICATE"
    else:
        raise AssertionError("duplicate seed accepted")
