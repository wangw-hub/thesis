def test_key_version_equals_body_version_on_chain(contracts, chain_result):
    _, registry = contracts
    resource = bytes.fromhex(chain_result["resourceId"])
    assert all(registry.functions.getAnchor(resource, version).call()[6] ==
               registry.functions.getAnchor(resource, version).call()[7]
               for version in (1, 2, 3))
