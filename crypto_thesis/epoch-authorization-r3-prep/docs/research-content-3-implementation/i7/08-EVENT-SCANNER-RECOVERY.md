# Event Scanner Recovery

Scanner restart resumes from the durable contiguous cursor. Event identity and
job insertion remain idempotent. A gap, block-hash conflict, or pruned historic
state halts automatic generation. Pruned events may support audit wording only;
they cannot synthesize current tasks.
