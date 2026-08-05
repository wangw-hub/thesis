import hashlib
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from epoch_auth_r3.header.builder import VersionedHeaderBuilderV1
from epoch_auth_r3.header.context import HeaderBuildContextV1, RecipientPublicKeyV1, verification_context_for
from epoch_auth_r3.storage import ObjectKind, ObjectReferenceV1

TEST_ONLY_HEADER_SEED = b"H" * 32
TEST_ONLY_CK = b"C" * 32


def make_context(version=1, previous=None, **changes):
    values = dict(
        chain_id=1337, authorization_contract="0x" + "11" * 20,
        header_registry="0x" + "22" * 20, resource_id="33" * 32,
        body_version=1, policy_digest="44" * 32, epoch=2, state_version=3,
        header_version=version, key_version=1, previous_header_digest=previous,
        issuer_key_id="test-header-key-v1",
    )
    values.update(changes)
    return HeaderBuildContextV1(**values)


def private_key(byte):
    return bytes([byte]) * 32


def public_key(private):
    return X25519PrivateKey.from_private_bytes(private).public_key().public_bytes_raw()


def recipients():
    return [
        RecipientPublicKeyV1("bb" * 32, 2, public_key(private_key(9))),
        RecipientPublicKeyV1("aa" * 32, 1, public_key(private_key(7))),
    ]


def body_reference(data=b"encrypted-body"):
    digest = hashlib.sha256(data).hexdigest()
    return ObjectReferenceV1(1, "local", "body", ObjectKind.BODY, "sha256", digest, len(data))


def build_header(context=None, recipient_list=None, body_ref=None):
    return VersionedHeaderBuilderV1().build(
        context=context or make_context(), body_reference=body_ref or body_reference(),
        content_key=TEST_ONLY_CK, recipients=recipient_list or recipients(),
        signing_private_seed=TEST_ONLY_HEADER_SEED,
    )


def signing_public():
    return Ed25519PrivateKey.from_private_bytes(TEST_ONLY_HEADER_SEED).public_key().public_bytes_raw()


def verification(header, **changes):
    base = verification_context_for(header.core, signing_public(), "test-header-key-v1")
    return replace(base, **changes)


@pytest.fixture
def signed_header():
    return build_header()
