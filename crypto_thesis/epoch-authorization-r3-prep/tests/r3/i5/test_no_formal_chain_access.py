def test_no_formal_chain_access(chain_result):
    assert chain_result["chainId"] == 2026073005
    assert chain_result["formalChainAccessed"] is False
