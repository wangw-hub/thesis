from epoch_auth_r3.blockchain.composite_gateway import CompositeReadStatus, CompositeStateGateway


def test_same_block_dual_read(w3, contracts, chain_result):
    frozen = chain_result["sameBlockRead"]
    assert frozen["blockNumber"] == chain_result["blocks"]["bodyRotation"]
    assert frozen["authorizationEpoch"] == 1
    assert frozen["headerVersion"] == 3
