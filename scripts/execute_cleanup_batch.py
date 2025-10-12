"""Execute cleanup batch: move default suggested paths from cleanup_candidates.json to Recycle Bin.
Usage (PowerShell-friendly):
  python .\scripts\execute_cleanup_batch.py [--count N]
Defaults to top 200 paths.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from send2trash import send2trash
except Exception as e:
    print('send2trash is required. Install with pip install send2trash', file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parent
CAND_FILE = ROOT / 'cleanup_candidates.json'
OUT_DIR = ROOT

MAX_DEFAULT = 200


def expand_path(p):
    return os.path.expandvars(p)


def main():
    count = MAX_DEFAULT
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except Exception:
            pass

    if not CAND_FILE.exists():
        print('cleanup_candidates.json not found at', CAND_FILE)
        return 2

    with open(CAND_FILE, 'r', encoding='utf-8') as f:
        cj = json.load(f)

    paths = cj.get('default_suggested_paths', [])
    if not paths:
        print('No default_suggested_paths in', CAND_FILE)
        return 3

    to_move = paths[:count]
    moved = []
    skipped = []
    failed = []

    for p in to_move:
        exp = expand_path(p)
        ppath = Path(exp)
        if not ppath.exists():
            skipped.append({'path': exp, 'reason': 'not found'})
            print('Not found, skipping:', exp)
            continue
        try:
            send2trash(str(ppath))
            moved.append({'path': exp, 'size': ppath.stat().st_size if ppath.exists() else None})
            print('Moved to Recycle Bin:', exp)
        except Exception as e:
            failed.append({'path': exp, 'error': str(e)})
            print('Failed to move:', exp, '->', e)

    out = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'requested_count': count,
        'moved_count': len(moved),
        'skipped_count': len(skipped),
        'failed_count': len(failed),
        'moved': moved,
        'skipped': skipped,
        'failed': failed,
    }

    fname = OUT_DIR / f'cleanup_run-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)

    print('\nSummary:')
    print('  Requested:', count)
    print('  Moved:', len(moved))
    print('  Skipped:', len(skipped))
    print('  Failed:', len(failed))
    print('Wrote:', fname)
    return 0

if __name__ == '__main__':
    sys.exit(main())
