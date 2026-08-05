from pathlib import Path
import json
import pytest

from epoch_auth_r3.pilot.bootstrap import AtomicJsonWriterV1, AttemptBootstrapManifestV1, BootstrapState
from epoch_auth_r3.pilot.database import (
    PilotApplicationNameV1, PilotDatabaseConfigV1,
    PilotDatabaseConnectionRoleV1, frozen_pilot_database_config,
)

def test_database_config_is_strict_and_never_5432():
    name=PilotApplicationNameV1.generate(
        attempt_id="test-attempt",run_identity="NO_RUN",
        role=PilotDatabaseConnectionRoleV1.BOOTSTRAP,software_commit="a"*40)
    config=frozen_pilot_database_config(name.value)
    assert config.port==55432
    value=config.redacted_dict(); value["port"]=5432
    with pytest.raises(ValueError): PilotDatabaseConfigV1.from_strict_dict(value)
    value=config.redacted_dict(); value.pop("port")
    with pytest.raises(ValueError): PilotDatabaseConfigV1.from_strict_dict(value)

def test_atomic_json_round_trip(tmp_path:Path):
    path=tmp_path/"value.json"; sha=AtomicJsonWriterV1.write(path,{"x":1})
    assert json.loads(path.read_text())=={"x":1} and len(sha)==64

def test_bootstrap_state_cannot_skip():
    m=AttemptBootstrapManifestV1(1,"a","p","c","a","e","d","da","w","wa","p","s","experiment-client","/var/lib/x","now",BootstrapState.PLANNED.value)
    with pytest.raises(ValueError): m.transition(BootstrapState.READY_FOR_CANARY)
    assert m.transition(BootstrapState.BOOTSTRAP_FAILED).bootstrapState=="BOOTSTRAP_FAILED"
