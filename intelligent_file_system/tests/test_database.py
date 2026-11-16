import tempfile
import unittest
from pathlib import Path

from database.db_manager import DatabaseManager


def record(path: Path, size: int = 5) -> dict:
    return {
        "absolute_path": str(path.resolve()), "filename": path.name,
        "extension": path.suffix.lower() or "[no extension]", "size_bytes": size,
        "created_at": None, "modified_at": "2026-01-01T00:00:00+00:00",
        "scanned_at": "2026-01-02T00:00:00+00:00",
    }


class DatabaseTests(unittest.TestCase):
    def test_upsert_does_not_duplicate_path(self):
        with tempfile.TemporaryDirectory() as temp:
            db = DatabaseManager(Path(temp) / "test.sqlite3")
            path = Path(temp) / "example.txt"
            db.upsert_many([record(path, 5)])
            db.upsert_many([record(path, 9)])
            rows = db.fetch_all("SELECT * FROM files")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["size_bytes"], 9)

    def test_schema_has_indexes(self):
        with tempfile.TemporaryDirectory() as temp:
            db = DatabaseManager(Path(temp) / "test.sqlite3")
            indexes = db.fetch_all("SELECT name FROM sqlite_master WHERE type='index'")
            self.assertTrue(any(row["name"] == "idx_files_size" for row in indexes))


if __name__ == "__main__":
    unittest.main()
