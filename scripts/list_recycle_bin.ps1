$shell = New-Object -ComObject Shell.Application
$rb = $shell.Namespace(0xA)
$items = @()
for ($i=0; $i -lt $rb.Items().Count; $i++) {
    $it = $rb.Items().Item($i)
    $items += [PSCustomObject]@{
        Name = $it.Name
        OriginalPath = $rb.GetDetailsOf($it, 1)
        Size = $rb.GetDetailsOf($it, 2)
        DeletionTime = $rb.GetDetailsOf($it, 3)
    }
}
$dest = Join-Path $PSScriptRoot 'recycle_bin.json'
$items | ConvertTo-Json -Depth 3 | Out-File -FilePath $dest -Encoding utf8
Get-Content -Path $dest -Raw
