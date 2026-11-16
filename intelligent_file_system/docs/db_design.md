# Updated database design
files: one record per absolute path; UNIQUE absolute_path supports idempotent rescans. Indexed filename, extension, size and content_hash. scan_jobs records folder and scan outcome. audit_log records scan actions. CHECK(size_bytes>=0) enforces valid sizes.
