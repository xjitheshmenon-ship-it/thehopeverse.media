@echo off
rem Run by Windows Task Scheduler. Output goes to runs\auto.log.
rem   hope_auto.bat        -> 4 PM: research, script and make the video (no upload)
rem   hope_auto.bat post   -> 6 PM: upload to YouTube and Instagram
rem   hope_auto.bat stats  -> hourly: send views and spend to the dashboard
cd /d "%~dp0"
if not exist runs mkdir runs
set PYTHONIOENCODING=utf-8
rem The hourly stats run skips git pull so it never disturbs a run in progress.
if /i "%1"=="stats" (
  python dashboard.py >> runs\stats.log 2>&1
  exit /b
)
echo ===== %date% %time% %1 ===== >> runs\auto.log
rem Fetch the latest code and instructions from GitHub first.
git pull --rebase --autostash >> runs\auto.log 2>&1
if /i "%1"=="post" (
  if defined TELEGRAM_TOKEN python approve.py collect >> runs\auto.log 2>&1
  python video.py >> runs\auto.log 2>&1
  rem Show today's spending report on screen.
  if defined TELEGRAM_TOKEN (python approve.py report >> runs\auto.log 2>&1) else (
    if exist runs\spend-report.md start "" notepad runs\spend-report.md
  )
  python dashboard.py >> runs\auto.log 2>&1
) else (
  python agents.py >> runs\auto.log 2>&1
  python video.py --no-upload >> runs\auto.log 2>&1
  if defined TELEGRAM_TOKEN python approve.py ask >> runs\auto.log 2>&1
)
