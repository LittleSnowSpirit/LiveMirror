# LiveMirror

AI驱动的直播复盘分析系统。支持音视频转写、情绪归因分析、话术优化建议、跨场次趋势对比。

## 技术栈

- **后端**: Python 3.10+ / FastAPI / SQLAlchemy / Whisper (faster-whisper) / DashScope
- **前端**: Vue 3 / TypeScript / Vite / Element Plus / ECharts / Pinia

## 项目结构

```
backend/
  main.py              # FastAPI app factory, 路由动态加载
  features.py          # 功能注册表, 控制哪些路由被挂载
  models.py            # SQLAlchemy 数据模型
  config.py            # Pydantic Settings 配置
  routes/              # API 路由 (10个模块)
    core_auth.py       # 认证: /auth/*
    core_upload.py     # 上传: /api/upload
    core_tasks.py      # 任务: /api/task/:id
    core_reports.py    # 报告: /api/report/:id
    core_export.py     # 导出: /api/export/:id/:format
    attribution.py     # 归因分析: /api/attribution/*
    suggestions.py     # 话术建议: /api/suggestions/*
    trends.py          # 趋势分析: /api/trends/*
    monitor.py         # 竞品监控: /api/monitor/*
    features.py        # 功能列表: /api/features
  services/            # 业务逻辑层
  ai_analysis/         # AI 分析模块 (DeepSeek/GPT)
  tests/               # 后端测试

frontend/
  src/
    api/index.ts       # API 层 (axios 封装)
    views/             # 页面组件 (8个)
    components/        # 通用组件
    router/index.ts    # Vue Router 配置
    App.vue            # 根组件
```

## 常用命令

```bash
# 后端
cd backend
python3 -m uvicorn main:app --reload          # 启动开发服务器 (端口 8000)
python3 -m pytest tests/ -v                    # 运行后端测试
python3 -c "from main import app; print('OK')" # 验证导入

# 前端
cd frontend
npm run dev           # 启动开发服务器 (端口 3000)
npm run build         # 生产构建
npm run typecheck     # TypeScript 类型检查
npm run test          # 运行前端测试 (vitest)
```

## 路由认证

`main.py` 中自动为所有 `/api` 前缀的路由注入 `get_current_user` 依赖。无需手动添加。

## 测试约定

- 后端: pytest, 测试文件在 `backend/tests/`
- 前端: vitest + @vue/test-utils, 测试文件与源文件同目录 (`*.test.ts`)
- Element Plus 组件在测试中需要 mock (vitest 环境不支持 CSS 导入)

## 提交规范

- **每个开发阶段完成后必须提交代码**，不要积累大量变更后再提交
- 提交信息格式：`<type>: <简短描述>`，type 包括 feat/fix/chore/docs/refactor/test
- 描述说明这批变更做了什么，不要罗列文件清单
- 敏感文件（.env、credentials）禁止提交，.env.example 可以

## 构建注意事项

- Element Plus 使用显式 import (`import { ElMessage } from 'element-plus'`), 不依赖 AutoImport
- vite.config.mjs 中不要为 element-plus 设置 manualChunks, 否则会阻止 tree-shaking
- Python 3.10 兼容: 使用 `datetime.timezone.utc` 而非 `datetime.UTC` (3.11+)

## Agent Team 协作

**必须使用 Agent Team 工具（TeamCreate），不要用 subagent。** 用户需要在 UI 中看到团队状态和任务进度。

开发流程：
1. **需求问答**：用 AskUserQuestion 多问问题，充分确认需求
2. **任务规划**：用 TaskCreate 创建任务列表，模块分明、分类明确、任务量够大
3. **创建团队**：用 TeamCreate 创建团队
4. **分配任务**：用 Agent（带 team_name）启动 Teammate，用 TaskUpdate 分配 owner
5. **并行开发**：Teammate 各自认领任务执行
6. **验收提交**：Lead 验证后统一提交

角色分工：
- **Team Lead**：只协调，不写代码（Delegate Mode）
- **数据层 Agent**：数据库、服务层、API 路由、后端测试
- **交互层 Agent**：前端页面、API 客户端、状态管理、前端测试
- **基建 Agent**：Docker、CI/CD、PWA、部署脚本

约束：
- **Agent 必须指定 `model` 参数**：代码类用 `model: "sonnet"`，UI/图片类用 `model: "haiku"`（不传会 400 报错）
- Lead 先定义 API 合约，再启动 Teammate 并行开发
- Teammate 复杂任务先 Plan Mode，Lead 审核后执行
- 每个 Agent 负责 3-5 个相关任务，不要拆太细
