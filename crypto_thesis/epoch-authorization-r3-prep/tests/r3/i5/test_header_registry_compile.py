import json
from pathlib import Path


def test_header_registry_compile():
    artifact = json.loads(Path("contracts/r3/build/HeaderRegistryV1.json").read_text())
    assert artifact["compiler"].startswith("0.8.30+")
    assert artifact["evmVersion"] == "london"
    assert artifact["bytecode"] and artifact["deployedBytecode"]
