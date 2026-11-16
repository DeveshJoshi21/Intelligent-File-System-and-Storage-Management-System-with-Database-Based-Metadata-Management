"""Beginner-friendly text menu."""
from pathlib import Path

from config import DEFAULT_DATABASE
from database.db_manager import DatabaseManager
from core.metadata_indexer import MetadataIndexer
from core.search_service import SearchService
from core.storage_analyzer import StorageAnalyzer, human_size


def _show_rows(rows) -> None:
    if not rows:
        print("No matching indexed files.")
        return
    for row in rows:
        print(f"- {row['filename']} | {human_size(row['size_bytes'])} | {row['extension']}")
        print(f"  {row['absolute_path']}")


def run_menu() -> None:
    try:
        db = DatabaseManager(DEFAULT_DATABASE)
    except RuntimeError as exc:
        print(exc)
        return
    indexer = MetadataIndexer(db)
    search = SearchService(db)
    analyzer = StorageAnalyzer(db)

    while True:
        print("\\n=== Intelligent File System and Storage Management ===")
        print("1. Scan / rescan a folder")
        print("2. Search and filter indexed files")
        print("3. Storage summary")
        print("4. Find duplicate-content files")
        print("5. Show database path")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                folder = input("Folder path to scan: ").strip().strip('"')
                result = indexer.index_folder(folder)
                print(f"Files scanned: {result['scanned']}")
                print(f"Records inserted or updated: {result['saved_or_updated']}")
                print(f"Scan warnings/errors: {len(result['errors'])}")
                for error in result["errors"][:10]:
                    print("  Warning:", error)
                if len(result["errors"]) > 10:
                    print("  (Further warnings omitted from screen.)")
            elif choice == "2":
                filename = input("Filename contains (blank = any): ").strip()
                extension = input("Extension, e.g. .pdf (blank = any): ").strip()
                min_text = input("Minimum size in bytes (blank = any): ").strip()
                max_text = input("Maximum size in bytes (blank = any): ").strip()
                date_from = input("Modified from YYYY-MM-DD (blank = any): ").strip()
                date_to = input("Modified to YYYY-MM-DD (blank = any): ").strip()
                min_size = int(min_text) if min_text else None
                max_size = int(max_text) if max_text else None
                if min_size is not None and min_size < 0 or max_size is not None and max_size < 0:
                    raise ValueError("Size cannot be negative.")
                if min_size is not None and max_size is not None and min_size > max_size:
                    raise ValueError("Minimum size cannot exceed maximum size.")
                _show_rows(search.search(filename, extension, min_size, max_size, date_from, date_to))
            elif choice == "3":
                report = analyzer.summary()
                print(f"Indexed files: {report['file_count']}")
                print(f"Indexed storage: {human_size(report['total_bytes'])} ({report['total_bytes']} bytes)")
                print("\\nStorage by extension:")
                for row in report["by_extension"]:
                    print(f"  {row['extension']}: {row['file_count']} files, {human_size(row['total_bytes'])}")
                print("\\nLargest files:")
                _show_rows(report["largest"])
            elif choice == "4":
                print("Checking same-size candidates with SHA-256. This reads candidate files only.")
                duplicates = analyzer.find_duplicates()
                if not duplicates:
                    print("No matching-content duplicate groups found (or files could not be read).")
                for group in duplicates:
                    print(f"\\nMatching content, {human_size(group[0]['size_bytes'])}:")
                    for item in group:
                        print(" ", item["absolute_path"])
                    print("  SHA-256:", group[0]["content_hash"])
                print("No files were deleted or changed.")
            elif choice == "5":
                print(f"SQLite database: {Path(DEFAULT_DATABASE).resolve()}")
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Please choose one of the listed options.")
        except (ValueError, FileNotFoundError, NotADirectoryError, RuntimeError, OSError) as exc:
            print(f"Could not complete operation: {exc}")
