@echo off
set "ROOT=D:\inetpub\wwwroot\idm\lokal"
set "OUT=index.json"

powershell -NoLogo -NoProfile -Command ^
  "$root = '%ROOT%';" ^
  "$out = '%OUT%';" ^
  "$files = Get-ChildItem -Path $root -Recurse -Filter *.xml |" ^
  "  Where-Object { $_.FullName -notmatch '\\\\_' -and $_.FullName -notmatch '\\\\gfx(\\\\|$)' };" ^
  "" ^
  "# Extract: prefix + numeric ID" ^
  "$parsed = $files | ForEach-Object {" ^
  "  $name = $_.BaseName;" ^
  "  if ($name -match '^(.*)_([0-9]+)) {" ^
  "    [PSCustomObject]@{ Prefix = $matches[1]; ID = [int]$matches[2]; Original = $name }" ^
  "  }" ^
  "} | Where-Object { $_ -ne $null };" ^
  "" ^
  "# Get the item with the highest ID per prefix" ^
  "$selected = $parsed | Group-Object Prefix | ForEach-Object {" ^
  "  ($_.Group | Sort-Object ID -Descending | Select-Object -First 1).Original" ^
  "} | Sort-Object;" ^
  "" ^
  "# Convert to JSON array" ^
  "$json = $selected | ConvertTo-Json -Depth 3;" ^
  "Set-Content -Path $out -Value $json -Encoding UTF8"

echo Done: %OUT%