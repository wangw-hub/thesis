# Revision 8 Canary Result

`CANARY_PASSED`.

Exactly one Canary was planned and executed. Its two planned isolated-chain transactions both succeeded. `JOB_CREATE` was committed and independently visible before admission; chain writes before admission were zero; `DATABASE_FINALIZE` committed the job after receipt and fixed-block CompositeState verification.

- register tx: `190ea922929f3232dfaeb2dbf8e316c93ac53f0206163112af218532ede2783f`, block 13949
- anchor tx: `7c9f4f425317289d19ea41fab884ebb6c557fc158eebbbc0dab224b891c23fb8`, block 13950
- CompositeState block: 13950
- Header digest: `cb4dcb0524b66e0a5675886abcc2bafbeb7ed6a588bdb1268174d3f854dee33e`
- Body object digest: `948006d5ab1e3e3ef1448ebf76679288b4ab419d28d8187ff259f66d6979dad5`

No automatic retry occurred.
