# LiveMirror 自动化测试

## 目录结构

```
tests/
├── api/                    # API 集成测试
│   ├── test_upload_api.py  # 上传接口测试
│   ├── test_task_api.py    # 任务状态接口测试
│   └── test_report_api.py  # 报告接口测试
├── e2e/                    # 端到端测试
│   ├── test_upload.py      # 上传流程 E2E 测试
│   ├── test_report.py      # 报告展示 E2E 测试
│   └── fixtures/           # 测试数据
├── utils/                  # 测试工具
│   └── test_helpers.py     # 辅助函数
├── conftest.py             # Pytest 配置
├── pytest.ini              # Pytest 设置
├── requirements.txt        # 测试依赖
├── run_tests.ps1           # 测试运行脚本
└── README.md               # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
cd tests
pip install -r requirements.txt
playwright install chromium
```

### 2. 启动服务

确保后端和前端服务正在运行：

```bash
# 后端（端口 8000）
cd backend
python main.py

# 前端（端口 5173）
cd frontend
npm run dev
```

### 3. 运行测试

#### 运行所有测试

```bash
pytest
```

#### 运行特定类型测试

```bash
# API 测试
pytest -m api

# E2E 测试
pytest -m e2e

# 快速冒烟测试
pytest -m smoke

# 上传相关测试
pytest -m upload

# 报告相关测试
pytest -m report
```

#### 使用 PowerShell 脚本

```powershell
# 运行所有测试
.\run_tests.ps1 -TestType all

# 只运行 API 测试
.\run_tests.ps1 -TestType api

# 带覆盖率报告
.\run_tests.ps1 -TestType all -Coverage

# 生成 HTML 报告
.\run_tests.ps1 -TestType all -HtmlReport
```

### 4. 查看报告

测试完成后会生成：

- `report.html` - HTML 测试报告
- `coverage_html/` - 代码覆盖率报告

## 测试标记

| 标记 | 说明 | 使用场景 |
|------|------|----------|
| `api` | API 集成测试 | 后端接口测试 |
| `e2e` | 端到端测试 | 完整用户流程 |
| `smoke` | 冒烟测试 | 快速验证核心功能 |
| `upload` | 上传测试 | 音频上传相关 |
| `report` | 报告测试 | 报告展示相关 |
| `slow` | 慢速测试 | 耗时较长的测试 |

## 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TEST_BASE_URL` | http://localhost:8000 | 后端 API 地址 |
| `TEST_FRONTEND_URL` | http://localhost:5173 | 前端地址 |
| `TEST_TIMEOUT` | 30 | 请求超时（秒） |

### pytest.ini 配置

```ini
[pytest]
# 超时设置
timeout = 300

# 日志级别
log_cli = true
log_cli_level = INFO
```

## 持续监控模式

### 本地监控脚本

创建 `monitor_tests.py`：

```python
import subprocess
import time
from datetime import datetime

def run_tests():
    """运行测试并记录结果"""
    result = subprocess.run(
        ['pytest', '-m', 'smoke', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    timestamp = datetime.now().isoformat()
    status = "PASS" if result.returncode == 0 else "FAIL"
    
    with open('test_log.txt', 'a') as f:
        f.write(f"{timestamp} - {status}\n")
    
    return result.returncode == 0

# 每 30 分钟运行一次
while True:
    run_tests()
    time.sleep(1800)  # 30 分钟
```

### 监控频率

- **开发中**: 每 30 分钟运行一次冒烟测试
- **提交前**: 运行完整测试套件
- **CI/CD**: 每次 push 自动运行

### 通知机制

测试失败时：

1. 记录到 `test_log.txt`
2. 截图保存证据（E2E 测试）
3. 发送通知（如果配置了）

## 编写新测试

### API 测试示例

```python
import pytest
import httpx

@pytest.mark.api
async def test_example(async_http_client: httpx.AsyncClient):
    response = await async_http_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### E2E 测试示例

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_example(page: Page, frontend_url: str):
    page.goto(frontend_url)
    expect(page).to_have_title("LiveMirror")
```

## 最佳实践

1. **测试独立性**: 每个测试应该独立，不依赖其他测试的状态
2. **使用临时数据**: 使用 `tmp_path` fixture 创建临时文件
3. **清理资源**: 使用 `cleanup_tasks` fixture 自动清理测试任务
4. **合理超时**: 设置合适的超时时间，避免测试卡住
5. **有意义的断言**: 断言应该清晰表达测试意图
6. **失败截图**: E2E 测试失败时自动截图

## 故障排查

### 常见问题

#### 1. 测试连接失败

```bash
# 检查服务是否运行
curl http://localhost:8000/health
curl http://localhost:5173
```

#### 2. Playwright 浏览器问题

```bash
# 重新安装浏览器
playwright install chromium
```

#### 3. 数据库连接失败

```bash
# 检查数据库配置
echo $DATABASE_URL
```

### 调试技巧

```bash
# 运行单个测试
pytest tests/api/test_upload_api.py::TestUploadAPI::test_upload_valid_audio -v

# 显示打印输出
pytest -s

# 失败后进入调试
pytest --pdb

# 增加详细程度
pytest -vvv
```

## CI/CD 集成

GitHub Actions 配置在 `.github/workflows/test.yml`：

- **push/PR**: 自动运行测试
- **每日调度**: 每天运行完整测试
- **工件上传**: 保存测试报告和覆盖率

## 性能优化

1. **并行执行**: 使用 `pytest-xdist` 并行运行测试
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

2. **测试缓存**: 使用 `pytest-cache` 缓存测试结果

3. **选择性运行**: 只运行变更相关的测试

## 贡献指南

1. 新功能必须包含测试
2. 保持测试覆盖率 > 80%
3. 遵循现有测试风格
4. 提交前运行完整测试套件

## 许可证

与主项目相同
