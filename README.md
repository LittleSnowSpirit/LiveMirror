# LiveMirror

LiveMirror 是一个直播复盘分析项目。当前仓库已经收敛到一条可运行的核心分析主线：账号注册登录、上传、任务进度、报告、导出、话术归因分析、话术优化建议、趋势分析和健康检查。竞品监控、培训、选品、标题优化、装修、A/B 测试等实验模块仍保留源码，但不作为当前默认验收范围。

## 当前真实能力

### 后端默认入口
- `/auth/*`
- `/api/upload`
- `/api/task/{task_id}`
- `/api/report/{task_id}`
- `/api/export/{task_id}/{format}`
- `/api/attribution/*`
- `/api/suggestions/*`
- `/api/trends/*`
- `/health`

### 已实现的功能面
- 账号注册、登录、刷新令牌、查询当前用户
- 上传音视频文件并创建分析任务
- 使用 mock 或本地 Whisper Provider 执行转写与分析
- 查询任务状态、查看报告、导出 JSON 和 Markdown
- 话术归因分析：情绪峰值检测、话术与情绪关联、话术与弹幕关联、归因配置查看
- 话术优化建议：问题诊断、改写示例、完整分析、优秀话术推荐、批量分析
- 趋势分析：历史场次、情绪趋势、话术质量趋势、互动趋势、成长报告、场次对比
- 健康检查：后端服务存活状态

### 当前仓库里仍保留但未完全收口的部分
- 竞品监控、选品、标题优化、装修、A/B 测试等实验页面
- WebSocket、自动化报表和旧实验接口

这些内容可以作为后续继续开发的基础，但现在不应该在文档里写成已经完全可交付的主线功能。

## 项目结构

- `backend/`：FastAPI 后端、SQLAlchemy 模型、服务与路由
- `frontend/`：Vue 3 + TypeScript + Vite 前端
- `tests/`：测试代码与测试数据
- `uploads/`、`exports/`、`reports/`、`demo_output/`：本地生成物或示例产物目录，默认不应提交

## 运行方式

### 运行环境
- Python 3.11 或更高版本
- Node.js 20.x
- FFmpeg：涉及音视频处理时需要

### 后端启动
1. 进入 `backend/`。
2. 复制 `backend/.env.example` 为 `backend/.env`，再填写真实配置。
3. 安装依赖：`pip install -r requirements.txt`
4. 启动服务：`python main.py`

也可以使用：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端默认地址：`http://localhost:8000`
接口文档：`http://localhost:8000/docs`

### 前端启动
1. 进入 `frontend/`。
2. 安装依赖：`npm install`
3. 启动开发服务器：`npm run dev`

前端默认地址：`http://localhost:3000`

## 环境变量

### 后端 `backend/.env`
当前 `backend/config.py` 会读取以下变量：

- `OPENAI_API_KEY`：可选，保留给 OpenAI 相关能力
- `OPENAI_API_BASE`：OpenAI 接口地址，默认 `https://api.openai.com/v1`
- `DASHSCOPE_API_KEY`：通义千问 / DashScope 密钥
- `DASHSCOPE_MODEL`：默认模型名，常用值 `qwen-plus`
- `HOST`：后端监听地址，默认 `0.0.0.0`
- `PORT`：后端监听端口，默认 `8000`
- `DEBUG`：是否开启调试模式
- `UPLOAD_DIR`：上传文件保存目录，默认 `./uploads`
- `MAX_FILE_SIZE`：允许的最大文件大小，单位字节
- `ALLOWED_EXTENSIONS`：允许的文件后缀，逗号分隔
- `DATABASE_URL`：数据库连接串，默认 SQLite
- `WHISPER_MODEL`：语音转写模型名
- `WHISPER_LANGUAGE`：默认识别语言
- `LOG_LEVEL`：日志级别

### 前端 `frontend/.env`
当前前端部分页面和工具函数会读取这些变量：

- `VITE_API_BASE_URL`：后端业务 API 基地址，默认 `/api`
- `VITE_AUTH_BASE_URL`：认证 API 基地址，默认从 `/api` 推导到同源根路径
- `VITE_USE_MOCK`：是否启用 Mock 数据
- `VITE_PUSH_PUBLIC_KEY`：推送订阅公钥，留空即可

## 测试

### 后端核心 API

```bash
python -m pytest backend/tests/test_core_api.py -q
```

### 浏览器核心闭环

E2E 测试会自动启动后端 mock 转写服务和前端 Vite，用 Playwright 模拟注册、登录、上传、查看报告、导出和分析页面访问。

```bash
python -m pytest tests/e2e_core -q
```

失败时截图、trace、前后端日志会写入 `tests/e2e_core/.runtime/artifacts/`。

## 清理策略

这个仓库里会持续产生本地生成物，提交前请保持它们不进版本库：

- `node_modules/`
- `dist/`
- `.vite/`
- `__pycache__/`
- `.pytest_cache/`
- `coverage/`、`htmlcov/`
- `*.db`
- `uploads/` 下的本地上传产物
- `reports/`、`exports/`、`demo_output/` 等导出或示例产物

根目录 `.gitignore` 已经按这个方向补齐。若以后新增新的生成目录，也请继续按同一规则维护。

## 已知现状

- 当前后端主入口挂载核心闭环路由，实验路由默认不作为主线暴露。
- 默认转写 Provider 可用 mock 保证测试稳定；真实本地 Whisper/faster-whisper 仍需要按机器环境安装依赖和模型。
- 前端主导航只覆盖核心闭环，实验页面后续按模块巡检和修复。

## 备注

本仓库现在更适合作为“核心分析能力的可运行底座”，而不是把所有历史功能都当成已经完成的产品说明书。
