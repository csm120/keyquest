@echo off
setlocal EnableExtensions

REM Build a stable-name portable ZIP for release uploads.
REM Usage:
REM   tools\build\build_portable_zip.bat
REM   tools\build\build_portable_zip.bat --nopause

set "NO_PAUSE=0"
if /I "%~1"=="--nopause" set "NO_PAUSE=1"

pushd "%~dp0\..\.."

echo ========================================
echo KeyQuest Portable ZIP Builder
echo ========================================
echo.

if not exist "dist\KeyQuest\KeyQuest.exe" (
    echo ERROR: dist\KeyQuest\KeyQuest.exe not found.
    echo Build the executable first:
    echo   tools\build\build_exe.bat
    goto :fail
)

if exist "dist\KeyQuest-win64.zip" del /f /q "dist\KeyQuest-win64.zip"

tar -a -cf "dist\KeyQuest-win64.zip" -C "dist" "KeyQuest"
if errorlevel 1 (
    echo ERROR: Failed to create dist\KeyQuest-win64.zip
    goto :fail
)

echo.
echo Portable ZIP build complete:
echo   dist\KeyQuest-win64.zip
goto :done

:fail
echo.
echo Portable ZIP build failed.
if "%NO_PAUSE%"=="0" pause
popd
exit /b 1

:done
if "%NO_PAUSE%"=="0" pause
popd
exit /b 0
