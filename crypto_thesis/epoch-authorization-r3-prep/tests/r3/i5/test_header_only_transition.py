def test_header_only_transition(contracts, chain_result):
    _, registry = contracts
    anchor = registry.functions.getAnchor(bytes.fromhex(chain_result["resourceId"]), 2).call()
    assert (anchor[5], anchor[6], anchor[7], anchor[8]) == (2, 1, 1, 1)
