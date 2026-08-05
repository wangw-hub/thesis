def test_header_registry_key_version_authority(contracts, chain_result):
    _, registry = contracts
    anchor = registry.functions.getCurrentAnchor(bytes.fromhex(chain_result["resourceId"])).call()
    assert anchor[6] == anchor[7]
    assert anchor[6] >= chain_result["current"]["bodyVersion"]
