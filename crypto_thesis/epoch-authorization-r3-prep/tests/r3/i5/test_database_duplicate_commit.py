def test_database_duplicate_commit(contracts, chain_result):
    _, registry = contracts
    operation_id = bytes.fromhex(chain_result["trigger"]["operationId"])
    assert registry.functions.operationUsed(operation_id).call() is True
