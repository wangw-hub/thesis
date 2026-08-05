# Resource Recipient Index

`resource_recipient_index` maps `(resourceId,userId)` to recipient key, user version, active state, and source Header digest. `resource_recipient_index_state` records `COMPLETE` or `INCOMPLETE`. The closure has two entries, one active legal recipient and one revoked recipient, bound to the current Header digest.
