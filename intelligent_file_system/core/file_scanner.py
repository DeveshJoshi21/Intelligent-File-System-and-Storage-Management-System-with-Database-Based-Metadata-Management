"""Read-only recursive filesystem scanner."""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


def utc_now() -> str:
    """Return UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def timestamp_or_none(value: float | None) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(value, timezone.utc).isoformat(timespec="seconds")
    except (OverflowError, OSError, ValueError):
        return None


def normalize_path(path: Path) -> str:
    # resolve(strict=False) gives a stable absolute path even for some unusual paths.
    return str(path.expanduser().resolve(strict=False))


class FileScanner:
    """Collect metadata without opening or modifying file contents."""

    def scan(self, folder: str | Path) -> tuple[list[dict], list[str]]:
        root = Path(folder).expanduser()
        if not root.exists():
            raise FileNotFoundError(f"Folder does not exist: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Path is not a folder: {root}")

        records: list[dict] = []
        errors: list[str] = []
        scan_time = utc_now()

        def on_walk_error(error: OSError) -> None:
            errors.append(f"{getattr(error, 'filename', 'folder')}: {error}")

        # os.walk exposes an onerror callback, allowing permission errors to be reported
        # while continuing to scan accessible directories.
        for current, directories, filenames in os.walk(root, onerror=on_walk_error):
            directories[:] = sorted(d for d in directories if d not in {".git", "__pycache__"})
            for filename in sorted(filenames):
                path = Path(current) / filename
                try:
                    # stat follows normal filesystem semantics; it does not read file data.
                    info = path.stat()
                    if not path.is_file():
                        continue
                    records.append({
                        "absolute_path": normalize_path(path),
                        "filename": path.name,
                        "extension": path.suffix.lower() or "[no extension]",
                        "size_bytes": int(info.st_size),
                        "created_at": timestamp_or_none(getattr(info, "st_birthtime", None)),
                        "modified_at": timestamp_or_none(info.st_mtime),
                        "scanned_at": scan_time,
                    })
                except (OSError, PermissionError) as exc:
                    errors.append(f"{path}: {exc}")
        return records, errors
