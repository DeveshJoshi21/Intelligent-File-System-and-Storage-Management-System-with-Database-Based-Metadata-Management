"""SQLite connection, schema initialization, and transactional operations."""
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from config import DEFAULT_DATABASE, DATABASE_SCHEMA


class DatabaseManager:
    """Owns short-lived SQLite connections and keeps SQL parameterized."""

    def __init__(self, db_path: Path | str = DEFAULT_DATABASE):
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create tables/indexes on first run; safe to repeat."""
        try:
            schema = DATABASE_SCHEMA.read_text(encoding="utf-8")
            with self.connect() as connection:
                connection.executescript(schema)
        except (OSError, sqlite3.Error) as exc:
            raise RuntimeError(f"Could not initialize database: {exc}") from exc

    def upsert_file(self, record: dict) -> str:
        """Insert a path once, or refresh its metadata when rescanned."""
        sql = """
        INSERT INTO files (
            absolute_path, filename, extension, size_bytes, created_at,
            modified_at, scanned_at, content_hash, hash_checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)
        ON CONFLICT(absolute_path) DO UPDATE SET
            filename=excluded.filename,
            extension=excluded.extension,
            size_bytes=excluded.size_bytes,
            created_at=excluded.created_at,
            modified_at=excluded.modified_at,
            scanned_at=excluded.scanned_at,
            content_hash=CASE
                WHEN files.size_bytes != excluded.size_bytes
                  OR files.modified_at IS NOT excluded.modified_at
                THEN NULL ELSE files.content_hash END,
            hash_checked_at=CASE
                WHEN files.size_bytes != excluded.size_bytes
                  OR files.modified_at IS NOT excluded.modified_at
                THEN NULL ELSE files.hash_checked_at END
        """
        with self.connect() as connection:
            cursor = connection.execute(sql, (
                record["absolute_path"], record["filename"], record["extension"],
                record["size_bytes"], record["created_at"], record["modified_at"],
                record["scanned_at"],
            ))
            return "saved"

    def upsert_many(self, records: Iterable[dict]) -> int:
        count = 0
        sql = """
        INSERT INTO files (
            absolute_path, filename, extension, size_bytes, created_at,
            modified_at, scanned_at, content_hash, hash_checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)
        ON CONFLICT(absolute_path) DO UPDATE SET
            filename=excluded.filename, extension=excluded.extension,
            size_bytes=excluded.size_bytes, created_at=excluded.created_at,
            modified_at=excluded.modified_at, scanned_at=excluded.scanned_at,
            content_hash=CASE
                WHEN files.size_bytes != excluded.size_bytes
                  OR files.modified_at IS NOT excluded.modified_at
                THEN NULL ELSE files.content_hash END,
            hash_checked_at=CASE
                WHEN files.size_bytes != excluded.size_bytes
                  OR files.modified_at IS NOT excluded.modified_at
                THEN NULL ELSE files.hash_checked_at END
        """
        try:
            with self.connect() as connection:
                for record in records:
                    connection.execute(sql, (
                        record["absolute_path"], record["filename"], record["extension"],
                        record["size_bytes"], record["created_at"], record["modified_at"],
                        record["scanned_at"],
                    ))
                    count += 1
        except sqlite3.Error as exc:
            raise RuntimeError(f"Database write failed: {exc}") from exc
        return count

    def fetch_all(self, sql: str, parameters: tuple = ()) -> list[sqlite3.Row]:
        """Run a read query with parameters and return rows."""
        try:
            with self.connect() as connection:
                return connection.execute(sql, parameters).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Database query failed: {exc}") from exc

    def update_hash(self, absolute_path: str, content_hash: str, checked_at: str) -> None:
        try:
            with self.connect() as connection:
                connection.execute(
                    "UPDATE files SET content_hash = ?, hash_checked_at = ? WHERE absolute_path = ?",
                    (content_hash, checked_at, absolute_path),
                )
        except sqlite3.Error as exc:
            raise RuntimeError(f"Could not save content hash: {exc}") from exc

    def get_file(self, absolute_path: str) -> Optional[sqlite3.Row]:
        rows = self.fetch_all("SELECT * FROM files WHERE absolute_path = ?", (absolute_path,))
        return rows[0] if rows else None
