@echo off
rem One-time setup: saves your API key and runs Hope daily at 9:00 while you're logged in.
cd /d "%~dp0"
set /p KEY=Paste your Anthropic API key and press Enter: 
setx ANTHROPIC_API_KEY "%KEY%" >nul
schtasks /Create /SC DAILY /ST 09:00 /TN "Hope - Hopeverse Media" /TR "\"%~dp0hope_auto.bat\"" /F
echo.
echo Done. Hope will run every day at 9:00. To stop it: schtasks /Delete /TN "Hope - Hopeverse Media" /F
pause
