# LiveMirror

AI 驱动的直播复盘分析平台，基于 FastAPI + Vue 3 + DashScope 构建，为主播和运营团队提供从数据到决策的完整闭环。

## 核心功能

| 模块 | 功能说明 |
|------|----------|
| **智能转写** | 支持音视频上传，自动语音转写（Whisper） |
| **情绪分析** | 实时情绪峰值检测，精准捕捉观众情绪波动 |
| **话术归因** | 建立话术-情绪-弹幕三维关联，找到真正有效的表达 |
| **AI 优化建议** | 基于分析结果，AI 自动生成话术改写方案与优秀话术推荐 |
| **趋势洞察** | 多场次历史对比，追踪情绪趋势与话术质量变化 |
| **导出报告** | 支持 JSON / Markdown 多格式导出，便于二次分析 |

## 技术栈

**后端**
- FastAPI — 高性能 Python Web 框架
- SQLAlchemy — 数据持久化
- DashScope / 通义千问 — AI 大模型能力
- Whisper — 语音转文字

**前端**
- Vue 3 + Composition API
- TypeScript
- Vite — 快速构建工具

## 项目结构

```
LiveMirror/
├── backend/          # FastAPI 后端
│   ├── routes/       # API 路由
│   ├── services/     # 核心业务逻辑
│   ├── models/       # 数据模型
│   └── migrations/   # 数据库迁移
├── frontend/         # Vue 3 前端
│   └── src/
│       ├── views/    # 页面组件
│       ├── api/      # 接口封装
│       └── utils/    # 工具函数
├── docs/             # 接口文档
└── tests/            # 测试代码
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20.x
- FFmpeg（音视频处理需要）

### 后端启动

```bash
cd backend
cp .env.example .env    # 填写真实配置
pip install -r requirements.txt
python main.py
```

后端地址：`http://localhost:8000`
API 文档：`http://localhost:8000/docs`

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://localhost:3000`

## 环境变量

### 后端 `.env`

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DASHSCOPE_API_KEY` | 通义千问密钥 | — |
| `DASHSCOPE_MODEL` | 默认模型 | `qwen-plus` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./livemirror.db` |
| `WHISPER_MODEL` | 转写模型 | — |

### 前端 `.env`

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `VITE_API_BASE_URL` | 后端 API 地址 | `/api` |

## 接口一览

- `POST /api/upload` — 上传音视频文件
- `GET /api/task/{task_id}` — 查询分析任务状态
- `GET /api/report/{task_id}` — 获取分析报告
- `GET /api/export/{task_id}/{format}` — 导出报告
- `POST /api/attribution/analyze` — 话术归因分析
- `POST /api/suggestions/generate` — AI 话术优化建议
- `GET /api/trends/{task_id}` — 趋势分析数据
- `GET /health` — 健康检查

> 完整接口文档请访问 `/docs`

## 测试

```bash
# 后端单元测试
python -m pytest backend/tests/test_core_api.py -q

# 浏览器 E2E 测试
python -m pytest tests/e2e_core -q
```

## License

MIT