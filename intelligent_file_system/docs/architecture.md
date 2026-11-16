# Updated architecture
Browser → Flask routes → service layer → SQLite. The scanner uses os.walk/os.stat in read-only mode. Services handle scan, search, hashing and reports. SQLite persists metadata, scan history and audit events.
