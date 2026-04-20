#!/usr/bin/env pwsh
# LiveMirror 测试运行脚本

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "api", "e2e", "smoke", "upload", "report")]
    [string]$TestType = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$Coverage,
    
    [Parameter(Mandatory=$false)]
    [switch]$HtmlReport,
    
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "http://localhost:8000",
    
    [Parameter(Mandatory=$false)]
    [string]$FrontendUrl = "http://localhost:5173"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LiveMirror 自动化测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量
$env:TEST_BASE_URL = $BaseUrl
$env:TEST_FRONTEND_URL = $FrontendUrl

# 构建 pytest 命令
$pytestArgs = @()

# 根据测试类型添加标记
switch ($TestType) {
    "api" { $pytestArgs += "-m", "api" }
    "e2e" { $pytestArgs += "-m", "e2e" }
    "smoke" { $pytestArgs += "-m", "smoke" }
    "upload" { $pytestArgs += "-m", "upload" }
    "report" { $pytestArgs += "-m", "report" }
    "all" { 
        Write-Host "运行所有测试..." -ForegroundColor Green
    }
}

# 添加覆盖率选项
if ($Coverage) {
    $pytestArgs += "--cov=../backend"
    $pytestArgs += "--cov-report=html:coverage_html"
    $pytestArgs += "--cov-report=term-missing"
}

# 添加 HTML 报告选项
if ($HtmlReport) {
    $pytestArgs += "--html=test-report.html"
    $pytestArgs += "--self-contained-html"
}

# 添加详细输出
$pytestArgs += "-v"
$pytestArgs += "--tb=short"

Write-Host "测试配置:" -ForegroundColor Yellow
Write-Host "  后端 URL: $BaseUrl"
Write-Host "  前端 URL: $FrontendUrl"
Write-Host "  测试类型：$TestType"
Write-Host "  覆盖率：$(if ($Coverage) { '是' } else { '否' })"
Write-Host "  HTML 报告：$(if ($HtmlReport) { '是' } else { '否' })"
Write-Host ""

# 检查依赖
Write-Host "检查测试依赖..." -ForegroundColor Yellow

try {
    $pytestVersion = pytest --version 2>&1
    Write-Host "  ✓ pytest 已安装：$pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ pytest 未安装" -ForegroundColor Red
    Write-Host "  运行：pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

try {
    $pwVersion = playwright --version 2>&1
    Write-Host "  ✓ Playwright 已安装：$pwVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Playwright 未安装" -ForegroundColor Red
    Write-Host "  运行：playwright install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "开始运行测试..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 运行测试
try {
    pytest $pytestArgs
    $exitCode = $LASTEXITCODE
} catch {
    $exitCode = 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "  ✓ 所有测试通过!" -ForegroundColor Green
} else {
    Write-Host "  ✗ 部分测试失败" -ForegroundColor Red
    Write-Host "  查看详细报告：test-report.html" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan

# 生成覆盖率报告
if ($Coverage) {
    Write-Host ""
    Write-Host "覆盖率报告已生成：coverage_html/index.html" -ForegroundColor Cyan
}

exit $exitCode
