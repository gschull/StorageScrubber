# Storage Scrubber

A lightweight Python CLI to scan your filesystem, classify files (personal, temp, cache, updates), produce reports, and optionally move safe-to-delete files to the Recycle Bin.

Usage examples:

Scan current directory (dry-run):

    python scrubber.py . --dry-run

Scan and auto-clean (prompt before delete):

    python scrubber.py C:\Users\You\ --auto-clean

Auto-clean without prompt:

    python scrubber.py C:\Temp --auto-clean -y

Notes:
- This tool moves files to the Recycle Bin using send2trash. Install with `pip install -r requirements.txt`.
- Use `--min-size` and `--min-age` to narrow candidates.
- This is a first draft. Always review the report before deleting files.
