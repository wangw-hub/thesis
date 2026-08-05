def test_header_registry_unauthorized(chain_result):
    assert chain_result["rejections"]["unauthorized"]
    assert chain_result["rejections"]["unknownResource"]
    assert chain_result["rejections"]["invalidAuthorizationContract"]
