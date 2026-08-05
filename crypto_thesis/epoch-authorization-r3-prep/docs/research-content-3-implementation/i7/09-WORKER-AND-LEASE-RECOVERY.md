# Worker and Lease Recovery

Expired leases can be reclaimed through the I4 CAS rules. Stale workers cannot
commit. Repeated delivery does not create a second job or Header anchor.
Retries are finite and preserve the existing dead-letter boundary.
