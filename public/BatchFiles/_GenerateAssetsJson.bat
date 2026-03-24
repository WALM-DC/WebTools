@echo off
setlocal

set "PS1=%~dp0_GenerateAssetsJson.ps1"

if not exist "%PS1%" (
  echo ERROR: Script not found: "%PS1%"
  pause
  exit /b 1
)

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
pause