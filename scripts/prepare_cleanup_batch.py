import json
import os
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORT = os.path.join(ROOT, 'report-userprofile.json')
OUT = os.path.join(os.path.dirname(__file__), 'cleanup_candidates.json')

CATEGORIES = {
    'cache/temp': ['.cache\\', '\\pip\\cache', '\\AppData\\Local\\Temp', '\\Temp\\', '\\pip\\http-v2'],
    'nuget/package-cache': ['\\.nuget\\', '\\NuGet\\v3-cache', '.nupkg', '\\packages\\'],
    'vscode-extension': ['\\.cursor\\extensions\\', '\\Microsoft\\vscode', '\\.vscode\\extensions\\vscode-cpptools', '\\vscode-cpptools'],
    'platformio': ['\\.platformio\\', 'platformio'],
    'installers': ['installer.exe', '.msi', '.exe', '.msix', '.zip']
}


def match_any(path, patterns):
    lp = path.lower()
    for p in patterns:
        if p.lower() in lp:
            return True
    return False


def human(n):
    for u in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.2f}{u}"
        n /= 1024
    return f"{n:.2f}PB"


def main():
    if not os.path.exists(REPORT):
        print('report not found:', REPORT)
        return
    with open(REPORT, 'r', encoding='utf-8') as f:
        data = json.load(f)

    groups = {k:[] for k in CATEGORIES}
    others = []
    for it in data:
        p = it.get('path','')
        sz = it.get('size',0)
        matched = False
        for k,patterns in CATEGORIES.items():
            if match_any(p, patterns):
                groups[k].append(it)
                matched = True
                break
        if not matched:
            others.append(it)

    summary = {}
    for k,v in groups.items():
        s = sum(x.get('size',0) for x in v)
        summary[k] = {'count': len(v), 'size': s}

    print('Cleanup candidate summary:')
    total_candidates = sum(summary[k]['count'] for k in summary)
    total_size = sum(summary[k]['size'] for k in summary)
    for k in sorted(summary.keys(), key=lambda x: -summary[x]['size']):
        print(f"  {k:15} {summary[k]['count']:6} items   {human(summary[k]['size']):>8}")
    print(f"\nTotal candidates: {total_candidates}   Combined size: {human(total_size)}\n")

    # For safety, exclude android/sdk images from default cleanup list
    pick_groups = ['cache/temp','nuget/package-cache','vscode-extension','platformio','installers']
    pick = []
    for k in pick_groups:
        pick.extend(groups.get(k, []))

    # dedupe by path
    seen = set()
    pick_unique = []
    for it in pick:
        p = it['path']
        if p in seen:
            continue
        seen.add(p)
        pick_unique.append(it)

    print('Default suggested cleanup (moved to Recycle Bin if you confirm):')
    for i,it in enumerate(sorted(pick_unique, key=lambda x:-x.get('size',0))[:200],1):
        print(f"{i:3d}. {human(it.get('size',0)):>8}  {it['path']}")

    # save out list for review
    out_json = {
        'candidates_summary': summary,
        'default_suggested_paths': [p['path'] for p in pick_unique],
    }
    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(out_json,f,indent=2)
    print(f"\nWrote {OUT}")

if __name__=='__main__':
    main()
