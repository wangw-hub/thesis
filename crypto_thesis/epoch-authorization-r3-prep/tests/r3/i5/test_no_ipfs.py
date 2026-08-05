from pathlib import Path


def test_no_ipfs():
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("src/epoch_auth_r3/blockchain").glob("*.py")
    ).lower()
    assert "ipfs" not in sources and "kubo" not in sources
