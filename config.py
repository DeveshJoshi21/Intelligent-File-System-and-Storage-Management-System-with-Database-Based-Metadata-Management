"""Application configuration."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE = PROJECT_ROOT / "intelligent_file_system.sqlite3"
DATABASE_SCHEMA = PROJECT_ROOT / "database" / "schema.sql"
