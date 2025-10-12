import json
import os
from pathlib import Path

try:
    from send2trash import send2trash
except Exception as e:
    print('send2trash not available:', e)
    raise

targets = [
    r"C:\ProgramData\Microsoft\Windows Defender\Definition Updates\Backup\mpasbase.lkg",
    r"C:\ProgramData\dotnet\workloads\Microsoft.Android.Sdk.Windows.Msi.x64\35.0.92\9cbca012256566d88087dd4bb24baef7-x64.msi",
    r"C:\ProgramData\Package Cache\{B4D3359E-1191-4BBD-ABDB-0E4A39534981}v7.5.3.0\PowerShell-7.5.3-win-x64.msi",
    r"C:\ProgramData\dotnet\workloads\Microsoft.Android.Sdk.Windows.Msi.x64\34.0.154\dbc501244ed5f0a90bd823629bf18067-x64.msi",
]

results = []
for t in targets:
    p = Path(os.path.expandvars(t))
    res = {'path': str(p), 'exists': p.exists()}
    if not p.exists():
        results.append(res)
        print('Not found, skipping:', p)
        continue
    try:
        send2trash(str(p))
        res['moved_to_recycle'] = True
        print('Moved to Recycle Bin:', p)
    except PermissionError as pe:
        res['error'] = 'permission denied: ' + str(pe)
        print('Permission denied for:', p)
    except Exception as e:
        res['error'] = str(e)
        print('Failed to move:', p, '->', e)
    results.append(res)

out = Path(__file__).with_name('recycle_programdata_result.json')
out.write_text(json.dumps(results, indent=2), encoding='utf-8')
print('\nWrote log to', out)
