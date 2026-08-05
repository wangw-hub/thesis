# IpfsReplicaGatewayV1

Replication reads a verified local object, adds it with the frozen profile, reads it back exactly, validates the object format, confirms pinning, then emits the replica record. Fetch and restore fail closed.
