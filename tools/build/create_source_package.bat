@echo off
REM KeyQuest Source Code Packaging Script
REM Creates a clean source code archive for distribution to developers
setlocal
pushd "%~dp0\..\.."

set "NO_PAUSE="
if /I "%~1"=="--nopause" set "NO_PAUSE=1"

echo ========================================
echo KeyQuest Source Code Packager
echo ========================================
echo.

REM Step 1: Clean old source packages
echo [1/4] Cleaning old source packages...
if exist "source\*.zip" (
    echo   Removing old ZIP files from source/ folder...
    del /q "source\*.zip"
    echo   Old packages removed!
) else (
    echo   No old packages found.
)
echo.

REM Step 2: Set package name with date (use PowerShell for reliable date formatting)
echo [2/4] Preparing new package...
for /f "tokens=*" %%i in ('powershell -command "Get-Date -Format 'yyyyMMdd'"') do set DATESTR=%%i
REM Single source of truth for version: modules/version.py
for /f "usebackq delims=" %%i in (`python -c "from modules.version import __version__; print(__version__)" 2^>nul`) do set VERSION=%%i
if not defined VERSION set VERSION=1.0
set PACKAGE_NAME=KeyQuest-Source-v%VERSION%-%DATESTR%

echo Creating package: %PACKAGE_NAME%
echo.

REM Create source directory if it doesn't exist
if not exist "source" mkdir "source"

REM Step 3: Create temporary directory
echo [3/4] Building package structure...
if exist "%PACKAGE_NAME%" rmdir /s /q "%PACKAGE_NAME%"
mkdir "%PACKAGE_NAME%"

echo Copying source files...

REM Copy main files
copy keyquest.pyw "%PACKAGE_NAME%\" >nul
copy README.md "%PACKAGE_NAME%\" >nul
copy docs\user\SOURCE_PACKAGE_README.txt "%PACKAGE_NAME%\EXTRACTION_INSTRUCTIONS.txt" >nul
copy requirements.txt "%PACKAGE_NAME%\" >nul
copy tools\build\KeyQuest-RootFolders.spec "%PACKAGE_NAME%\" >nul
copy progress.sample.json "%PACKAGE_NAME%\" >nul 2>nul
copy docs\dev\DEVELOPER_SETUP.md "%PACKAGE_NAME%\" >nul 2>nul
if exist COMPREHENSIVE_IMPROVEMENT_RESEARCH.md copy COMPREHENSIVE_IMPROVEMENT_RESEARCH.md "%PACKAGE_NAME%\" >nul
if exist INTEGRATION_TEST_CHECKLIST.md copy INTEGRATION_TEST_CHECKLIST.md "%PACKAGE_NAME%\" >nul
if exist TEST_RESULTS.md copy TEST_RESULTS.md "%PACKAGE_NAME%\" >nul

REM Copy directories
echo Copying modules...
xcopy /E /I /Q modules "%PACKAGE_NAME%\modules" >nul
if exist "%PACKAGE_NAME%\modules\__pycache__" (
    rmdir /s /q "%PACKAGE_NAME%\modules\__pycache__"
)

echo Copying games...
xcopy /E /I /Q games "%PACKAGE_NAME%\games" >nul
if exist "%PACKAGE_NAME%\games\__pycache__" (
    rmdir /s /q "%PACKAGE_NAME%\games\__pycache__"
)

echo Copying sentences...
xcopy /E /I /Q Sentences "%PACKAGE_NAME%\Sentences" >nul

echo Copying documentation...
xcopy /E /I /Q docs "%PACKAGE_NAME%\docs" >nul
if exist "%PACKAGE_NAME%\docs\.claude" (
    rmdir /s /q "%PACKAGE_NAME%\docs\.claude"
)

echo Copying ui...
xcopy /E /I /Q ui "%PACKAGE_NAME%\ui" >nul

REM Step 4: Create ZIP archive
echo.
echo [4/4] Creating ZIP archive...

REM Use PowerShell to create ZIP (built-in on Windows, uses forward slashes for cross-platform compatibility)
echo Using PowerShell to create ZIP archive...
powershell -command "Compress-Archive -LiteralPath '%PACKAGE_NAME%' -DestinationPath 'source\%PACKAGE_NAME%.zip' -Force"
if %ERRORLEVEL% EQU 0 (
    echo Archive created: source\%PACKAGE_NAME%.zip
    echo.
    echo Verifying ZIP structure...
    powershell -command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path 'source\%PACKAGE_NAME%.zip').Path); Write-Host 'Sample ZIP entries (should show folder structure):'; $zip.Entries | Select-Object -First 8 | ForEach-Object { Write-Host ('  ' + $_.FullName) }; $zip.Dispose(); Write-Host ''; Write-Host 'If entries show %PACKAGE_NAME%/ prefix with forward slashes, structure is correct.'"
) else (
    echo.
    echo ERROR: Failed to create ZIP archive.
    echo Please manually ZIP the folder: %PACKAGE_NAME%
    echo.
)

REM Clean up temporary directory
echo.
echo Cleaning up...
rmdir /s /q "%PACKAGE_NAME%"
if exist "modules\__pycache__" rmdir /s /q "modules\__pycache__"
if exist "games\__pycache__" rmdir /s /q "games\__pycache__"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo ========================================
echo Packaging complete!
echo ========================================
echo.
echo Source package ready for distribution: source\%PACKAGE_NAME%.zip
echo.

REM Keep window open
if not defined NO_PAUSE pause
popd
