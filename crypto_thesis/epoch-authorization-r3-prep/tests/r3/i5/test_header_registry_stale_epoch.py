def test_header_registry_stale_epoch(chain_result):
    assert chain_result["rejections"]["wrongEpoch"]
    assert chain_result["rejections"]["staleAuthorizationState"]
