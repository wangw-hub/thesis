def test_header_committed_event(w3, contracts, chain_result):
    _, registry = contracts
    receipt = w3.eth.get_transaction_receipt(bytes.fromhex(chain_result["transactions"]["initial"]))
    events = registry.events.HeaderCommittedV1().process_receipt(receipt)
    assert len(events) == 1
    assert events[0]["args"]["operationId"].hex() == chain_result["trigger"]["operationId"]
