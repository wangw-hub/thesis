# Gate sequencing

The sequence is execution completion → raw SHA and strict evidence validation → `P9AAcceptanceDecisionV1.evaluate()` → terminalizer atomic write. A8/business completion alone cannot write `P9_A_PASSED`. Local and remote gate artifacts derive from the same serialized decision.
