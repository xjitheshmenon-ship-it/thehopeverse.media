@echo off
cd /d "%~dp0"
if "%ANTHROPIC_API_KEY%"=="" set /p ANTHROPIC_API_KEY=Paste your Anthropic API key and press Enter:
set /p GOAL=What should Hope do? (press Enter for the default):
if "%GOAL%"=="" set GOAL=Hope, introduce yourself and plan the first video for Hopeverse Media
python agents.py "%GOAL%"
pause
