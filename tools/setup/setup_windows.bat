@echo off
setlocal
cd /d "%~dp0\..\.."

echo.
echo Playwright Core Framework Setup
echo Running Windows setup...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1"

if errorlevel 1 (
    echo.
    echo Setup failed.
    exit /b 1
)

echo.
echo Setup completed successfully.
endlocal
