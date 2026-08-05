# STRICT_ACCEPTANCE_REQUIREMENTS_MATRIX

All 16 decision requirements have a producer, serialized field, validator, decision input, and regression test: PLANNED_RUN_COUNT, ACTUAL_RUN_COUNT, VALID_RUN_COUNT, CLASSIFICATION, PHASE, RAW_SHA, MIRROR_SHA, DATABASE_INVARIANTS, CHAIN_INVARIANTS, MATERIAL_RELEASE, DUPLICATES, TRUE_SECRET, UNCLASSIFIED, FORMAL_MIX, FATAL, MAJOR.

Requirement count=16; missing producer=0; multiple authority=0; unclassified=0. Gate order is execution -> seal -> mirror -> strict/invariant validation -> `P9AAcceptanceDecisionV1` -> Gate.
