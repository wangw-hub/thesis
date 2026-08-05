from dataclasses import replace

import pytest

from epoch_auth_r3.pilot.config import R3PilotConfigV1, deterministic_run_id
from epoch_auth_r3.pilot.pairing import assert_semantically_comparable, pair_id
from epoch_auth_r3.pilot.state import PilotRunStateV1, validate_transition
from epoch_auth_r3.pilot.workload import R3PilotWorkloadGeneratorV1


def config(**changes):
    value = dict(
        schemaVersion=1, pilotProtocolVersion="I9_PILOT_V1", pilotRunGroupId="g",
        seed=7, workloadId="R3_I9_PILOT_ONLY_W1", scenarioClass="HEADER_ONLY",
        updateKind="HEADER_ONLY", bodySizeBytes=64, recipientCount=2,
        affectedResourceCount=1, workerCount=1, storageMode="LOCAL_IPFS",
        faultScenario="NONE", repeatIndex=0, warmup=False, measurementEnabled=True,
        chainId=2026073005, authorizationStateAddress="0x"+"12"*20,
        headerRegistryAddress="0x"+"28"*20, databaseName="epoch_auth_r3_i9_pilot",
        localObjectStoreRoot="/var/lib/epoch-auth-r3/i9-pilot/local-store",
        kuboApi="http://127.0.0.1:15001", kuboAddProfileDigest="a"*64,
        softwareCommit="b"*40, environmentManifestDigest="c"*64,
        createdAt="2026-07-30T00:00:00Z",
    )
    value.update(changes)
    return R3PilotConfigV1(**value)


def test_run_id_deterministic_and_created_at_excluded():
    first = config()
    assert deterministic_run_id(first) == deterministic_run_id(replace(first, createdAt="later"))
    assert deterministic_run_id(first) != deterministic_run_id(replace(first, seed=8))


def test_strict_config_unknown_and_missing_rejected():
    value = config().__dict__.copy(); value["unknown"] = 1
    with pytest.raises(ValueError): R3PilotConfigV1.from_strict_dict(value)
    value.pop("unknown"); value.pop("seed")
    with pytest.raises(ValueError): R3PilotConfigV1.from_strict_dict(value)


@pytest.mark.parametrize("size", [0, 1, 64, 65536])
def test_workload_reproducible_and_sized(size):
    a = R3PilotWorkloadGeneratorV1.generate(4, size)
    assert a == R3PilotWorkloadGeneratorV1.generate(4, size)
    assert len(a) == size
    assert R3PilotWorkloadGeneratorV1.manifest(4, size)["plaintextSha256"]


def test_state_machine_and_terminal_immutability():
    validate_transition(PilotRunStateV1.PLANNED, PilotRunStateV1.ENVIRONMENT_CHECKED)
    with pytest.raises(ValueError):
        validate_transition(PilotRunStateV1.EVIDENCE_VERIFIED, PilotRunStateV1.RUNNING)


def test_semantic_noncomparability():
    left = config().__dict__
    right = replace(config(), scenarioClass="BODY_ROTATION", updateKind="BODY_ROTATION").__dict__
    with pytest.raises(ValueError): assert_semantically_comparable(left, right)


def test_pair_id_stable():
    assert pair_id(config().__dict__) == pair_id(config().__dict__)
