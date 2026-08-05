from scripts.r3_i9.run_revised_remote_pilot import matrix


def test_p9b_frozen_matrix_has_update_paths():
    rows = matrix("P9-B")
    assert len(rows) == 45
    assert sum(row["scenario"] == "HEADER_ONLY" for row in rows) == 18
    assert sum(row["scenario"] == "BODY_ROTATION" for row in rows) == 27


def test_p9b_update_paths_require_three_chain_transactions():
    for row in matrix("P9-B"):
        assert row["scenario"] in {"HEADER_ONLY", "BODY_ROTATION"}
        # The runner's default is intentionally not stored in the matrix so
        # the plan derives it from the frozen update semantic class.
        assert row.get("expectedTransactionCount") is None
