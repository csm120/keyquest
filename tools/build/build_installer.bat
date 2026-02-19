@echo off
setlocal EnableExtensions

REM Build a Windows installer for KeyQuest using Inno Setup 6
REM Usage:
REM   tools\build\build_installer.bat
REM   tools\build\build_installer.bat --nopause

set "NO_PAUSE=0"
if /I "%~1"=="--nopause" set "NO_PAUSE=1"

pushd "%~dp0\..\.."

echo ========================================
echo KeyQuest Installer Builder
echo ========================================
echo.

if not exist "dist\KeyQuest\KeyQuest.exe" (
    echo ERROR: dist\KeyQuest\KeyQuest.exe not found.
    echo Build the executable first:
    echo   tools\build\build_exe.bat
    goto :fail
)

set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC_PATH (
    echo ERROR: Inno Setup compiler not found.
    echo Install Inno Setup 6 from:
    echo   https://jrsoftware.org/isdl.php
    goto :fail
)

set "APP_VERSION="
for /f "tokens=2 delims==" %%A in ('findstr /R /C:"__version__ *= *\".*\"" modules\version.py') do (
    set "APP_VERSION=%%~A"
)
set "APP_VERSION=%APP_VERSION:"=%"
set "APP_VERSION=%APP_VERSION: =%"
if "%APP_VERSION%"=="" set "APP_VERSION=1.0"

echo Building installer version %APP_VERSION% ...
"%ISCC_PATH%" /DMyAppVersion=%APP_VERSION% tools\build\installer\KeyQuest.iss
if errorlevel 1 goto :fail

echo.
echo Installer build complete:
echo   dist\installer\KeyQuestSetup.exe
goto :done

:fail
echo.
echo Installer build failed.
if "%NO_PAUSE%"=="0" pause
popd
exit /b 1

:done
if "%NO_PAUSE%"=="0" pause
popd
exit /b 0
