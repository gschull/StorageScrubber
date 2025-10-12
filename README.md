# Storage Scrubber

A lightweight Python CLI to scan your filesystem, classify files (personal, temp, cache, updates), produce JSON reports, and optionally move safe-to-delete files to the Recycle Bin.

Features
- Recursive scanning with configurable minimum size and age filters
- Heuristics to classify files (cache, temp, installers, personal)
- Duplicate detection (optional, by SHA-256)
- Safe deletion via Recycle Bin (send2trash) with interactive or non-interactive modes
- JSON reports and helper scripts for PowerShell-friendly batch cleanup

Quick start
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run a dry-run scan of your user profile for files >1MB and older than 7 days:

```powershell
python .\scrubber.py "%USERPROFILE%" --dry-run --min-size 1048576 --min-age 7 --report-json report-userprofile.json
```

4. Review `report-userprofile.json` (or use the included scripts in `scripts/` to analyze and prepare cleanup batches).

Safety notes
- By default deletions use the Recycle Bin (send2trash). Permanently deleting files is irreversible.
- Always review reports before running auto-clean.

Included helper scripts (in `scripts/`)
- `analyze_report.py` — print top N largest items in a report and suggested groups
- `prepare_cleanup_batch.py` — prepare `cleanup_candidates.json` with safe-first candidates
- `execute_cleanup_batch.py` — move top-N candidate files to Recycle Bin (PowerShell-friendly)
- `execute_cleanup_dirs.py` — move whole cache/extension directories to Recycle Bin
- `bulk_recycle.py` — earlier PowerShell-friendly batch mover

Contributing
- See `CONTRIBUTING.md` for how to run tests and propose changes.

License
- This project is licensed under the MIT License (see `LICENSE`).
