# Application-name truncation root cause

Revision 6 generated the Canary name as:

`epoch-auth-r3-i9-pilot-canary-` + the complete attempt ID.

The exact expected value was
`epoch-auth-r3-i9-pilot-canary-I9_REVISION_6_20260730T141500Z_8fc5f44`:
68 ASCII characters and 68 UTF-8 bytes. PostgreSQL retained only its first 63
bytes, producing a 63-character server value. The difference began at byte 64.
The Bootstrap value omitted the extra `canary-` component and therefore happened
to fit at 61 bytes; that accidental success did not establish a
safe naming rule.

The old configuration embedded the full attempt ID and the Canary path added a
free-form component prefix. It did not embed the run ID. Environment and DSN
override paths were not used by the frozen factory. The factory rejected the
server truncation, correctly failing before the database insert and before any
chain transaction, but its previous `contains` comparison was itself too weak
and has now been replaced by exact three-source attestation.
