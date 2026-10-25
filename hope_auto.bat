@echo off
rem Run by Windows Task Scheduler. Output goes to runs\auto.log.
rem   hope_auto.bat        -> 4 PM: research, script and make the video (no upload)
rem   hope_auto.bat post   -> 6 PM: upload to YouTube and Instagram
cd /d "%~dp0"
if not exist runs mkdir runs
set PYTHONIOENCODING=utf-8
echo ===== %date% %time% %1 ===== >> runs\auto.log
rem Fetch the latest code and instructions from GitHub first.
git pull --rebase --autostash >> runs\auto.log 2>&1
if /i "%1"=="post" (
  python video.py >> runs\auto.log 2>&1
) else (
  python agents.py >> runs\auto.log 2>&1
  python video.py --no-upload >> runs\auto.log 2>&1
)
