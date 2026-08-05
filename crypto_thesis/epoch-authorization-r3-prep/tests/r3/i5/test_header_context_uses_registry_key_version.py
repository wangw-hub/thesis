from epoch_auth_r3.blockchain.composite_gateway import CompositeStateGateway


def test_header_context_uses_registry_key_version(w3, contracts, chain_result):
    frozen = chain_result["sameBlockRead"]
    assert frozen["keyVersion"] == chain_result["current"]["keyVersion"]
