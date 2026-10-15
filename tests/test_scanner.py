import tempfile
import unittest
from pathlib import Path

from core.file_scanner import FileScanner


class ScannerTests(unittest.TestCase):
    def test_scan_finds_nested_file_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested = root / "nested"
            nested.mkdir()
            target = nested / "hello.txt"
            target.write_text("hello", encoding="utf-8")
            records, errors = FileScanner().scan(root)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["filename"], "hello.txt")
            self.assertEqual(records[0]["size_bytes"], 5)
            self.assertTrue(Path(records[0]["absolute_path"]).is_absolute())
            self.assertIsInstance(errors, list)

    def test_missing_folder_raises(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"
            with self.assertRaises(FileNotFoundError):
                FileScanner().scan(missing)


if __name__ == "__main__":
    unittest.main()
