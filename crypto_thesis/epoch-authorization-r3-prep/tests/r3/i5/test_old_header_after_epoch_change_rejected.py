from epoch_auth_r3.blockchain.composite_gateway import CompositeReadStatus, CompositeStateGateway


def test_old_header_after_epoch_change_rejected(w3, contracts, chain_result):
    auth, registry = contracts
    resource = bytes.fromhex(chain_result["resourceId"])
    old = registry.functions.getAnchor(resource, 3).call()
    current_auth = auth.functions.getResource(resource).call()
    assert (old[3], old[4]) != (current_auth[2], current_auth[5])
