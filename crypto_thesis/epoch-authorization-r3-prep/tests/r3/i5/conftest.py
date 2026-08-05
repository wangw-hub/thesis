import json
import os
import sys
from pathlib import Path

import pytest
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="session")
def chain_result():
    return json.loads(Path(os.environ["R3_I5_CHAIN_RESULT"]).read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def w3():
    client = Web3(Web3.HTTPProvider(os.environ.get("R3_I5_RPC_URL", "http://127.0.0.1:16545")))
    client.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    assert client.is_connected()
    assert client.eth.chain_id == 2026073005
    return client


@pytest.fixture(scope="session")
def contracts(w3, chain_result):
    auth_artifact = json.loads(
        Path(r"D:\Research\crypto_thesis\epoch-authorization\contracts\build\AuthorizationState.json")
        .read_text(encoding="utf-8")
    )
    registry_artifact = json.loads(
        (ROOT / "contracts/r3/build/HeaderRegistryV1.json").read_text(encoding="utf-8")
    )
    auth = w3.eth.contract(address=chain_result["authorizationState"], abi=auth_artifact["abi"])
    registry = w3.eth.contract(address=chain_result["headerRegistry"], abi=registry_artifact["abi"])
    return auth, registry
