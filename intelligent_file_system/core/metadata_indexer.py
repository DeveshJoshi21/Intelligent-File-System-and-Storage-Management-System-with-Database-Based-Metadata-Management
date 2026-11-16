"""Coordinates scanning and storing metadata."""
from pathlib import Path

from core.file_scanner import FileScanner
from database.db_manager import DatabaseManager


class MetadataIndexer:
    def __init__(self, database: DatabaseManager, scanner: FileScanner | None = None):
        self.database = database
        self.scanner = scanner or FileScanner()

    def index_folder(self, folder: str | Path) -> dict:
        records, errors = self.scanner.scan(folder)
        saved = self.database.upsert_many(records)
        return {"scanned": len(records), "saved_or_updated": saved, "errors": errors}
