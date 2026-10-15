import tempfile
import unittest
from pathlib import Path

from database.db_manager import DatabaseManager
from core.search_service import SearchService


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = DatabaseManager(Path(self.temp.name) / "test.sqlite3")
        self.db.upsert_many([
            {"absolute_path": "/tmp/report.pdf", "filename": "report.pdf", "extension": ".pdf",
             "size_bytes": 120, "created_at": None, "modified_at": "2026-05-10T12:00:00+00:00",
             "scanned_at": "2026-05-11T00:00:00+00:00"},
            {"absolute_path": "/tmp/photo.jpg", "filename": "photo.jpg", "extension": ".jpg",
             "size_bytes": 800, "created_at": None, "modified_at": "2026-06-10T12:00:00+00:00",
             "scanned_at": "2026-06-11T00:00:00+00:00"},
        ])
        self.search = SearchService(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_filename_and_extension_filter(self):
        rows = self.search.search(filename="REPORT", extension="pdf")
        self.assertEqual([row["filename"] for row in rows], ["report.pdf"])

    def test_size_filter(self):
        rows = self.search.search(min_size=100, max_size=200)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["size_bytes"], 120)

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            self.search.search(modified_from="10/05/2026")


if __name__ == "__main__":
    unittest.main()
