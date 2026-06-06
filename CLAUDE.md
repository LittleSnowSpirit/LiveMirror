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
- **Agent 角色按任务性质灵活分配**，不固定为"前端/后端"。举例：
  - UI 打磨 → "导航交互"（菜单+动画）+ "样式系统"（令牌+主题）+ "组件架构"（抽取+测试）
  - 报告分享 → "分享服务"（链接+API）+ "导出服务"（PDF+图片）+ "前端页面"（组件+页面）
  - 全栈功能 → "数据层"（模型+服务+API）+ "交互层"（页面+组件+测试）

约束：
- **Agent 必须指定 `model` 参数**：代码类用 `model: "sonnet"`，UI/图片类用 `model: "haiku"`（不传会 400 报错）
- 每个 Agent 负责 3-5 个相关任务，工作量要均衡
- 不要把所有同类任务丢给一个 Agent，按维度拆分并行
- Lead 先定义 API 合约，再启动 Teammate 并行开发
- Teammate 复杂任务先 Plan Mode，Lead 审核后执行

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

### 图谱社区命名规范

运行 `/graphify` 生成图谱时，社区标签必须遵守以下规则：

1. **所有社区名字必须是中文**，不得出现英文社区名（如 `Community 30`）
2. **每个社区都必须有名字**，即使是只有 1-2 个节点的小社区，也要根据其节点内容起名
3. 命名方式：读取社区内节点的 `label` 和 `source_file`，推断该社区的功能或主题，用 2-6 个中文字概括（如"弹幕分析"、"认证路由"、"前端页面组件"）
4. 命名后保存到 `graphify-out/.graphify_labels.json`，确保每个 key 都有对应的中文 value

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **LiveMirror** (5935 symbols, 10026 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/LiveMirror/context` | Codebase overview, check index freshness |
| `gitnexus://repo/LiveMirror/clusters` | All functional areas |
| `gitnexus://repo/LiveMirror/processes` | All execution flows |
| `gitnexus://repo/LiveMirror/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
