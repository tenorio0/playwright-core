@echo off
setlocal
cd /d "%~dp0\..\.."

echo.
echo Playwright Core Test Runner
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run tools\setup\setup_windows.bat first.
    exit /b 1
)

if /I "%~1"=="--headed" (
    set HEADLESS=false
    if "%~2"=="" (
        set SLOW_MO=400
        shift
    ) else (
        set SLOW_MO=%~2
        shift
        shift
    )
)

echo HEADLESS=%HEADLESS%
echo SLOW_MO=%SLOW_MO%

if "%~1"=="" (
    .venv\Scripts\python.exe -B -m playwright_core.testing.testng_runner automation\testng.xml
) else (
    .venv\Scripts\python.exe -B -m pytest %*
)

endlocal
