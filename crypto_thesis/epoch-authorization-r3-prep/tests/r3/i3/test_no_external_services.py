import ast
from pathlib import Path


def test_i3_modules_have_no_external_service_imports():
    forbidden = {"requests", "httpx", "socket", "web3", "psycopg", "ipfshttpclient"}
    source = Path(__file__).resolve().parents[3] / "src" / "epoch_auth_r3"
    imported = set()
    for path in [*source.joinpath("header").rglob("*.py"), *source.joinpath("workflows").rglob("*.py")]:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
    assert not forbidden.intersection(imported)
