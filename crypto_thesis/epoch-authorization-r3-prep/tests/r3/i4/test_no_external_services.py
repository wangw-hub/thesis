from pathlib import Path


def test_database_layer_has_no_chain_ipfs_or_http_clients():
    root=Path(__file__).resolve().parents[3]/"src"/"epoch_auth_r3"/"database"
    text="\n".join(p.read_text("utf-8") for p in root.glob("*.py"))
    for token in ("web3","requests","httpx","ipfs","besu"):
        assert token not in text.lower()
