import hashlib

from epoch_auth_r3.serialization.jcs_adapter import canonicalize


def pair_id(config: dict) -> str:
    keys = ("workloadId", "seed", "bodySizeBytes", "recipientCount", "affectedResourceCount",
            "scenarioClass")
    if config.get("scenarioClass") not in {"HEADER_ONLY", "BODY_ROTATION", "STORAGE", "FAULT"}:
        raise ValueError("UNKNOWN_SCENARIO_CLASS")
    return hashlib.sha256(b"EPOCH_AUTH_R3_I9_PAIR_V1\x00" +
                          canonicalize({k: config[k] for k in keys})).hexdigest()


def assert_semantically_comparable(left: dict, right: dict) -> None:
    if {left["scenarioClass"], right["scenarioClass"]} == {"HEADER_ONLY", "BODY_ROTATION"}:
        raise ValueError("NONCOMPARABLE_SEMANTICS")
