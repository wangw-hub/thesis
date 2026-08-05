import ast
from pathlib import Path


def test_storage_modules_have_no_network_database_chain_or_ipfs_imports():
    forbidden = {"requests", "httpx", "socket", "web3", "psycopg", "ipfshttpclient"}
    root = Path(__file__).resolve().parents[3] / "src" / "epoch_auth_r3" / "storage"
    imported = set()
    for path in root.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
    assert not imported.intersection(forbidden)
