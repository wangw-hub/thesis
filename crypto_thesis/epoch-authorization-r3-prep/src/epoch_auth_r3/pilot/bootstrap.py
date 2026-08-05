"""Atomic, secret-free bootstrap for an I9 attempt directory."""
from __future__ import annotations
import hashlib, json, os, socket, tempfile
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

class AtomicJsonWriterV1:
    @staticmethod
    def write(path: Path, value: dict) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(payload); out.flush(); os.fsync(out.fileno())
            if json.loads(Path(temp).read_text("utf-8")) != value: raise ValueError("ATOMIC_JSON_ROUNDTRIP_FAILED")
            os.replace(temp, path)
            with path.open("rb") as final:
                if hashlib.sha256(final.read()).hexdigest() != hashlib.sha256(payload).hexdigest():
                    raise ValueError("ATOMIC_JSON_FINAL_SHA_MISMATCH")
            try:
                directory = os.open(path.parent, os.O_RDONLY)
                try: os.fsync(directory)
                finally: os.close(directory)
            except OSError:
                pass
            return hashlib.sha256(payload).hexdigest()
        except Exception:
            Path(temp).unlink(missing_ok=True); raise

def strict_pilot_database_config() -> dict:
    return {"schemaVersion":1,"host":"127.0.0.1","port":55432,"database":"epoch_auth_r3_i9_pilot","user":"epoch_auth_r3_i9_pilot","connectTimeoutSeconds":5,"applicationName":"epoch-auth-r3-i9-pilot","sslMode":"disable","credentialSource":"external_file","expectedClusterName":"16/r3_i4","expectedServerVersionMajor":16}

class BootstrapState(str, Enum):
    PLANNED="PLANNED"; STAGING_CREATED="STAGING_CREATED"; CONFIG_WRITTEN="CONFIG_WRITTEN"
    CONFIG_VALIDATED="CONFIG_VALIDATED"; DATABASE_ATTESTED="DATABASE_ATTESTED"; WEB3_ATTESTED="WEB3_ATTESTED"
    PREFLIGHT_COMPLETED="PREFLIGHT_COMPLETED"; READY_FOR_CANARY="READY_FOR_CANARY"
    BOOTSTRAP_FAILED="BOOTSTRAP_FAILED"; PUBLISHED="PUBLISHED"

_NEXT = {BootstrapState.PLANNED:BootstrapState.STAGING_CREATED,
 BootstrapState.STAGING_CREATED:BootstrapState.CONFIG_WRITTEN,
 BootstrapState.CONFIG_WRITTEN:BootstrapState.CONFIG_VALIDATED,
 BootstrapState.CONFIG_VALIDATED:BootstrapState.DATABASE_ATTESTED,
 BootstrapState.DATABASE_ATTESTED:BootstrapState.WEB3_ATTESTED,
 BootstrapState.WEB3_ATTESTED:BootstrapState.PREFLIGHT_COMPLETED,
 BootstrapState.PREFLIGHT_COMPLETED:BootstrapState.READY_FOR_CANARY,
 BootstrapState.READY_FOR_CANARY:BootstrapState.PUBLISHED}

@dataclass(frozen=True)
class AttemptBootstrapManifestV1:
    schemaVersion:int; attemptId:str; attemptPurpose:str; softwareCommit:str; remoteArchiveSha256:str
    environmentManifestDigest:str; databaseConfigDigest:str; databaseAttestationDigest:str
    web3ConfigDigest:str; web3AttestationDigest:str; phaseContractDigest:str; stageGateDigest:str
    remoteExecutionHost:str; remoteAttemptRoot:str; createdAt:str; bootstrapState:str
    def transition(self, target: BootstrapState):
        current=BootstrapState(self.bootstrapState)
        if target is BootstrapState.BOOTSTRAP_FAILED: return replace(self,bootstrapState=target.value)
        if _NEXT.get(current) is not target: raise ValueError("ILLEGAL_BOOTSTRAP_STATE_TRANSITION")
        return replace(self,bootstrapState=target.value)

class AttemptBootstrapLockV1:
    def __init__(self,path:Path,attempt_id:str,software_commit:str): self.path=path; self.data={"attemptId":attempt_id,"ownerProcessId":os.getpid(),"executionHost":socket.gethostname(),"softwareCommit":software_commit,"acquiredAt":datetime.now(timezone.utc).isoformat()}
    def __enter__(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(self.path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); os.write(fd,json.dumps(self.data,sort_keys=True).encode()); os.fsync(fd); os.close(fd); return self
    def __exit__(self,*args): self.path.unlink()
