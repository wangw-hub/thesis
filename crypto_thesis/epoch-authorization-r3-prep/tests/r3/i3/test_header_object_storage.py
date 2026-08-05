from epoch_auth_r3.header.models import SignedVersionedHeaderV1
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind


def test_signed_header_is_stored_as_header_object(tmp_path, signed_header):
    store = LocalObjectStore(tmp_path)
    ref = store.put(signed_header.to_canonical_bytes(), namespace="header", object_kind=ObjectKind.HEADER)
    assert ref.object_kind is ObjectKind.HEADER and store.verify(ref).verified
    assert SignedVersionedHeaderV1.from_strict_json_bytes(store.get(ref)) == signed_header
