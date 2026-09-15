@echo off
rem Double-clickable launcher: runs run.ps1 without needing to change the execution policy.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
