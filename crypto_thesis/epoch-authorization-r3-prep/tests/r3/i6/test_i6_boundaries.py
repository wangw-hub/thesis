from pathlib import Path
import hashlib
import subprocess


ROOT = Path(__file__).resolve().parents[3]


def test_no_ipfs():
    assert not (ROOT / "src/epoch_auth_r3/ipfs").exists()


def test_no_formal_contract_change():
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "contracts/AuthorizationState.sol"],
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0


def test_agent_has_no_unbounded_loop():
    text = (ROOT / "src/epoch_auth_r3/revocation/agent.py").read_text(encoding="utf-8")
    assert "while True" not in text


def test_migration_does_not_create_plaintext_secret_columns():
    text = (ROOT / "migrations/r3_control/0010_i6_revocation_agent.sql").read_text(encoding="utf-8")
    assert "plaintext_ck" not in text.lower()
    assert "root_kek" not in text.lower()
