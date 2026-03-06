"""GitHub release updater support for KeyQuest."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path


GITHUB_OWNER = "csm120"
GITHUB_REPO = "KeyQuest"
LATEST_RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
DEFAULT_TIMEOUT_SECONDS = 15
INSTALLER_NAME = "KeyQuestSetup.exe"
PORTABLE_ZIP_NAME = "KeyQuest-win64.zip"


def can_self_update() -> bool:
    """Return True when the current process can update an installed app."""
    return os.name == "nt" and getattr(sys, "frozen", False)


def is_portable_layout(app_dir: str) -> bool:
    """Return True when the running frozen app appears to be a portable build."""
    exe_dir = Path(app_dir)
    return (
        exe_dir.exists()
        and (exe_dir / "KeyQuest.exe").exists()
        and (exe_dir / "modules").exists()
        and (exe_dir / "games").exists()
        and (exe_dir / "Sentences").exists()
    )


def _extract_version_parts(raw: str) -> tuple[int, ...]:
    tokens = re.findall(r"\d+", raw or "")
    if not tokens:
        return (0,)
    return tuple(int(token) for token in tokens)


def normalize_version(raw: str) -> str:
    """Normalize a raw version/tag string to dotted numeric form."""
    parts = _extract_version_parts(raw)
    if not parts:
        return "0"
    return ".".join(str(part) for part in parts)


def is_newer_version(current_version: str, candidate_version: str) -> bool:
    """Return True when candidate_version is newer than current_version."""
    current = _extract_version_parts(current_version)
    candidate = _extract_version_parts(candidate_version)
    width = max(len(current), len(candidate))
    current += (0,) * (width - len(current))
    candidate += (0,) * (width - len(candidate))
    return candidate > current


def parse_release_version(release: dict) -> str:
    """Return the version string to compare from a GitHub release payload."""
    raw = str(release.get("tag_name") or release.get("name") or "").strip()
    return normalize_version(raw)


def select_installer_asset(release: dict) -> dict | None:
    """Return the preferred installer asset from a GitHub release."""
    assets = release.get("assets", [])
    exact_match = None
    fallback = None

    for asset in assets:
        name = str(asset.get("name", ""))
        lowered = name.lower()
        if name == INSTALLER_NAME:
            exact_match = asset
            break
        if lowered.endswith(".exe") and "setup" in lowered and fallback is None:
            fallback = asset

    return exact_match or fallback


def select_portable_asset(release: dict) -> dict | None:
    """Return the preferred portable ZIP asset from a GitHub release."""
    assets = release.get("assets", [])
    exact_match = None
    fallback = None

    for asset in assets:
        name = str(asset.get("name", ""))
        lowered = name.lower()
        if name == PORTABLE_ZIP_NAME:
            exact_match = asset
            break
        if lowered.endswith(".zip") and "keyquest" in lowered and fallback is None:
            fallback = asset

    return exact_match or fallback


def fetch_latest_release(url: str = LATEST_RELEASE_API_URL, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Fetch the latest GitHub release metadata."""
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "KeyQuest-Updater",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_updates_dir() -> Path:
    """Return the staging directory used for downloaded installers and launcher scripts."""
    base = Path(tempfile.gettempdir()) / "KeyQuestUpdater"
    base.mkdir(parents=True, exist_ok=True)
    return base


