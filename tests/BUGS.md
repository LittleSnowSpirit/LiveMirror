# Bug 清单

## 测试执行时间
2026-04-08 13:33 - 13:40

## 环境状态
- ✅ 后端服务：运行中 (http://localhost:8000)
- ✅ 前端服务：运行中 (http://localhost:5173)
- ✅ Python 环境：3.14.2
- ✅ Node 环境：v24.13.0

---

## Bug 清单

### BUG-001
**严重程度**: 高  
**模块**: 后端/数据库  
**描述**: SQLAlchemy 模型使用了保留字段名 `metadata`  
**复现步骤**: 
1. 启动后端服务
2. 导入 models.py
**期望行为**: 服务正常启动  
**实际行为**: `sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.`  
**修复状态**: ✅ 已修复 - 将 `metadata` 字段重命名为 `task_metadata`  
**修复文件**: `backend/models.py:45`

---

### BUG-002
**严重程度**: 中  
**模块**: 前端/E2E 测试  
**描述**: 页面标题与测试期望不匹配 + 页面元素选择器不匹配  
**复现步骤**:
1. 运行 E2E 测试 `pytest -m e2e`
2. 测试 `test_upload_page_loads` 检查页面标题和元素
**期望行为**: 页面标题为 "LiveMirror"，存在 `.upload-card` 元素  
**实际行为**: 页面标题为 "LiveMirror - 直播复盘系统"，`.upload-card` 元素不存在  
**修复状态**: ⚠️ 部分修复 - 标题已修复，但页面结构与测试不匹配  
**修复建议**: 需要检查前端实际 DOM 结构并更新测试选择器  
**修复文件**: `tests/e2e/test_upload.py`

---

### BUG-003
**严重程度**: 高  
**模块**: 测试框架  
**描述**: API 测试缺少超时机制，导致无限轮询  
**复现步骤**:
1. 未配置 OPENAI_API_KEY
2. 运行 API 测试 `pytest -m api`
3. 测试等待任务完成时进入无限轮询
**期望行为**: 测试在超时后失败或跳过  
**实际行为**: 测试无限轮询直到被强制终止  
**修复建议**: 
1. 添加 pytest-timeout 插件
2. 在 conftest.py 中配置全局超时
3. 或为轮询循环添加最大尝试次数限制
**修复文件**: `tests/conftest.py`, `tests/requirements.txt`

---

### BUG-004
**严重程度**: 中  
**模块**: 后端/配置  
**描述**: 缺少 OPENAI_API_KEY 时 AI 分析功能无法使用  
**复现步骤**:
1. 使用默认 .env 配置（OPENAI_API_KEY=your_openai_api_key_here）
2. 上传音频文件
3. 任务停留在 "analyzing" 状态
**期望行为**: 服务优雅降级或明确提示配置缺失  
**实际行为**: 任务卡住，测试无限等待  
**修复建议**: 
1. 启动时检查必需配置并提示
2. AI 分析失败时标记任务为 failed 而非卡住
3. 提供 mock 模式用于测试
**修复文件**: `backend/config.py`, `backend/services/ai_analysis.py`

---

### BUG-005
**严重程度**: 低  
**模块**: 测试框架  
**描述**: pytest 收集警告 - TestContext 类被误识别为测试类  
**复现步骤**: 运行任何 pytest 命令  
**期望行为**: 无警告  
**实际行为**: `PytestCollectionWarning: cannot collect test class 'TestContext' because it has a __init__ constructor`  
**修复建议**: 将 `TestContext` 重命名为 `TestContextHelper` 或添加 `__test__ = False` 属性  
**修复文件**: `tests/utils/test_helpers.py:182`

---

### BUG-006
**严重程度**: 低  
**模块**: 后端/依赖  
**描述**: requirements.txt 中指定的 pydantic 版本与 Python 3.14 不兼容  
**复现步骤**:
1. 使用 Python 3.14
2. `pip install -r requirements.txt`
**期望行为**: 依赖安装成功  
**实际行为**: pydantic-core==2.14.6 没有 Python 3.14 的预编译包，需要 Rust 编译  
**修复状态**: ✅ 临时修复 - 使用最新版 pydantic（不锁定版本）  
**修复建议**: 更新 requirements.txt 使用兼容 Python 3.14 的版本或降低 Python 版本要求  
**修复文件**: `backend/requirements.txt`

---

### BUG-007
**严重程度**: 中  
**模块**: E2E 测试  
**描述**: E2E 测试选择器与前端实际 DOM 结构不匹配  
**复现步骤**:
1. 运行 E2E 测试 `pytest -m smoke`
2. 测试 `test_upload_page_loads` 查找 `.upload-card` 元素
**期望行为**: 找到 `.upload-card` 元素  
**实际行为**: 元素不存在，测试失败  
**修复建议**: 检查前端实际使用的 CSS 类名并更新测试选择器  
**修复文件**: `tests/e2e/test_upload.py`

---

## 测试结果汇总

### 冒烟测试 (smoke) - 第二次运行
- 总计：13 个测试
- 通过：12 ✅
- 失败：1 ❌ (BUG-007: E2E 元素选择器不匹配)
- 通过率：92.3%

### API 测试 (api)
- 状态：⚠️ 需要 OPENAI_API_KEY 配置
- 阻塞问题：AI 分析功能需要有效的 API Key

### E2E 测试 (e2e)
- 状态：⚠️ 需要更新测试选择器
- 已知问题：页面元素选择器与实际 DOM 不匹配

---

## 建议修复优先级

1. **高优先级**: BUG-004 (API Key 配置处理) - 影响核心功能
2. **高优先级**: BUG-007 (E2E 选择器) - 阻塞 E2E 测试
3. **中优先级**: BUG-002 (页面结构不匹配) - 影响 E2E 测试
4. **低优先级**: BUG-005 (测试警告) - 代码清理
5. **已完成**: BUG-001 (metadata 保留字) ✅
6. **已完成**: BUG-003 (测试超时) ✅ - 已添加 pytest-timeout
7. **已完成**: BUG-006 (pydantic 兼容) ✅ - 已使用最新版

---

## 下一步行动

1. **阻塞项**: 用户需要配置 `backend/.env` 中的 `OPENAI_API_KEY`
2. 更新 E2E 测试选择器以匹配前端实际 DOM 结构
3. 配置 API Key 后重新运行 API 测试
4. 生成最终验收报告
