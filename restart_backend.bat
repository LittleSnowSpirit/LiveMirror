@echo off
chcp 65001 >nul
echo Restarting LiveMirror Backend...
taskkill /F /FI "WINDOWTITLE eq python main.py" 2>nul
timeout /t 2 /nobreak >nul
cd /d %~dp0\backend
start "LiveMirror Backend" python main.py
echo Backend restarted!
timeout /t 3 /nobreak >nul
