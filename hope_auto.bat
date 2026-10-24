@echo off
rem Run by Windows Task Scheduler. Output goes to runs\auto.log.
cd /d "%~dp0"
if not exist runs mkdir runs
set PYTHONIOENCODING=utf-8
echo ===== %date% %time% ===== >> runs\auto.log
rem Fetch the latest code and instructions from GitHub first.
git pull --rebase --autostash >> runs\auto.log 2>&1
python agents.py >> runs\auto.log 2>&1
python video.py >> runs\auto.log 2>&1
