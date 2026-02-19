param(
  [ValidateSet("exe", "installer", "source", "all")]
  [string]$Target = "all",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$testsDir = Join-Path $repoRoot "tests"
$logsDir = Join-Path $testsDir "logs"
$logPath = Join-Path $logsDir "build.log"

New-Item -ItemType Directory -Force $logsDir | Out-Null

function Run-Step([string]$name, [scriptblock]$command) {
  "=== $name ===" | Out-File -FilePath $logPath -Append -Encoding utf8
  & $command *>&1 | Tee-Object -FilePath $logPath -Append | Out-Host
  $exitCode = $LASTEXITCODE
  "" | Out-File -FilePath $logPath -Append -Encoding utf8
  if ($exitCode -ne 0) {
    throw "$name failed with exit code $exitCode"
  }
}

Push-Location $repoRoot
try {
  "=== Build: $(Get-Date -Format o) | Target=$Target | Clean=$Clean ===" | Out-File -FilePath $logPath -Append -Encoding utf8

  if ($Clean) {
    Run-Step "Clean artifacts" { powershell -ExecutionPolicy Bypass -File tools/clean_artifacts.ps1 }
  }

  if ($Target -eq "exe" -or $Target -eq "all") {
    Run-Step "Build executable" { cmd /c "tools\\build\\build_exe.bat --nopause" }
    Run-Step "Build portable zip" { cmd /c "tools\\build\\build_portable_zip.bat --nopause" }
  }

  if ($Target -eq "installer") {
    Run-Step "Build installer" { cmd /c "tools\\build\\build_installer.bat --nopause" }
  }

  if ($Target -eq "source" -or $Target -eq "all") {
    Run-Step "Build source package" { cmd /c "tools\\build\\create_source_package.bat --nopause" }
  }

  Write-Host "Build completed. Log: $logPath"
} finally {
  Pop-Location
}
