$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$testsDir = Join-Path $repoRoot "tests"
$logsDir = Join-Path $testsDir "logs"
$logPath = Join-Path $logsDir "clean_caches.log"

New-Item -ItemType Directory -Force $logsDir | Out-Null

function Remove-IfExists($path) {
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction Stop
    "Removed: $path" | Out-File -FilePath $logPath -Append -Encoding utf8
  }
}

Push-Location $repoRoot
try {
  "=== Clean caches: $(Get-Date -Format o) ===" | Out-File -FilePath $logPath -Append -Encoding utf8

  Get-ChildItem -LiteralPath $repoRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "__pycache__" -or $_.Name -eq ".pytest_cache" -or $_.Name -eq ".ruff_cache" -or $_.Name -eq ".mypy_cache" } |
    ForEach-Object { Remove-IfExists $_.FullName }

  Write-Host "Caches cleaned. Log: $logPath"
} finally {
  Pop-Location
}

