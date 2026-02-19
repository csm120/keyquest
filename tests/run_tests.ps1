$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$logsDir = Join-Path $PSScriptRoot "logs"
$logPath = Join-Path $logsDir "unittest.log"

New-Item -ItemType Directory -Force $logsDir | Out-Null

Push-Location $repoRoot
try {
  python -m unittest discover -s tests -p "test_*.py" -v 2>&1 | Tee-Object -FilePath $logPath
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
