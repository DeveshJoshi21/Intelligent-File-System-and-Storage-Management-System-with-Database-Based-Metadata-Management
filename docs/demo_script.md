# Evaluator demo script (5–7 minutes)

1. From the project root, create sample data using the command in `sample_data/README.md`.
2. Start the app: `python main.py`.
3. Choose `1`, enter `demo_files`, and note scanned/inserted-or-updated counts.
4. Choose `3` to show total indexed files, bytes, extension grouping, and largest files.
5. Choose `2`; search filename `notes`, leave other filters blank, and show the matching path.
6. Choose `1` and scan `demo_files` again. Explain that the unique absolute path and SQLite upsert prevent duplicate rows.
7. Choose `4`. `notes.txt` and `report.txt` have identical content and size, so the app should report them after SHA-256 hashing. Explain that same size alone is not proof; matching hashes indicate matching content. No file is deleted.
8. Exit with `0`.
9. Run tests in a separate terminal: `python -m unittest discover -s tests -v`.

## What to point out
- Files are only scanned/read; no move, rename, or delete operations exist in the application.
- SQLite holds metadata, not copies of the user's files.
- Hashing is on-demand and only for same-size groups.
