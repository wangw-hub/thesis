from epoch_auth_r3.crypto.hpke_provider import PyHPKEProvider
from epoch_auth_r3.crypto.key_material import TestOnlyEphemeral as VectorEphemeral

INFO = bytes.fromhex("4f6465206f6e2061204772656369616e2055726e")
SKE = bytes.fromhex("52c4a758a802cd8b936eceea314432798d5baf2d7e9235dc084ab1b9cfa2f736")
PKE = bytes.fromhex("37fda3567bdbd628e88668c3c8d7e97d1d1253b6d4ea6d44c150f741f1bf4431")
SKR = bytes.fromhex("4612c550263fc8ad58375df3f557aac531d26850903e55a9f23f21d8534e8ac8")
PKR = bytes.fromhex("3948cfe0ad1ddb695d780e59077195da6c56506b027329794ab02bca80815c4d")
PT = bytes.fromhex("4265617574792069732074727574682c20747275746820626561757479")
AADS = [bytes.fromhex(x) for x in ("436f756e742d30", "436f756e742d31", "436f756e742d32")]
CTS = [bytes.fromhex(x) for x in (
    "f938558b5d72f1a23810b4be2ab4f84331acc02fc97babc53a52ae8218a355a96d8770ac83d07bea87e13c512a",
    "af2d7e9ac9ae7e270f46ba1f975be53c09f8d875bdc8535458c2494e8a6eab251c03d0c22a56b8ca42c2063b84",
    "498dfcabd92e8acedc281e85af1cb4e3e31c7dc394a1ca20e173cb72516491588d96a19ad4a683518973dcc180",
)]


def test_rfc9180_a_1_1_exact_enc_ciphertexts_exporters_and_recipient():
    provider = PyHPKEProvider()
    enc, sender = provider.create_sender_context_for_test(
        PKR, INFO, VectorEphemeral(SKE, PKE)
    )
    assert enc == PKE
    for aad, expected in zip(AADS, CTS):
        assert sender.seal(PT, aad) == expected
    expected_exports = (
        (b"", bytes.fromhex("3853fe2b4035195a573ffc53856e77058e15d9ea064de3e59f4961d0095250ee")),
        (b"\x00", bytes.fromhex("2e8f0b54673c7029649d4eb9d5e33bf1872cf76d623ff164ac185da9e88c21a5")),
        (b"TestContext", bytes.fromhex("e9e43065102c3836401bed8c3c3c75ae46be1639869391d62c61f1ec7af54931")),
    )
    for context, expected in expected_exports:
        assert sender.export(context, 32) == expected
    recipient = provider.create_recipient_context_for_test(SKR, enc, INFO)
    for aad, ct in zip(AADS, CTS):
        assert recipient.open(ct, aad) == PT


def test_frozen_suite_ids():
    assert vars(PyHPKEProvider().suite_metadata()) == {
        "provider": "pyhpke", "version": "0.6.4", "mode": 0,
        "kem_id": 32, "kdf_id": 1, "aead_id": 1,
    }
