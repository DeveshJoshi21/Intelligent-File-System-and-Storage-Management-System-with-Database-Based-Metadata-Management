"""Storage reports and lazy content hashing for duplicate candidates."""
import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from database.db_manager import DatabaseManager


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{size} B"
        value /= 1024
    return f"{size} B"


class StorageAnalyzer:
    def __init__(self, database: DatabaseManager):
        self.database = database

    def summary(self) -> dict:
        totals = self.database.fetch_all(
            "SELECT COUNT(*) AS file_count, COALESCE(SUM(size_bytes), 0) AS total_bytes FROM files"
        )[0]
        by_extension = self.database.fetch_all("""
            SELECT extension, COUNT(*) AS file_count, SUM(size_bytes) AS total_bytes
            FROM files GROUP BY extension ORDER BY total_bytes DESC
        """)
        largest = self.database.fetch_all(
            "SELECT filename, absolute_path, extension, size_bytes FROM files ORDER BY size_bytes DESC LIMIT 10"
        )
        return {"file_count": totals["file_count"], "total_bytes": totals["total_bytes"],
                "by_extension": by_extension, "largest": largest}

    def duplicate_candidates(self) -> list:
        # Size is a cheap first pass. Hashes are only computed for files in same-size groups.
        return self.database.fetch_all("""
            SELECT size_bytes, COUNT(*) AS file_count
            FROM files GROUP BY size_bytes HAVING COUNT(*) > 1 ORDER BY file_count DESC
        """)

    def find_duplicates(self) -> list[list[dict]]:
        groups = self.duplicate_candidates()
        duplicates: list[list[dict]] = []
        for group in groups:
            rows = self.database.fetch_all(
                "SELECT absolute_path, size_bytes, content_hash, modified_at FROM files WHERE size_bytes = ?",
                (group["size_bytes"],),
            )
            hashes: dict[str, list[dict]] = defaultdict(list)
            for row in rows:
                digest = row["content_hash"]
                if not digest or not row["modified_at"]:
                    digest = self._hash_file(row["absolute_path"])
                if digest:
                    hashes[digest].append(dict(row) | {"content_hash": digest})
            duplicates.extend(items for items in hashes.values() if len(items) > 1)
        return duplicates

    def _hash_file(self, absolute_path: str) -> str | None:
        path = Path(absolute_path)
        try:
            # Read in chunks to avoid loading large files fully into memory.
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            value = digest.hexdigest()
            self.database.update_hash(absolute_path, value, _now())
            return value
        except (OSError, PermissionError):
            return None
