CREATE UNIQUE INDEX one_job_per_resource_target_header_version
 ON r3_control.header_update_job (resource_id, target_header_version);
