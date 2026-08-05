# Header Verification Context

`HeaderVerificationContextV1` supplies expected chain/contract/resource/policy/epoch/state/Header/key/previous-digest/Body-reference values plus trusted issuer key ID and public key.

This object is a local I3 trust input, not proof that a chain state is current. I3 tests use fixed local values. Future chain integration must construct it fail-closed from accepted chain state rather than Header-controlled data.

