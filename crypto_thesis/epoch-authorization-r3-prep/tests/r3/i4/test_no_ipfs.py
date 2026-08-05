from pathlib import Path


def test_i4_database_code_has_no_ipfs_client():
    root=Path(__file__).resolve().parents[3]/"src"/"epoch_auth_r3"/"database"
    assert all("ipfs" not in p.read_text("utf-8").lower() for p in root.glob("*.py"))
