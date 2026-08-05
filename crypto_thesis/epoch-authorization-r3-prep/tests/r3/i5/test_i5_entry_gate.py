def test_i5_entry_gate(w3, chain_result):
    assert w3.eth.chain_id == 2026073005
    assert chain_result["formalChainAccessed"] is False
