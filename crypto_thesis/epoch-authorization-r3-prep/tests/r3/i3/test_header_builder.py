from conftest import TEST_ONLY_CK, build_header


def test_builder_returns_immutable_self_validating_header():
    header = build_header()
    header.validate_schema()
    assert header.signature.header_digest
    try:
        header.core.epoch = 5
        assert False
    except Exception:
        pass
