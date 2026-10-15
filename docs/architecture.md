# Architecture and team responsibilities

## Scope
This is an application-level metadata indexer. It scans folders through Python's filesystem APIs and records metadata in SQLite. It does not implement a kernel, mount a filesystem, allocate physical disk blocks, or replace the host operating system.

## Data flow
1. `cli/menu.py` accepts user input and displays reports.
2. `core/file_scanner.py` recursively enumerates files and reads metadata using `pathlib`, `os.walk`, and `Path.stat()`.
3. `core/metadata_indexer.py` passes scanner records to the database layer.
4. `database/db_manager.py` initializes schema, uses parameterized SQL, and commits batches in transactions.
5. `core/search_service.py` builds filters from fixed SQL clauses and bound parameter values.
6. `core/storage_analyzer.py` aggregates indexed metadata and computes SHA-256 only for same-size candidates when duplicate detection is requested.

## Modules
- `config.py`: project and database paths.
- `database/schema.sql`: tables, constraints, and indexes.
- `database/db_manager.py`: connections, initialization, upserts, and query helpers.
- `core/file_scanner.py`: read-only filesystem metadata scan and warning collection.
- `core/metadata_indexer.py`: scan-to-index coordination.
- `core/search_service.py`: filename, extension, size, and date filters.
- `core/storage_analyzer.py`: totals, extension grouping, largest files, duplicate checks.
- `cli/menu.py`: menu-driven interface and input validation.
- `tests/`: automated checks using `unittest`.

## Team contribution plan
1. **Student 1 — scanning + initial DB schema/inserts:** `core/file_scanner.py`, `database/schema.sql`, initial insert behavior in `database/db_manager.py`.
2. **Student 2 — rescan/update + DBMS integrity:** upsert conflict handling, transaction behavior, constraints and indexes in `database/db_manager.py` and `database/schema.sql`.
3. **Student 3 — search + safe metadata handling:** `core/search_service.py` and filesystem error/timestamp handling in `core/file_scanner.py`.
4. **Student 4 — reports + integration/testing:** `core/storage_analyzer.py`, `cli/menu.py`, and tests/docs integration.

Each member should review the complete project and be ready to explain how their module interacts with the rest.
