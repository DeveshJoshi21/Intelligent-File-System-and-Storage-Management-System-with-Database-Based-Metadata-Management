import sqlite3
from flask import current_app,g
SCHEMA="""
CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY,absolute_path TEXT UNIQUE NOT NULL,filename TEXT NOT NULL,extension TEXT NOT NULL DEFAULT '',size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),created_at TEXT,modified_at TEXT,scanned_at TEXT NOT NULL,content_hash TEXT,hash_checked_at TEXT);
CREATE INDEX IF NOT EXISTS ix_filename ON files(filename);
CREATE INDEX IF NOT EXISTS ix_extension ON files(extension);
CREATE INDEX IF NOT EXISTS ix_size ON files(size_bytes);
CREATE INDEX IF NOT EXISTS ix_hash ON files(content_hash);
CREATE TABLE IF NOT EXISTS scan_jobs(id INTEGER PRIMARY KEY,root_path TEXT NOT NULL,started_at TEXT NOT NULL,completed_at TEXT,files_seen INTEGER DEFAULT 0,status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY,action TEXT NOT NULL,details TEXT NOT NULL,created_at TEXT NOT NULL);
"""
def get_db():
 if "db" not in g:
  g.db=sqlite3.connect(current_app.config["DATABASE"]); g.db.row_factory=sqlite3.Row
 return g.db
def close_db(_=None):
 db=g.pop("db",None)
 if db: db.close()
def init_db(app):
 with app.app_context():
  db=sqlite3.connect(app.config["DATABASE"]); db.executescript(SCHEMA); db.commit(); db.close()
 app.teardown_appcontext(close_db)
