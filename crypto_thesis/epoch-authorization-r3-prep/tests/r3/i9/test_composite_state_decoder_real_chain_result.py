"""Runs only when explicitly enabled against the isolated I5 chain."""
import os
import json
from pathlib import Path
import pytest


@pytest.mark.skipif(os.getenv("R3_I9_REAL_CHAIN") != "1", reason="isolated-chain preflight only")
def test_composite_decoder_reads_isolated_chain():
    from epoch_auth_r3.blockchain import CompositeReadStatus, CompositeStateGateway
    from epoch_auth_r3.blockchain.web3_factory import BesuQbftWeb3FactoryV1
    from scripts.r3_i9.run_revised_remote_pilot import AUTH_ABI, CHAIN_ID
    w3 = BesuQbftWeb3FactoryV1.create(
        os.environ["R3_I9_RPC_URL"], expected_chain_id=CHAIN_ID,
    )
    auth = w3.eth.contract(address=os.environ["R3_I9_AUTHORIZATION"], abi=AUTH_ABI)
    artifact = Path("contracts/r3/build/HeaderRegistryV1.json")
    registry = w3.eth.contract(
        address=os.environ["R3_I9_HEADER_REGISTRY"],
        abi=json.loads(artifact.read_text("utf-8"))["abi"],
    )
    result = CompositeStateGateway(w3, auth, registry).read(bytes.fromhex(os.environ["R3_I9_RESOURCE_ID"]))
    assert result.status is CompositeReadStatus.CONFIRMED
    assert result.resource_id == bytes.fromhex(os.environ["R3_I9_RESOURCE_ID"])
