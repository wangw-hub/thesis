# Local restore from IPFS

Missing objects are restored through `LocalObjectStore.put` with expected digest. Corrupt local objects are quarantined first; atomic publication and final verification are mandatory.
