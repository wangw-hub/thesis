# A7 fixture root cause

Root cause: Final A7 dropped the event-derived target versions between task planning and Header anchor construction. `_anchor` then supplied its legacy defaults `epoch=1,state_version=1`. No contract, ABI, event, resolver, database, chain or security defect was found.
