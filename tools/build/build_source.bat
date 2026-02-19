@echo off
REM build_source.bat (Deprecated)
REM Use create_source_package.bat (more robust date formatting + ZIP verification).

echo ========================================
echo KeyQuest Source Package Builder (Deprecated)
echo ========================================
echo.
echo This script is deprecated.
echo Calling create_source_package.bat...
echo.

call "%~dp0create_source_package.bat" --nopause
exit /b %ERRORLEVEL%
