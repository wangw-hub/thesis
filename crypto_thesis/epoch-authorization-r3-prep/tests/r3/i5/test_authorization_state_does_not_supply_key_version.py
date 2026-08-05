def test_authorization_state_does_not_supply_key_version(contracts, chain_result):
    auth, _ = contracts
    record = auth.functions.getResource(bytes.fromhex(chain_result["resourceId"])).call()
    assert len(record) == 7
