# Folder to scan (edit this)
$root = "D:\inetpub\wwwroot\icom\ICOM\gfx\"

# Output: assets.json next to the .bat/.ps1
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$out = Join-Path $scriptDir "assets.json"

Write-Host "Scanning for .png and .jpeg under:" $root

$files = Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match "^\.(png|jpeg)$" } |
    Select-Object -ExpandProperty FullName |
    Sort-Object

$files | ConvertTo-Json -Depth 3 | Set-Content -Path $out -Encoding UTF8

Write-Host "Created:" $out
Write-Host "Count:" $files.Count