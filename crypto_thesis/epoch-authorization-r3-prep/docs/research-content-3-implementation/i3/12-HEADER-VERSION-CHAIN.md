# Header Version Chain

Version 1 requires `previousHeaderDigest=null`. Later versions require a normalized digest equal to the prior Header core digest and an exact Header-version increment. Tests reject missing links, wrong links, skipped versions and rollback to an older Header under a newer expected context.

This is local structural validation. I3 does not claim that the chain tip is globally authoritative; HeaderRegistry anchoring belongs to a later approved stage.

