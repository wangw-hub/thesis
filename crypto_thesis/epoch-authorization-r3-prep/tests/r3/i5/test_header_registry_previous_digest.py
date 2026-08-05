def test_header_registry_previous_digest(chain_result):
    assert chain_result["rejections"]["wrongPreviousHeaderDigest"]
