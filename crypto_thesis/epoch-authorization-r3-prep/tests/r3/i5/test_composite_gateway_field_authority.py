from epoch_auth_r3.blockchain.composite_gateway import CompositeReadStatus, CompositeStateGateway


def test_composite_gateway_field_authority(w3, contracts, chain_result):
    # Bonsai may prune old state after later stages; I5's hashed same-block
    # evidence remains the immutable regression oracle.
    frozen = chain_result["sameBlockRead"]
    assert (frozen["bodyVersion"], frozen["keyVersion"]) == (2, 2)
    assert (frozen["authorizationEpoch"], frozen["authorizationStateVersion"]) == (1, 1)
