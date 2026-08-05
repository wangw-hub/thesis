def test_initial_version_transition(contracts, chain_result):
    _, registry = contracts
    anchor = registry.functions.getAnchor(bytes.fromhex(chain_result["resourceId"]), 1).call()
    assert (anchor[5], anchor[6], anchor[7], anchor[8], anchor[15]) == (1, 1, 1, 0, True)
