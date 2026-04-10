param(
    [switch]$InstallAllureCli
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Playwright Core Framework Setup" -ForegroundColor Cyan
Write-Host "Running Windows setup..." -ForegroundColor Cyan

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }

    throw "Python was not found in PATH. Please install Python 3.11+ and try again."
}

$pythonCommand = Get-PythonCommand

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    if ($pythonCommand -eq "py") {
        py -m venv .venv
    }
    else {
        python -m venv .venv
    }
}
else {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
}

$venvPython = Join-Path ".venv" "Scripts\python.exe"

Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip

Write-Host "Installing framework in editable mode..." -ForegroundColor Yellow
& $venvPython -m pip install -e .

Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
& $venvPython -m playwright install

if ($InstallAllureCli) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing Allure CLI with winget..." -ForegroundColor Yellow
        winget install --id Qameta.Allure -e
    }
    else {
        Write-Host "winget not found. Install Allure CLI manually if needed." -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host "Setup completed successfully." -ForegroundColor Green
Write-Host "Run tests with:" -ForegroundColor Green
Write-Host ".venv\Scripts\python.exe -m playwright_core.testing.testng_runner automation\testng.xml" -ForegroundColor White

