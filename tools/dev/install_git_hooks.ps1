Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

$hooksPath = ".githooks"

git config core.hooksPath $hooksPath
if ($LASTEXITCODE -ne 0) {
    throw "Could not set git hooks path to $hooksPath."
}

Write-Host "Configured git hooks path: $hooksPath" -ForegroundColor Green
