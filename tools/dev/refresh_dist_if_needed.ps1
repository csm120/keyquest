param(
    [ValidateSet("pre-commit", "post-checkout", "post-merge", "manual")]
    [string]$Trigger = "manual",
    [string[]]$ChangedPaths = @(),
    [switch]$Strict
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

$distExe = Join-Path $repoRoot "dist\KeyQuest\KeyQuest.exe"
$relevantPatterns = @(
    "keyquest.pyw",
    "games/",
    "modules/",
    "ui/",
    "Sentences/",
    "docs/user/WHATS_NEW.md",
    "README.md",
    "README.html",
    "requirements.txt",
    "requirements.lock",
    "tools/build/",
    "modules/version.py"
)

function Test-RelevantPath {
    param([string]$Path)

    if (-not $Path) {
        return $false
    }

    $normalized = $Path.Replace("\", "/").Trim()
    foreach ($pattern in $relevantPatterns) {
        if ($normalized.StartsWith($pattern, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Get-StagedPaths {
    $output = git diff --cached --name-only --diff-filter=ACMR
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read staged paths."
    }
    return @($output | Where-Object { $_.Trim() })
}

function Invoke-LocalDistBuild {
    Write-Host "[dist-sync] Refreshing local dist/ from current working tree..." -ForegroundColor Cyan
    cmd /c tools\build\build_exe.bat --nopause
    if ($LASTEXITCODE -ne 0) {
        throw "Executable build failed."
    }

    cmd /c tools\build\build_portable_zip.bat --nopause
    if ($LASTEXITCODE -ne 0) {
        throw "Portable ZIP build failed."
    }

    cmd /c tools\build\build_installer.bat --nopause
    if ($LASTEXITCODE -ne 0) {
        throw "Installer build failed."
    }
}

$pathsToInspect = @($ChangedPaths | Where-Object { $_ -and $_.Trim() })
if (-not $pathsToInspect -and $Trigger -eq "pre-commit") {
    $pathsToInspect = Get-StagedPaths
}

$needsRefresh = -not (Test-Path $distExe)
if (-not $needsRefresh) {
    $needsRefresh = @($pathsToInspect | Where-Object { Test-RelevantPath $_ }).Count -gt 0
}

if (-not $needsRefresh) {
    Write-Host "[dist-sync] No dist refresh needed for $Trigger." -ForegroundColor DarkGray
    exit 0
}

try {
    Invoke-LocalDistBuild
    Write-Host "[dist-sync] dist/ is current." -ForegroundColor Green
    exit 0
} catch {
    Write-Host "[dist-sync] $($_.Exception.Message)" -ForegroundColor Red
    if ($Strict) {
        exit 1
    }
    exit 0
}
