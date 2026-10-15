-- SQLite schema for indexed filesystem metadata.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    absolute_path TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    extension TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    created_at TEXT,
    modified_at TEXT,
    scanned_at TEXT NOT NULL,
    content_hash TEXT,
    hash_checked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_files_size ON files(size_bytes);
CREATE INDEX IF NOT EXISTS idx_files_modified_at ON files(modified_at);
CREATE INDEX IF NOT EXISTS idx_files_content_hash ON files(content_hash);
