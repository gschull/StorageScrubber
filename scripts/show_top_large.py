import json
from pathlib import Path

data = json.loads(Path('report-large.json').read_text(encoding='utf-8'))
print('Top items:')
for i, it in enumerate(data[:50], 1):
    print(f"{i:2d}. {it['path']} — {it['size'] // (1024*1024)} MB  ({it.get('ext')})")
