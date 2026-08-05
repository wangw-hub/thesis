def test_header_registry_replay(chain_result):
    assert chain_result["rejections"]["operationReplay"]
