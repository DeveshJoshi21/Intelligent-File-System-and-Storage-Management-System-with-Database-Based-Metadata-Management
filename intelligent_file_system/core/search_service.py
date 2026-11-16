"""Safe metadata search and filtering."""
from datetime import datetime, timezone
from database.db_manager import DatabaseManager


class SearchService:
    def __init__(self, database: DatabaseManager):
        self.database = database

    def search(self, filename: str = "", extension: str = "",
               min_size: int | None = None, max_size: int | None = None,
               modified_from: str = "", modified_to: str = "") -> list:
        clauses = []
        params: list = []
        if filename.strip():
            clauses.append("filename LIKE ? COLLATE NOCASE")
            params.append(f"%{filename.strip()}%")
        if extension.strip():
            ext = extension.strip().lower()
            if not ext.startswith(".") and ext != "[no extension]":
                ext = "." + ext
            clauses.append("extension = ? COLLATE NOCASE")
            params.append(ext)
        if min_size is not None:
            clauses.append("size_bytes >= ?")
            params.append(min_size)
        if max_size is not None:
            clauses.append("size_bytes <= ?")
            params.append(max_size)
        if modified_from.strip():
            clauses.append("modified_at >= ?")
            params.append(_date_bound(modified_from, end=False))
        if modified_to.strip():
            clauses.append("modified_at <= ?")
            params.append(_date_bound(modified_to, end=True))

        sql = "SELECT * FROM files"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY filename COLLATE NOCASE"
        return self.database.fetch_all(sql, tuple(params))


def _date_bound(value: str, end: bool) -> str:
    """Accept YYYY-MM-DD; convert to ISO UTC range bounds."""
    try:
        date = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("Dates must use YYYY-MM-DD format.") from exc
    if end:
        date = date.replace(hour=23, minute=59, second=59)
    return date.isoformat(timespec="seconds")
