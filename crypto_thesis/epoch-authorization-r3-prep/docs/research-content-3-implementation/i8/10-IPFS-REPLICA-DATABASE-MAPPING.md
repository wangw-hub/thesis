# Replica database mapping

Migration `0012_i8_storage_replica.sql` adds append-only replica metadata under `r3_control`, with one replica per object/backend and strict pin/verification constraints.
