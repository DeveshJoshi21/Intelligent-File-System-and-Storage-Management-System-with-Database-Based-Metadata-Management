# IntelliFS — Intelligent File System and Storage Management System

This release keeps your original CLI/core modules and adds a browser-based GUI using Python, Flask and SQLite.

## Run on Windows
1. Install Python 3.10+.
2. Extract this ZIP and open Command Prompt in `intelligent_file_system`.
3. Run `py -m venv .venv`
4. Run `.venv\Scripts\activate`
5. Run `py -m pip install -r requirements.txt`
6. Run `py run.py`
7. Open `http://127.0.0.1:5000`.

You can also double-click `START_WINDOWS.bat` (it creates the venv, installs Flask, and launches the app).

## Modules
- Dashboard: indexed file count, logical storage, extension breakdown and scan history.
- File explorer: filename, extension and size filters.
- Scanner: recursive read-only metadata indexing with SQLite UPSERT on absolute path.
- Duplicate analysis: SHA-256 hashing and duplicate groups.
- Storage lab: fixed-size block allocation and internal-fragmentation estimate.
- SQLite tables: files, scan_jobs, audit_log; indexes on common search fields.
- Original CLI, core services, docs and tests are retained.

## Tests
`py -m unittest discover -s tests -v`

## OS/DBMS concepts for viva
- Directory traversal and metadata: `os.walk`, `os.stat`.
- Allocation estimate: `ceil(file_size / block_size)` blocks per file.
- Internal fragmentation: allocated bytes minus logical bytes.
- DBMS: primary key, UNIQUE path, CHECK constraint, indexes, transactions and UPSERT.
- Hashing: SHA-256 compares contents; equal file size alone is not proof of duplication.
- Scan history and audit log record operations.

## Scope and safety
Scanning is read-only: this app never moves, renames or deletes files. The Storage Lab is an educational simulation, not physical disk telemetry; it does not inspect real filesystem block maps, free-space bitmaps, inodes or disk scheduling. Start with a small folder. Hashing reads file contents and may take time on large folders. This is designed for localhost, not public deployment.
