# Intelligent File System and Storage Management System

A college mini-project developed using **Python 3 and SQLite** that demonstrates Operating Systems and Database Management System (DBMS) concepts through an application-level file management tool.

### Key Features
- Recursive scanning of user-selected folders.
- File metadata collection and storage in SQLite.
- Automatic metadata updates when files are rescanned.
- Search and filtering by filename, extension, file size, and modification date.
- Storage analytics, including total indexed files, storage by extension, and largest files.
- SHA-256-based duplicate-content detection.
- Parameterized SQL queries, database constraints, indexes, and transaction handling.
- Automated unit tests using Python's built-in `unittest` framework.

### Technologies
- Python 3
- SQLite
- `pathlib`, `os`, `hashlib`, and `unittest`

### Academic Focus
This project demonstrates filesystem traversal, file metadata handling, relational database design, SQL queries, indexing, transactions, and safe data access.

**Note:** This is an application-level file management system. It uses the host operating system's filesystem APIs and does not replace or implement an operating system kernel or filesystem. It does not automatically move, rename, or delete user files.
