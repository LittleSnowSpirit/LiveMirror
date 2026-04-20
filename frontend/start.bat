@echo off
chcp 65001 >nul
echo ========================================
echo   LiveMirror 前端 - 快速启动脚本
echo ========================================
echo.

echo [1/3] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Node.js，请先安装 Node.js (https://nodejs.org/)
    pause
    exit /b 1
)
echo ✓ Node.js 已安装

echo.
echo [2/3] 安装依赖...
if not exist node_modules (
    call npm install
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo ✓ 依赖已安装
)

echo.
echo [3/3] 启动开发服务器...
echo.
echo 访问地址：http://localhost:5173
echo 按 Ctrl+C 停止服务
echo.
call npm run dev

pause
