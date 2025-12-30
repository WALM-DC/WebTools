@echo off
set "ROOT=D:\inetpub\wwwroot\icom\ICOM"
rem set "OUT=C:\temp\json_paths.txt"
set "OUT=json_paths.txt"

powershell -NoLogo -NoProfile -Command ^
  "$root = '%ROOT%';" ^
  "$out = '%OUT%';" ^
  "Get-ChildItem -Path $root -Recurse -Filter *.json |" ^
  "Where-Object { $_.FullName -notmatch '\\\\_' -and $_.FullName -notmatch '\\\\gfx(\\\\|$)' } |" ^
  "Select-Object -Expand FullName | Out-File -Encoding utf8 $out"

echo Done: %OUT%
