from pathlib import Path


def test_i4_database_code_has_no_chain_client():
    root=Path(__file__).resolve().parents[3]/"src"/"epoch_auth_r3"/"database"
    text="\n".join(p.read_text("utf-8") for p in root.glob("*.py")).lower()
    assert "web3" not in text and "besu" not in text and "rpc" not in text
