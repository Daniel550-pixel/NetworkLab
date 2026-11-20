@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher (py.exe) niet gevonden. Installeer Python 3.10 of hoger.
  pause
  exit /b 1
)
py ".\wifi_profile_manager.py"
if errorlevel 1 (
  echo De applicatie is afgesloten met een fout.
  pause
)
