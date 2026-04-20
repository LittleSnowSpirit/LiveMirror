@echo off
chcp 65001 >nul
echo Starting LiveMirror Backend...
cd /d %~dp0\backend
python main.py
pause
