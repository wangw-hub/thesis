def test_body_increment_without_key_rejected_on_chain(chain_result):
    assert chain_result["rejections"]["keyBodyMismatch"]
