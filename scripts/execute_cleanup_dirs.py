"""Move common cache/extension directories to Recycle Bin (safer: directory-level).
Targets are derived from cleanup_candidates.json but hard-coded common directories for Windows user profile.
Run in PowerShell: python .\scripts\execute_cleanup_dirs.py
"""
import os
import json
from pathlib import Path
import sys

try:
    from send2trash import send2trash
except Exception:
    print('send2trash required', file=sys.stderr)
    sys.exit(2)

USER = os.environ.get('USERPROFILE')
if not USER:
    print('Cannot determine USERPROFILE', file=sys.stderr)
    sys.exit(3)

candidates_dirs = [
    os.path.join(USER, '.cache'),
    os.path.join(USER, '.wdm', 'drivers'),
    os.path.join(USER, '.platformio', '.cache'),
    os.path.join(USER, '.platformio', 'packages'),
    os.path.join(USER, '.cursor', 'extensions'),
    os.path.join(USER, 'AppData', 'Local', 'pip', 'cache'),
    os.path.join(USER, '.nuget', 'packages'),
    os.path.join(USER, 'AppData', 'Local', 'Microsoft', 'vscode-cpptools'),
    os.path.join(USER, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'SwReporter'),
    os.path.join(USER, 'AppData', 'Local', 'Arduino15', 'staging'),
    os.path.join(USER, 'AppData', 'Local', 'Microsoft', 'Teams'),
    os.path.join(USER, 'AppData', 'Local', 'unityhub-updater'),
    os.path.join(USER, 'AppData', 'Local', 'arduino-ide-updater'),
]

moved = []
failed = []
not_found = []

for d in candidates_dirs:
    p = Path(d)
    if not p.exists():
        not_found.append(d)
        print('Not found:', d)
        continue
    try:
        send2trash(str(p))
        moved.append(d)
        print('Moved dir to Recycle Bin:', d)
    except Exception as e:
        failed.append((d, str(e)))
        print('Failed to move:', d, '->', e)

summary = {
    'moved': moved,
    'failed': failed,
    'not_found': not_found,
}

out = Path(__file__).resolve().parent / f'cleanup_dirs_run-{Path(__file__).stat().st_mtime_ns}.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print('\nSummary:')
print('Moved:', len(moved))
print('Not found:', len(not_found))
print('Failed:', len(failed))
print('Wrote:', out)
