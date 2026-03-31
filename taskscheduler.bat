@echo off
REM Schedule bot to run on startup (Windows Task Scheduler)

cd /d %~dp0

setlocal enabledelayedexpansion

REM Create task
echo Creating Windows Task Scheduler entry...
echo.

REM Get full path to run_live.bat
for /f %%I in ('cd') do set fullpath=%%I

schtasks /create /tn "PolymarketBot" /tr "%fullpath%\run_live.bat" /sc onlogon /ru %USERNAME% /f

echo.
echo Task created! Bot will run on next login.
echo To remove: schtasks /delete /tn "PolymarketBot" /f
echo.
pause