# Likely viva questions and concise answers

**1. What is the project?**  
An application-level file metadata indexer that stores filesystem metadata in SQLite and offers search and storage reports.

**2. Does it implement an operating system filesystem?**  
No. It uses the host OS filesystem APIs and does not implement a kernel, block allocator, or replacement filesystem.

**3. Which OS concepts are demonstrated?**  
Directory traversal, file metadata, paths, file size, timestamps, error handling, and read-only file access.

**4. Which DBMS concepts are demonstrated?**  
Relational tables, primary and unique keys, constraints, indexes, transactions, aggregate queries, and parameterized SQL.

**5. Why use the absolute path as a unique key?**  
It identifies the indexed path and prevents repeated scans from creating duplicate rows for that same normalized path.

**6. What does an upsert do?**  
It inserts a row when the path is new, or updates its metadata when that path already exists.

**7. Why use parameterized SQL?**  
It keeps user-provided values separate from SQL syntax and reduces SQL-injection risk.

**8. Why are indexes used?**  
They can speed up common filters and lookups, at the cost of extra storage and write work.

**9. Is equal file size proof of duplication?**  
No. It only identifies candidates. SHA-256 hashes are compared to identify matching content.

**10. What does a matching SHA-256 hash mean?**  
It is strong evidence that the file contents match, though hashes are not a mathematical proof against every possible collision.

**11. Why hash lazily?**  
Hashing every file on every scan can be expensive. The app hashes only same-size candidates when duplicate detection is requested.

**12. What happens if a file cannot be read?**  
The scanner reports a warning, or duplicate hashing skips the unreadable file rather than crashing the whole report.

**13. Why can creation time be missing?**  
Filesystem APIs vary by platform. `st_birthtime` is not universally available, so the field can be `NULL`.

**14. Are timestamps stored consistently?**  
Yes, available timestamps are stored as UTC ISO 8601 strings with an explicit offset.

**15. Does the program delete duplicate files?**  
No. It only reports likely identical content and never deletes, renames, or moves user files.

**16. What is a transaction?**  
A group of database operations treated as one unit; it commits together or rolls back on failure.

**17. What are limitations?**  
It indexes only folders the user chooses, does not automatically remove stale rows for files that were deleted after scanning, and may take time to hash large same-size candidates.

**18. How could it be improved?**  
Add an explicit stale-record reconciliation mode, pagination, configurable database location, background scanning, and a graphical interface.
