def test_key_version_increment_without_body_rejected_on_chain(chain_result):
    assert chain_result["rejections"]["keyBodyMismatch"]
