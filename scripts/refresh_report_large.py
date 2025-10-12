import json
import os
from pathlib import Path

REPORT = Path(__file__).with_name('..').resolve().joinpath('report-large.json')

def normalize_path(p: str) -> str:
    # Some report paths contain literal newlines (\n) due to prior concatenation bugs.
    # Replace newlines with the OS path separator, and strip surrounding whitespace.
    return p.replace('\n', os.sep).strip()

def main():
    if not REPORT.exists():
        print('report-large.json not found at', REPORT)
        return
    j = json.loads(REPORT.read_text(encoding='utf-8'))
    out = []
    for e in j:
        raw = e.get('path', '')
        path = normalize_path(raw)
        p = Path(path)
        exists = p.exists()
        size = None
        try:
            if exists:
                size = p.stat().st_size
        except Exception:
            size = None
        e['path'] = path
        e['exists'] = exists
        e['current_size'] = size
        out.append(e)
    REPORT.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('Updated', REPORT)

if __name__ == '__main__':
    main()
