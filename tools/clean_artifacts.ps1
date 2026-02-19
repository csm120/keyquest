$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$testsDir = Join-Path $repoRoot "tests"
$logsDir = Join-Path $testsDir "logs"
$logPath = Join-Path $logsDir "clean_artifacts.log"

New-Item -ItemType Directory -Force $logsDir | Out-Null

function Remove-IfExists($path) {
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction Stop
    "Removed: $path" | Out-File -FilePath $logPath -Append -Encoding utf8
  } else {
    "Missing: $path" | Out-File -FilePath $logPath -Append -Encoding utf8
  }
}

Push-Location $repoRoot
try {
  "=== Clean artifacts: $(Get-Date -Format o) ===" | Out-File -FilePath $logPath -Append -Encoding utf8

  Remove-IfExists (Join-Path $repoRoot "build")
  Remove-IfExists (Join-Path $repoRoot "dist")

  if (Test-Path -LiteralPath (Join-Path $repoRoot "source")) {
    Get-ChildItem -LiteralPath (Join-Path $repoRoot "source") -Filter "*.zip" -File -ErrorAction SilentlyContinue |
      ForEach-Object {
        Remove-Item -LiteralPath $_.FullName -Force -ErrorAction Stop
        "Removed: $($_.FullName)" | Out-File -FilePath $logPath -Append -Encoding utf8
      }
  } else {
    "Missing: source/" | Out-File -FilePath $logPath -Append -Encoding utf8
  }

  Get-ChildItem -LiteralPath $repoRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "__pycache__" -or $_.Name -eq ".pytest_cache" -or $_.Name -eq ".ruff_cache" -or $_.Name -eq ".mypy_cache" } |
    ForEach-Object { Remove-IfExists $_.FullName }

  "Done." | Out-File -FilePath $logPath -Append -Encoding utf8
  Write-Host "Artifacts cleaned. Log: $logPath"
} finally {
  Pop-Location
}

