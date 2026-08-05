from __future__ import annotations

import json
from pathlib import Path

import pytest
from web3 import EthereumTesterProvider, Web3


@pytest.fixture
def contract_env():
    root = Path(__file__).resolve().parents[2]
    artifact = json.loads(
        (root / "contracts" / "build" / "AuthorizationState.json").read_text("utf-8")
    )
    web3 = Web3(EthereumTesterProvider())
    admin, owner, authorizer, revoker, outsider, user = web3.eth.accounts[:6]
    factory = web3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    receipt = web3.eth.wait_for_transaction_receipt(
        factory.constructor().transact({"from": admin})
    )
    contract = web3.eth.contract(address=receipt.contractAddress, abi=artifact["abi"])
    for role_name, account in [
        ("OWNER_ROLE", owner),
        ("AUTHORIZER_ROLE", authorizer),
        ("REVOCATION_ROLE", revoker),
    ]:
        role = contract.functions.__getattribute__(role_name)().call()
        tx = contract.functions.grantRole(role, account).transact({"from": admin})
        web3.eth.wait_for_transaction_receipt(tx)
    return {
        "w3": web3,
        "contract": contract,
        "admin": admin,
        "owner": owner,
        "authorizer": authorizer,
        "revoker": revoker,
        "outsider": outsider,
        "user": user,
        "resource_id": Web3.keccak(text="resource-1"),
        "user_id": Web3.keccak(text="user-1"),
        "digest": Web3.keccak(text="policy-1"),
        "key_id": Web3.keccak(text="user-key-1"),
    }
