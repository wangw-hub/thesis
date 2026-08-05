def test_body_rotation_transition(contracts, chain_result):
    _, registry = contracts
    anchor = registry.functions.getAnchor(bytes.fromhex(chain_result["resourceId"]), 3).call()
    assert (anchor[5], anchor[6], anchor[7], anchor[8]) == (3, 2, 2, 2)
