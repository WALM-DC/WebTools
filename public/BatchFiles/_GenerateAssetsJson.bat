@echo off
setlocal

python "D:\inetpub\wwwroot\idm\XMLLister\CreateProdListJsonServer.py"

if errorlevel 1 (
    echo ERROR: Python script failed.
    pause
    exit /b 1
)

set "PS1=%~dp0_GenerateAssetsJson.ps1"

if not exist "%PS1%" (
    echo ERROR: PowerShell script not found:
    echo "%PS1%"
    pause
    exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%"

if errorlevel 1 (
    echo ERROR: PowerShell script failed.
    pause
    exit /b 1
)

echo.
echo Processing completed successfully.
exit /b 0