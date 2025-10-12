import json
import os
import sys
from datetime import datetime

REPORT = os.path.join(os.path.dirname(__file__), '..', 'report-userprofile.json')
REPORT = os.path.abspath(REPORT)

def human(n):
    for u in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.2f}{u}"
        n /= 1024
    return f"{n:.2f}PB"

def guess_category(p):
    lp = p.lower()
    if '\\.cache\\' in lp or '\\appdata\\local\\temp' in lp or '\\temp\\' in lp or '\\pip\\cache' in lp:
        return 'cache/temp'
    if '\\.nuget\\' in lp or lp.endswith('.nupkg') or '\\nuget\\packages' in lp:
        return 'nuget/package-cache'
    if '\\node_modules\\' in lp:
        return 'node_modules'
    if '\\android\\' in lp or 'system-images' in lp or 'android-sdk' in lp or 'android' in lp:
        return 'android/sdk/image'
    if '\\.cursor\\extensions\\' in lp or '\\vscode' in lp or '\\extensions\\' in lp or '\\ms-vscode' in lp:
        return 'vscode-extension'
    if lp.endswith('.zip') or lp.endswith('.msi') or lp.endswith('.exe') or lp.endswith('.msix') or lp.endswith('.msu'):
        return 'installer/archive'
    if lp.endswith('.whl') or lp.endswith('.dist-info') or '\\site-packages\\' in lp:
        return 'python-package'
    return 'personal/other'


def main():
    if not os.path.exists(REPORT):
        print('REPORT not found:', REPORT)
        sys.exit(2)
    with open(REPORT, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_sorted = sorted(data, key=lambda x: x.get('size',0), reverse=True)
    top = data_sorted[:40]

    total = sum(x.get('size',0) for x in data)
    top_total = sum(x.get('size',0) for x in top)

    print(f'Report: {REPORT}')
    print(f'Total items in report: {len(data)}')
    print(f'Total size in report: {human(total)}')
    print(f'Top {len(top)} combined size: {human(top_total)}\n')

    groups = {}
    print('Top items:')
    for i, it in enumerate(top,1):
        path = it['path']
        size = it.get('size',0)
        mtime = datetime.fromtimestamp(it.get('mtime',0)).isoformat()
        cat = guess_category(path)
        groups[cat] = groups.get(cat,0) + 1
        print(f"{i:2d}. {human(size):>8}  {cat:20}  {path}")

    print('\nGroup counts in top items:')
    for k,v in sorted(groups.items(), key=lambda x:-x[1]):
        print(f"  {k:25} {v}")

    # Also print easy cleanup candidates (cache/temp, nuget, vscode-extension, android/sdk/image)
    candidates = [x for x in data_sorted if guess_category(x['path']) in ('cache/temp','nuget/package-cache','vscode-extension','android/sdk/image','node_modules')]
    cand_total = sum(x.get('size',0) for x in candidates[:200])
    print(f"\nTop cleanup-candidate count: {len(candidates)}; top-200 candidates combined size: {human(cand_total)}")

if __name__ == '__main__':
    main()
