# Intelligent File System and Storage Management System

## Purpose and limitations
This beginner-friendly Python mini-project recursively scans a folder, records file metadata in SQLite, supports search/filtering, and produces storage reports. It demonstrates OS and DBMS concepts at the **application level**. It does **not** implement or replace an OS kernel or filesystem, allocate real disk blocks, or move/rename/delete user files.

## Features
- Recursively scan a user-provided folder.
- Record normalized absolute path, filename, extension, size in bytes, available creation/birth time, modified time, and scan time.
- Store metadata in SQLite with a unique path and indexes.
- Rescan and update existing rows instead of duplicating a path.
- Search by filename, extension, size range, and modified-date range.
- Show indexed file count, total bytes, storage by extension, and largest files.
- Find duplicate-content groups: size narrows candidates, then SHA-256 is calculated on demand. Matching hashes strongly indicate matching content.
- Graceful handling of missing paths, scan permission errors, invalid input, and database errors.
- File operations are read-only; duplicate detection never deletes anything.

## Prerequisites
- Python 3.10+ (the code uses modern type annotations and dictionary union syntax).
- No third-party packages. `requirements.txt` is intentionally empty of dependencies because SQLite and all other modules are built into Python.

Check Python:
```bash
python --version
```

## Exact setup and run commands
Open a terminal in the `intelligent_file_system/` project root:

```bash
python -m venv .venv
```

Activate the environment:
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- Windows Command Prompt: `.venv\\Scripts\\activate.bat`
- macOS/Linux: `source .venv/bin/activate`

Then run:
```bash
python -m pip install -r requirements.txt
python main.py
```

Run automated tests:
```bash
python -m unittest discover -s tests -v
```

## Database initialization behavior
On startup, `DatabaseManager` creates `intelligent_file_system.sqlite3` in the project root if it does not exist, then executes `database/schema.sql`. `CREATE TABLE/INDEX IF NOT EXISTS` makes initialization safe to repeat. The database file is ignored by Git. Existing rows are preserved between launches.

## Quick demo walkthrough
1. Create the demo folder/files using the command in [`sample_data/README.md`](sample_data/README.md).
2. Run `python main.py`.
3. Choose `1` and enter `demo_files`.
4. Choose `3` for a storage report.
5. Choose `2`, enter `notes` for filename, and leave other filters blank.
6. Choose `1` and rescan `demo_files`; existing paths update rather than duplicate.
7. Choose `4` to find the identical `notes.txt` and `report.txt` contents.
8. Choose `0` to exit.

## Sample CLI interaction
```text
=== Intelligent File System and Storage Management ===
1. Scan / rescan a folder
2. Search and filter indexed files
3. Storage summary
4. Find duplicate-content files
5. Show database path
0. Exit
Choose an option: 1
Folder path to scan: demo_files
Files scanned: 3
Records inserted or updated: 3
Scan warnings/errors: 0
```
The counts above illustrate the expected interaction for the provided demo files; filesystem behavior can vary. Scanning again should not increase the row count for the same paths.

## Team member contribution division
1. **Student 1:** file scanning, initial schema, and insert operations.
2. **Student 2:** rescan/upsert logic, DB constraints, transactions, and indexes.
3. **Student 3:** search/filter operations and safe filesystem metadata/error handling.
4. **Student 4:** storage reports, CLI integration, and automated testing.

See [`docs/architecture.md`](docs/architecture.md) for module responsibilities and data flow.

## OS concepts used
- Directory traversal and path normalization.
- Filesystem metadata from `stat` (`st_size`, `st_mtime`, optional `st_birthtime`).
- File read access for optional content hashing.
- Handling inaccessible directories/files without aborting all work.

The scanner uses `pathlib` for path manipulation and `os.walk` because it provides recursive traversal and an `onerror` callback. `Path.stat()` reads metadata. SHA-256 hashing opens only candidate files in binary read mode and reads them in chunks.

## DBMS concepts used
- Relational table and typed columns.
- Primary key and unique constraint.
- Check constraint for nonnegative size.
- Indexes for common search fields.
- Transactions and conflict-handling upserts.
- Parameterized SQL and aggregate queries (`COUNT`, `SUM`, `GROUP BY`).

## Timestamp and duplicate details
Dates are stored as UTC ISO 8601 strings with `+00:00`. The scan time is the time the metadata snapshot was taken. Creation/birth time is stored only when `st_birthtime` is available; it may be `NULL` on Windows/Linux or other platforms where that attribute is not exposed in this form. Modified time uses `st_mtime`.

Equal file size only indicates a duplicate candidate. On request, same-size groups are hashed using SHA-256. Matching hashes are strong evidence of matching contents. Hashing reads candidate contents and can take time for large files.

## Known limitations and future improvements
- The app does not remove database rows for files that have since been deleted or moved. A future version could add a safe, explicit stale-record reconciliation report.
- Symlinks follow standard `Path.stat()`/`is_file()` behavior and are not specially deduplicated by inode.
- Date filtering accepts `YYYY-MM-DD`; time-of-day input is not supported.
- Very large folders may take time to scan, and duplicate hashing may be I/O intensive.
- Future work could include pagination, export to CSV, configurable database location, richer progress reporting, or a GUI.
