param(
    [string]$CommitMessage = "",
    [switch]$SkipTests,
    [switch]$SkipLocalBuilds,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "==> $Label" -ForegroundColor Cyan
    & $Action
}

function Invoke-GitOrThrow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandLine
    )

    Invoke-Expression $CommandLine
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $CommandLine"
    }
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command git)) {
    throw "git is required."
}
if (-not (Test-Command python)) {
    throw "python is required."
}

$version = python -c "from modules.version import __version__; print(__version__)" 2>$null
if (-not $version) {
    throw "Could not read modules/version.py"
}

$version = $version.Trim()
$tagName = "v$version"

if (-not $CommitMessage) {
    $CommitMessage = "Release $tagName"
}

$currentBranch = git branch --show-current
if ($LASTEXITCODE -ne 0) {
    throw "Could not detect current git branch."
}
if ($currentBranch.Trim() -ne "main") {
    throw "Release script must be run from the main branch. Current branch: $currentBranch"
}

$statusBefore = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "Could not read git status."
}
if (-not $statusBefore) {
    throw "Working tree is clean. Make your release changes first, then run this script."
}

Invoke-Step "Check release tag availability" {
    git rev-parse --verify --quiet "refs/tags/$tagName" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        throw "Tag $tagName already exists locally. Update modules/version.py before releasing."
    }

    git ls-remote --exit-code --tags origin "refs/tags/$tagName" *> $null
    if ($LASTEXITCODE -eq 0) {
        throw "Tag $tagName already exists on origin. Update modules/version.py before releasing."
    }
}

Invoke-Step "Build Pages site" {
    python tools/dev/build_pages_site.py
}

if (-not $SkipTests) {
    Invoke-Step "Run test suite" {
        python -m pytest -q
    }
}

if (-not $SkipLocalBuilds) {
    Invoke-Step "Build local EXE" {
        cmd /c tools\build\build_exe.bat --nopause
    }

    Invoke-Step "Build local portable ZIP" {
        cmd /c tools\build\build_portable_zip.bat --nopause
    }

    Invoke-Step "Build local installer" {
        cmd /c tools\build\build_installer.bat --nopause
    }
}

if ($DryRun) {
    Write-Host ""
    Write-Host "Dry run complete." -ForegroundColor Yellow
    Write-Host "Would commit with message: $CommitMessage"
    Write-Host "Would push branch: main"
    Write-Host "Would create and push tag: $tagName"
} else {
    Invoke-Step "Commit release changes" {
        Invoke-GitOrThrow "git add -A"
        Invoke-GitOrThrow "git commit -m `"$CommitMessage`""
    }

    Invoke-Step "Push main" {
        Invoke-GitOrThrow "git push origin main"
    }

    Invoke-Step "Create release tag" {
        Invoke-GitOrThrow "git tag -a $tagName -m `"KeyQuest $version`""
    }

    Invoke-Step "Push release tag" {
        Invoke-GitOrThrow "git push origin $tagName"
    }
}

Write-Host ""
Write-Host "Release submitted successfully." -ForegroundColor Green
Write-Host "Version: $version"
Write-Host "Tag: $tagName"
Write-Host "GitHub Pages will update from main."
Write-Host "GitHub Release assets will be built from the pushed tag."