def download_file(url: str, destination: Path, progress_callback=None, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> Path:
    """Download a file with optional byte progress reporting."""
    request = urllib.request.Request(url, headers={"User-Agent": "KeyQuest-Updater"})
    destination.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(request, timeout=timeout) as response, open(destination, "wb") as handle:
        total = response.headers.get("Content-Length")
        total_bytes = int(total) if total and total.isdigit() else 0
        downloaded = 0
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            handle.write(chunk)
            downloaded += len(chunk)
            if progress_callback:
                progress_callback(downloaded, total_bytes)

    return destination


def build_installer_filename(version: str) -> str:
    """Return a stable installer filename for a staged update."""
    safe_version = normalize_version(version).replace(".", "_")
    return f"KeyQuestSetup_{safe_version}.exe"


def build_portable_zip_filename(version: str) -> str:
    """Return a stable portable ZIP filename for a staged update."""
    safe_version = normalize_version(version).replace(".", "_")
    return f"KeyQuest-win64_{safe_version}.zip"


def _sentence_merge_powershell(source_sentences: str, target_sentences: str) -> str:
    """Return a PowerShell one-liner that merges sentence files by unique lines."""
    return (
        'powershell -NoProfile -ExecutionPolicy Bypass -Command ^\n'
        f'  "$sourceSentences = {source_sentences}; " ^\n'
        f'  "$targetSentences = {target_sentences}; " ^\n'
        '  "if ((Test-Path $sourceSentences) -and (Test-Path $targetSentences)) {{ " ^\n'
        '  "  Get-ChildItem -LiteralPath $sourceSentences -File | ForEach-Object {{ " ^\n'
        '  "    $dest = Join-Path $targetSentences $_.Name; " ^\n'
        '  "    if (Test-Path $dest) {{ " ^\n'
        '  "      $existing = Get-Content -LiteralPath $_.FullName; " ^\n'
        '  "      $incoming = Get-Content -LiteralPath $dest; " ^\n'
        '  "      $merged = New-Object System.Collections.Generic.List[string]; " ^\n'
        '  "      foreach ($line in $existing) {{ if (-not $merged.Contains($line)) {{ [void]$merged.Add($line) }} }} " ^\n'
        '  "      foreach ($line in $incoming) {{ if (-not $merged.Contains($line)) {{ [void]$merged.Add($line) }} }} " ^\n'
        '  "      Set-Content -LiteralPath $dest -Value $merged -Encoding UTF8; " ^\n'
        '  "    }} else {{ " ^\n'
        '  "      Copy-Item -LiteralPath $_.FullName -Destination $dest -Force; " ^\n'
        '  "    }} " ^\n'
        '  "  }} " ^\n'
        '  "}}"'
    )


def create_update_launcher(
    installer_path: Path,
    app_dir: str,
    app_exe_path: str,
    current_pid: int,
    script_path: Path | None = None,
) -> Path:
    """Create a detached launcher script that waits, installs, then restarts KeyQuest."""
    script_path = script_path or (installer_path.parent / "run_keyquest_update.cmd")
    backup_dir = installer_path.parent / "installer_backup"
    sentence_merge_command = _sentence_merge_powershell(
        "'%BACKUP_DIR%\\Sentences'",
        "'%APP_DIR%\\Sentences'",
    )

    script_text = f"""@echo off
setlocal EnableExtensions
set "TARGET_PID={int(current_pid)}"
set "INSTALLER={installer_path}"
set "APP_DIR={app_dir}"
set "APP_EXE={app_exe_path}"
set "BACKUP_DIR={backup_dir}"

:wait_for_exit
tasklist /FI "PID eq %TARGET_PID%" | find "%TARGET_PID%" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto :wait_for_exit
)

if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"
mkdir "%BACKUP_DIR%" >nul 2>&1
if exist "%APP_DIR%\\progress.json" copy /Y "%APP_DIR%\\progress.json" "%BACKUP_DIR%\\progress.json" >nul
if exist "%APP_DIR%\\Sentences" robocopy "%APP_DIR%\\Sentences" "%BACKUP_DIR%\\Sentences" /E /R:2 /W:1 /NFL /NDL /NJH /NJS /NP >nul

start "" /wait "%INSTALLER%" /CURRENTUSER /VERYSILENT /SUPPRESSMSGBOXES /NOCANCEL /CLOSEAPPLICATIONS /FORCECLOSEAPPLICATIONS
if errorlevel 1 exit /b %errorlevel%

if exist "%BACKUP_DIR%\\progress.json" copy /Y "%BACKUP_DIR%\\progress.json" "%APP_DIR%\\progress.json" >nul
{sentence_merge_command}
if errorlevel 1 exit /b %errorlevel%

if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"
timeout /t 2 /nobreak >nul
start "" "%APP_EXE%"
exit /b 0
"""
    script_path.write_text(script_text, encoding="utf-8")
    return script_path


def create_portable_update_launcher(
    zip_path: Path,
    app_dir: str,
    app_exe_path: str,
    current_pid: int,
    script_path: Path | None = None,
) -> Path:
    """Create a detached launcher script that replaces a portable build in place."""
    script_path = script_path or (zip_path.parent / "run_keyquest_portable_update.cmd")
    extract_dir = zip_path.parent / "portable_extract"
    sentence_merge_command = _sentence_merge_powershell(
        "'%APP_DIR%\\Sentences'",
        "$releaseSentences",
    )

    script_text = f"""@echo off
setlocal EnableExtensions
set "TARGET_PID={int(current_pid)}"
set "ZIP_PATH={zip_path}"
set "APP_DIR={app_dir}"
set "APP_EXE={app_exe_path}"
set "EXTRACT_DIR={extract_dir}"

:wait_for_exit
tasklist /FI "PID eq %TARGET_PID%" | find "%TARGET_PID%" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto :wait_for_exit
)

if exist "%EXTRACT_DIR%" rmdir /s /q "%EXTRACT_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ZIP_PATH%' -DestinationPath '%EXTRACT_DIR%' -Force"
if errorlevel 1 exit /b %errorlevel%

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$releaseRoot = Join-Path '%EXTRACT_DIR%' 'KeyQuest'; " ^
  "$releaseSentences = Join-Path $releaseRoot 'Sentences'; " ^
{sentence_merge_command}
if errorlevel 1 exit /b %errorlevel%

robocopy "%EXTRACT_DIR%\\KeyQuest" "%APP_DIR%" /E /R:2 /W:1 /NFL /NDL /NJH /NJS /NP /XF progress.json
set "ROBOCODE=%ERRORLEVEL%"
if %ROBOCODE% GEQ 8 exit /b %ROBOCODE%

if exist "%EXTRACT_DIR%" rmdir /s /q "%EXTRACT_DIR%"
timeout /t 1 /nobreak >nul
start "" "%APP_EXE%"
exit /b 0
"""
    script_path.write_text(script_text, encoding="utf-8")
    return script_path
