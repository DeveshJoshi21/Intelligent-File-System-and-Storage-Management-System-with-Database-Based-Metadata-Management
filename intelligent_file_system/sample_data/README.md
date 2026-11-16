# Sample data folder

The demo creates a temporary `demo_files/` folder in the project root with:
- `notes.txt`
- `report.txt` (same content as `notes.txt`, for duplicate detection)
- `images/pixel-info.csv`

Run these commands from the project root:

```bash
python -c "from pathlib import Path; p=Path('demo_files'); (p/'images').mkdir(parents=True, exist_ok=True); (p/'notes.txt').write_text('College mini project demo\\n', encoding='utf-8'); (p/'report.txt').write_text('College mini project demo\\n', encoding='utf-8'); (p/'images'/'pixel-info.csv').write_text('width,height\\n1,1\\n', encoding='utf-8')"
```

The application scans the folder read-only. The one-time command above creates demo files; the application itself never moves, renames, or deletes files. You can remove the demo folder manually after the demonstration if desired.
