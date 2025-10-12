"""Bulk recycle (move to Recycle Bin) selected candidate paths for Storage Scrubber
This script is written to be run under PowerShell without heredocs: python scripts\bulk_recycle.py
"""
import os
import sys
from pathlib import Path

try:
    from send2trash import send2trash
except Exception:
    print('send2trash is required. Install with pip install send2trash', file=sys.stderr)
    sys.exit(2)

USER = os.environ.get('USERPROFILE') or os.environ.get('HOME')
if not USER:
    print('Cannot determine user profile path', file=sys.stderr)
    sys.exit(3)

candidates = [
    r"%USERPROFILE%\\.platformio\\packages",
    r"%USERPROFILE%\\.platformio\\.cache",
    r"%USERPROFILE%\\.platformio\\.cache\\downloads",
    r"%USERPROFILE%\\.cursor\\extensions",
    r"%USERPROFILE%\\AppData\\Local\\arduino-ide-updater",
    r"%USERPROFILE%\\AppData\\Local\\unityhub-updater",
    r"%USERPROFILE%\\AppData\\Local\\pip\\cache",
    r"%USERPROFILE%\\.nuget\\packages",
    r"%USERPROFILE%\\AppData\\Local\\Microsoft\\vscode-cpptools",
]

moved = []
failed = []

for p in candidates:
    expanded = os.path.expandvars(p)
    path = Path(expanded)
    if not path.exists():
        print('Not found:', expanded)
        continue
    try:
        send2trash(str(path))
        print('Moved to Recycle Bin:', expanded)
        moved.append(expanded)
    except Exception as e:
        print('Failed to move:', expanded, '->', e)
        failed.append((expanded, str(e)))

print('\nSummary:')
print('Moved count:', len(moved))
if moved:
    for m in moved:
        print('  ', m)
if failed:
    print('\nFailed:')
    for f, e in failed:
        print('  ', f, 'error:', e)

print('Done')
