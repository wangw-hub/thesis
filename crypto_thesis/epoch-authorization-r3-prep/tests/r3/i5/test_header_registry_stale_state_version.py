def test_header_registry_stale_state_version(chain_result):
    assert chain_result["rejections"]["wrongStateVersion"]
