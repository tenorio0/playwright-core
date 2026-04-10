param(
    [string]$XmlPath = "automation\\testng.xml",
    [string]$Target = "",
    [switch]$Headed,
    [int]$SlowMo = 0
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Playwright Core Test Runner" -ForegroundColor Cyan

$venvPython = Join-Path ".venv" "Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment not found. Run .\tools\setup\setup_windows.ps1 first."
}

if ($Headed) {
    $env:HEADLESS = "false"
    if ($SlowMo -le 0) {
        $SlowMo = 400
    }
}

if ($SlowMo -gt 0) {
    $env:SLOW_MO = "$SlowMo"
}

$headlessValue = if ($env:HEADLESS) { $env:HEADLESS } else { "true" }
$slowMoValue = if ($env:SLOW_MO) { $env:SLOW_MO } else { "0" }

Write-Host "HEADLESS=$headlessValue" -ForegroundColor DarkGray
Write-Host "SLOW_MO=$slowMoValue" -ForegroundColor DarkGray

if ($Target -and $Target.Trim()) {
    $pytestArgs = @("-B", "-m", "pytest", $Target)
    Write-Host "Running target: $Target" -ForegroundColor Yellow
    & $venvPython @pytestArgs
}
else {
    Write-Host "Running XML: $XmlPath" -ForegroundColor Yellow
    & $venvPython -B -m playwright_core.testing.testng_runner $XmlPath
}
