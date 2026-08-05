def test_header_registry_roles(contracts, chain_result):
    _, registry = contracts
    role = registry.functions.HEADER_COMMITTER_ROLE().call()
    assert registry.functions.hasRole(role, "0xA35ea76E6ebAdd2643a0d154e18FE1E5EF2dE5A4").call()
    assert chain_result["rejections"]["revokedCommitter"]
    assert chain_result["rejections"]["adminBypass"]
