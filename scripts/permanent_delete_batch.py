import os
from pathlib import Path
targets = [
    r"C:\ProgramData\Microsoft\Windows Defender\Definition Updates\Backup\mpasbase.lkg",
    r"C:\Users\glsch\AppData\Local\NuGet\v3-cache\670c1461c29885f9aa22c281d8b7da90845b38e4$ps_api.nuget.org_v3_index.json\nupkg_microsoft.windowsappsdk.1.7.250513003.dat",
    r"C:\ProgramData\dotnet\workloads\Microsoft.Android.Sdk.Windows.Msi.x64\35.0.92\9cbca012256566d88087dd4bb24baef7-x64.msi",
    r"C:\ProgramData\Package Cache\{B4D3359E-1191-4BBD-ABDB-0E4A39534981}v7.5.3.0\PowerShell-7.5.3-win-x64.msi",
    r"C:\ProgramData\dotnet\workloads\Microsoft.Android.Sdk.Windows.Msi.x64\34.0.154\dbc501244ed5f0a90bd823629bf18067-x64.msi",
]

results = []
for t in targets:
    p = Path(os.path.expandvars(t))
    entry = {'path': str(p), 'exists': p.exists()}
    if p.exists():
        try:
            if p.is_dir():
                # avoid removing directories unexpectedly
                entry['error'] = 'is a directory'
            else:
                p.unlink()
                entry['deleted'] = True
        except Exception as e:
            entry['error'] = str(e)
    results.append(entry)

print(results)
