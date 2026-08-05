from types import SimpleNamespace

import pytest

from epoch_auth_r3.blockchain import CompositeConsistencyClass
from scripts.r3_i9.run_revised_remote_pilot import (
    MemoryEventRepository, final_a6_evidence, final_a8_evidence,
)
from epoch_auth_r3.storage import LocalObjectStore, ObjectKind


def test_final_a6_preserves_both_states_and_denies_old_header_release():
    state = SimpleNamespace(
        authorization_present=True,
        header_present=True,
        consistency_class=CompositeConsistencyClass.AUTHORIZATION_AHEAD_OF_HEADER,
    )
    evidence = final_a6_evidence(state, header_object_valid=True)
    assert evidence == {
        "authorizationPresent": True,
        "headerPresent": True,
        "consistencyClass": "AUTHORIZATION_AHEAD_OF_HEADER",
        "materialRelease": "DENIED",
        "reasonCode": "HEADER_UPDATE_PENDING",
        "oldHeaderUsableForRelease": False,
    }


def test_final_a6_rejects_missing_or_consistent_state():
    state = SimpleNamespace(
        authorization_present=False,
        header_present=True,
        consistency_class=CompositeConsistencyClass.HEADER_ONLY,
    )
    with pytest.raises(RuntimeError, match="A6_FAIL_CLOSED"):
        final_a6_evidence(state, header_object_valid=True)


def test_final_a7_repository_is_idempotent():
    event = SimpleNamespace(identity=(1, "a", "b", 0))
    repository = MemoryEventRepository()
    assert repository.insert(event)[1] is True
    assert repository.insert(event)[1] is False
    assert len(repository.events) == 1


def test_final_a8_consistent_path_has_zero_repairs():
    evidence = final_a8_evidence("a" * 64)
    assert evidence["recoveryDisposition"] == "CONSISTENT"
    assert evidence["materialRelease"] == "ALLOWED"
    assert sum(
        evidence[key] for key in (
            "automaticRecoveries", "manualInterventions", "irrecoverable",
            "databaseRepairWrites", "chainRepairWrites", "objectRestores",
        )
    ) == 0


def test_final_a5_controlled_delete_requires_verified_object(tmp_path):
    store = LocalObjectStore(tmp_path)
    ref = store.put(b"body", namespace="pilot", object_kind=ObjectKind.BODY)
    store.controlled_delete_for_recovery_test(ref)
    assert not store.exists(ref)
    with pytest.raises(Exception, match="CONTROLLED_DELETE_REQUIRES_VERIFIED"):
        store.controlled_delete_for_recovery_test(ref)
