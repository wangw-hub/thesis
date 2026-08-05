# I7 Entry Audit

- Entry HEAD: `128b585e60bcd71023b5f83224d19aed65651f7d`
- Entry state: `I6_COMPLETED_AWAITING_I7_APPROVAL`
- I6 regressions: I1 49/49, I2 49/49, I3 54/54, I4 55/55, I5 33/33, I6 50/50.
- I6 artifact hash errors: 0.
- Authorized scope: I7 only. I8 is not approved.
- Main repository: read-only and unchanged.
- Admission decision: **PASSED**.

The I6 Bonsai-pruned historic-state issue is retained as
`ACCEPTED_LIMITATION_WITH_WORDING`: pruned events are audit-only and cannot
create recovery work. Recovery begins at a retained safe checkpoint or a
trusted snapshot.
