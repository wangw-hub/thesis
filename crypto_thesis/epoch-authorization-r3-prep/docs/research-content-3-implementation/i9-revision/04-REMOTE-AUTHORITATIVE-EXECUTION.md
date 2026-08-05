# Remote authoritative execution

Authority is `EXPERIMENT_CLIENT_REMOTE_EXECUTION`.

The fixed root is `/var/lib/epoch-auth-r3/i9-pilot`.  Each attempt uses
`attempts/<attemptId>/{configs,workloads,raw,processed,logs,state,manifests,invalid-runs,local-store,runtime}`.
All measured phase events originate on `experiment-client`.  Windows never
provides the object root or phase clock and only launches bounded SSH commands
and verifies a sealed mirror.
