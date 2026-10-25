@echo off
rem One-time setup: saves your API key, then researches and makes a Short daily at 16:00 and posts it at 18:00.
cd /d "%~dp0"
set /p KEY=Paste your Anthropic API key and press Enter: 
setx ANTHROPIC_API_KEY "%KEY%" >nul
schtasks /Delete /TN "Hope - Hopeverse Media" /F >nul 2>&1
schtasks /Create /SC DAILY /ST 16:00 /TN "Hope - research" /TR "\"%~dp0hope_auto.bat\"" /F
schtasks /Create /SC DAILY /ST 18:00 /TN "Hope - post" /TR "\"%~dp0hope_auto.bat\" post" /F
schtasks /Create /SC HOURLY /TN "Hope - stats" /TR "\"%~dp0hope_auto.bat\" stats" /F
echo.
echo Done. Hope researches at 16:00 and posts at 18:00. To stop: schtasks /Delete /TN "Hope - research" /F  and  schtasks /Delete /TN "Hope - post" /F
pause
