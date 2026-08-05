# E1 raw data audit

- Formal configurations: 168
- Complete configurations: 168
- Missing configurations: 0
- Expected records: 15120
- Observed records: 15120
- Usable records: 15120
- Duplicate records: 0
- Missing metrics: 0
- Non-positive timings: 0
- Semantic errors: 0
- Failure records: 0
- Configuration hashes: 1
- Git commits: 1

No row was silently removed. No post-hoc outlier exclusion was applied; all
15,120 records are retained in the reported statistics. A stopped serial run
left one sample at 20/30 repeats; the frozen runner's unique-key resume
mechanism supplied exactly the missing 30 method-repeat rows. Four disjoint
remaining-data shards were run on fixed logical cores and merged without
duplicates. The pre-repair audit is retained as `audit_pre_repair.json`.
