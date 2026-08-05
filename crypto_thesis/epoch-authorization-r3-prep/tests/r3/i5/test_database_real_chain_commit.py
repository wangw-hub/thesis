import json
from pathlib import Path


def test_database_real_chain_commit():
    result = json.loads(Path(
        "experiments/r3/i5-header-registry/raw/database-chain-closure.json"
    ).read_text())
    assert (result["jobStatus"], result["commitStatus"], result["evidenceSource"]) == (
        "COMMITTED", "CONFIRMED_REAL_CHAIN", "REAL_ISOLATED_CHAIN_ONLY"
    )
    assert result["receiptStatus"] == 1
