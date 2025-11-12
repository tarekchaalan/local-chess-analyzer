@echo off
setlocal
REM One-click launcher for Windows
REM - Starts PowerShell and runs scripts\run-images.ps1
REM - Keeps the window open on completion for visibility

set "ROOT=%~dp0"
set "PS=powershell.exe"

REM Prefer pwsh if available
where pwsh.exe >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PS=pwsh.exe"
)

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\run-images.ps1"
set "EC=%ERRORLEVEL%"
echo.
if "%EC%"=="0" (
  echo Local Chess Analyzer launched successfully. You can close this window.
) else (
  echo The launcher exited with error code %EC%.
)
echo.
pause
exit /b %EC%


