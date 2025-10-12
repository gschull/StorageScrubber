import json
from pathlib import Path

files = ['report-large-users.json','report-large-progdata.json']
out = 'report-large.json'
all_items = []
for f in files:
    p = Path(f)
    if p.exists():
        all_items.extend(json.loads(p.read_text(encoding='utf-8')))

all_items_sorted = sorted(all_items, key=lambda x: x.get('size',0), reverse=True)
Path(out).write_text(json.dumps(all_items_sorted, indent=2), encoding='utf-8')
print('Wrote', out, 'with', len(all_items_sorted), 'entries')
