# LiveMirror 快速开始

这是一份只面向当前仓库真实状态的启动说明。默认可直接使用的主线是：注册登录、上传、任务进度、报告、导出、归因分析、话术建议、趋势分析和健康检查。

## 运行前准备

- Python 3.11 或更高版本
- Node.js 20.x
- FFmpeg：涉及音视频处理时需要

## 1. 配置后端环境

进入 `backend/`，复制示例文件为本地配置：

```bash
cd backend
copy .env.example .env
```

然后补充需要的值。至少要确认这些项：

- `DATABASE_URL`
- `UPLOAD_DIR`
- `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`（按你实际使用的服务填写）
- `WHISPER_MODEL`
- `WHISPER_LANGUAGE`

如果只想先看接口是否能起来，使用 SQLite 默认配置也可以。

## 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

或者：

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动后检查：

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器默认在 `http://localhost:3000`。

如果前端需要指向本地后端，检查 `frontend/.env` 里的：

- `VITE_API_BASE_URL=http://localhost:8000/api`
- `VITE_AUTH_BASE_URL=http://localhost:8000`
- `VITE_USE_MOCK=false`

## 4. 快速验证

最少确认五件事：

1. 后端 `docs` 能打开。
2. 前端首页能打开。
3. 注册、登录能成功。
4. 上传页面能创建任务并跳转报告页。
5. 后端 `/auth/*`、`/api/upload`、`/api/task/*`、`/api/report/*`、`/api/export/*`、`/api/attribution/*`、`/api/suggestions/*`、`/api/trends/*` 能被访问。

## 5. 跑核心浏览器测试

核心 E2E 测试会自动启动后端和前端。后端使用内存 SQLite 与 mock 转写 Provider，适合做稳定回归。

```bash
python -m pytest tests/e2e_core -q
```

失败时会在 `tests/e2e_core/.runtime/artifacts/` 里保留截图、trace 和前后端日志。

## 6. 当前不要误判为已完成的部分

- 竞品监控、选品、标题优化、装修、A/B 测试等页面
- WebSocket、自动化报表和旧实验接口

这些都还在继续收口，后续开发前先确认它们是否已经真正挂到主入口和主导航里。
