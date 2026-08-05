def test_body_rotation_body_digest_must_change(contracts, chain_result):
    _, registry = contracts
    resource = bytes.fromhex(chain_result["resourceId"])
    assert registry.functions.getAnchor(resource, 2).call()[12] != registry.functions.getAnchor(resource, 3).call()[12]
