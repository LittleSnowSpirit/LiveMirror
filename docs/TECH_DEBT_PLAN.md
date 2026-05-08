# LiveMirror 技术债解决计划

> 更新时间：2026-05-07
> 版本：v1.0

---

## 目录

1. [总览](#总览)
2. [P0 - 高优先级](#p0---高优先级)
3. [P1 - 中优先级](#p1---中优先级)
4. [P2 - 低优先级](#p2---低优先级)
5. [验收标准](#验收标准)
6. [进度追踪](#进度追踪)

---

## 总览

| 优先级 | 类别 | 问题 | 影响范围 | 预估工作量 |
|--------|------|------|----------|------------|
| P0 | 前端 | ECharts 全量引入，无 tree-shaking | 13 个组件，包体积 | 2-3 天 |
| P0 | 前端 | Vue 页面文件过大（18 个超 700 行） | 可维护性 | 持续进行 |
| P1 | 后端 | 建议引擎硬编码 mock 数据 | suggestion_engine.py | 0.5 天 |
| P1 | 后端 | Whisper 服务文件重复（5 个文件） | 转写服务 | 1 天 |
| P1 | 后端 | 双任务队列并存 | task_runner.py / task_queue.py | 0.5 天 |
| P2 | 后端 | SQLite 兼容补丁未移除 | database.py | 0.5 天 |
| P2 | 后端 | Alembic 迁移仅 1 个 | 数据库演进 | 持续进行 |

---

## P0 - 高优先级

### 1. ECharts 模块化改造

**问题描述**

当前 13 个组件使用 `import * as echarts from 'echarts'` 全量引入，导致：
- `vendor-echarts` chunk 超过 500KB 警告
- 无法利用 tree-shaking 移除未使用的图表类型
- 每个组件重复编写 init/resize/dispose 逻辑

**涉及文件**

```
frontend/src/views/CompetitorMonitor.vue
frontend/src/components/PredictionChart.vue
frontend/src/components/ABTestChart.vue
frontend/src/components/CompareChart.vue
frontend/src/components/SpeechTypePie.vue
frontend/src/components/ScoreRadar.vue
frontend/src/components/TrendChart.vue
frontend/src/components/EmotionChart.vue
frontend/src/components/ReportTimeline.vue
frontend/src/components/attribution/AttributionGraph.vue
frontend/src/components/attribution/DanmuHeatmap.vue
frontend/src/components/attribution/EmotionCurve.vue
frontend/src/components/trends/TrendChart.vue
```

**执行步骤**

- [ ] **Step 1: 创建 ECharts 模块化注册文件**
  - 新建 `frontend/src/utils/echarts.ts`
  - 从 `echarts/core` 引入核心模块
  - 按需注册图表类型（BarChart, LineChart, PieChart, RadarChart, HeatmapChart, GraphChart）
  - 按需注册组件（TooltipComponent, LegendComponent, GridComponent, DataZoomComponent 等）

```typescript
// 示例结构
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, LineChart, PieChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

export default echarts
```

- [ ] **Step 2: 创建 `useChart` composable**
  - 新建 `frontend/src/composables/useChart.ts`
  - 封装 init / setOption / resize / dispose 生命周期
  - 自动监听窗口 resize
  - 支持主题切换

```typescript
// 示例接口
export function useChart(containerRef: Ref<HTMLElement | null>) {
  // 返回 { chart, setOption, dispose }
}
```

- [ ] **Step 3: 逐个迁移组件**
  - 将 `import * as echarts from 'echarts'` 替换为 `import echarts from '@/utils/echarts'`
  - 将手动 init/resize/dispose 替换为 `useChart` composable
  - 每迁移一个组件后运行 `npm run build` 验证包体积变化

- [ ] **Step 4: 验证**
  - `npm run build` 确认无报错
  - 检查 `vendor-echarts` chunk 大小是否下降
  - 浏览器中验证各图表正常渲染和交互

**验收标准**
- `vendor-echarts` chunk 降至 300KB 以下
- 所有图表组件正常工作
- 无 console 报错

---

### 2. Vue 大页面拆分

**问题描述**

18 个视图文件超过 700 行，最大的 `Decorator.vue` 达 1770 行。大文件导致：
- 代码难以理解和维护
- 组件职责不清晰
- 难以复用子功能

**涉及文件（按行数排序）**

| 文件 | 行数 | 拆分优先级 |
|------|------|------------|
| Decorator.vue | 1770 | 高 |
| Campaign.vue | 1671 | 高 |
| ROIAnalysis.vue | 1508 | 高 |
| Playback.vue | 1413 | 中 |
| ProductAI.vue | 1357 | 中 |
| TitleOptimizer.vue | 1215 | 中 |
| Training.vue | 1195 | 中 |
| SensitiveWords.vue | 1173 | 中 |
| ScriptPlanner.vue | 1107 | 中 |
| ExportPro.vue | 1078 | 低 |
| ReportGenerator.vue | 1057 | 低 |
| FanProfile.vue | 1037 | 低 |
| CompetitorMonitor.vue | 890 | 低 |
| Controller.vue | 860 | 低 |
| InstallGuide.vue | 831 | 低 |
| ABTesting.vue | 824 | 低 |
| Ticket.vue | 811 | 低 |
| AdCreative.vue | 809 | 低 |

**拆分原则**

每个页面按以下结构拆分：

```
views/SomePage.vue              # 页面容器（< 300 行）
components/some-page/
├── SomeTable.vue               # 表格组件
├── SomeForm.vue                # 表单组件
├── SomeChart.vue               # 图表组件
└── SomeDialog.vue              # 弹窗组件
composables/
└── useSomePage.ts              # 页面逻辑和状态
```

**执行步骤**

- [ ] 从最小的文件开始（AdCreative.vue, 809 行）作为练手
- [ ] 分析页面结构，识别可拆分的独立区块
- [ ] 提取表格/列表为独立组件
- [ ] 提取表单/弹窗为独立组件
- [ ] 提取业务逻辑到 composable
- [ ] 每拆分一个页面后运行完整测试验证

**验收标准**
- 每个视图文件 < 500 行
- 拆分后的子组件可独立复用
- 页面功能无回归

---

## P1 - 中优先级

### 3. 移除建议引擎硬编码数据

**问题描述**

`suggestion_engine.py` 的 `recommend_excellent_examples` 方法（约第 438-500 行）包含硬编码的示例数据 `examples_db`，注释明确写着"实际应从数据库查询"。

**涉及文件**

```
backend/services/suggestion_engine.py (lines 438-500)
```

**执行步骤**

- [ ] **Step 1: 创建数据库模型**
  - 在 `backend/models.py` 中新增 `ExcellentExample` 模型
  - 字段：id, session_id, category, score, content, created_at

- [ ] **Step 2: 创建 Alembic 迁移**
  - `alembic revision --autogenerate -m "add excellent_examples table"`
  - 验证迁移脚本正确

- [ ] **Step 3: 创建种子数据脚本**
  - 新建 `backend/scripts/seed_excellent_examples.py`
  - 将当前硬编码数据转为种子数据

- [ ] **Step 4: 修改 service 逻辑**
  - 将 `examples_db` 替换为数据库查询
  - 保留排序和过滤逻辑

- [ ] **Step 5: 清理前端 mock 数据**
  - 检查 `TrendChart.vue` 等组件的 inline mockData
  - 确保后端返回完整数据，前端不再需要 fallback

**验收标准**
- `suggestion_engine.py` 中无硬编码数据
- 优秀案例可从数据库增删改查
- API 返回真实数据

---

### 4. Whisper 服务整合

**问题描述**

存在 5 个功能重叠的 Whisper 相关文件：
- `transcription.py` — Protocol 抽象 + LocalWhisper 实现（推荐保留）
- `whisper.py` — DashScope API 调用
- `whisper_gpu.py` — GPU 专用实现
- `whisper_local.py` — 本地转写变体
- `whisper_transcribe.py` — 另一个转写变体
- `dashscope_asr.py` — DashScope ASR 服务

**执行步骤**

- [ ] **Step 1: 分析各文件的调用关系**
  - 使用 grep 找出哪些路由/服务引用了这些文件
  - 确认 `transcription.py` 是否已覆盖所有场景

- [ ] **Step 2: 统一到 Protocol 抽象**
  - 保留 `transcription.py` 作为主入口
  - 将 `whisper_gpu.py` 的 GPU 优化逻辑合并到 `LocalWhisperTranscriptionService`
  - 将 `dashscope_asr.py` / `whisper.py` 封装为 `DashScopeTranscriptionService`
  - 在 `settings.transcription_provider` 中增加 `"dashscope"` 选项

- [ ] **Step 3: 迁移调用方**
  - 将所有直接引用旧文件的地方改为使用 `TranscriptionService` Protocol
  - 通过依赖注入获取具体实现

- [ ] **Step 4: 清理废弃文件**
  - 确认无引用后删除：
    - `whisper.py`
    - `whisper_gpu.py`
    - `whisper_local.py`
    - `whisper_transcribe.py`

- [ ] **Step 5: 增强转写能力**
  - 长音频分段（> 30 分钟自动切片）
  - FFmpeg 预检（格式/编码检查）
  - 模型加载进度反馈

**验收标准**
- 仅保留 `transcription.py` 和 `dashscope_asr.py`
- 所有转写请求通过统一 Protocol 调用
- 支持 local / dashscope / mock 三种 provider

---

### 5. 任务队列统一

**问题描述**

两套任务执行系统并存：
- `task_queue.py` — `BackgroundTaskQueue`（ThreadPoolExecutor，推荐）
- `task_runner.py` — `TaskRunner`（asyncio.Queue，已废弃）

**执行步骤**

- [ ] **Step 1: 找出 TaskRunner 的所有调用方**
  - `grep -r "TaskRunner\|task_runner" backend/`

- [ ] **Step 2: 逐个迁移到 BackgroundTaskQueue**
  - 保持接口兼容，只替换内部实现
  - 特别关注 `assistant_controller.py` 中的 `asyncio.create_task` 调用

- [ ] **Step 3: 删除 task_runner.py**
  - 确认无引用后删除

- [ ] **Step 4: 统一异步任务模式**
  - 长生命周期任务（如监控循环）使用 `asyncio.create_task`
  - 一次性后台任务使用 `BackgroundTaskQueue`

**验收标准**
- 仅保留 `task_queue.py`
- 所有后台任务通过统一队列执行
- 无废弃代码残留

---

## P2 - 低优先级

### 6. 移除 SQLite 兼容补丁

**问题描述**

`database.py` 中的 `ensure_database_compatibility()` 函数手动 ALTER TABLE 添加字段，是 Alembic 引入前的临时方案。

**执行步骤**

- [ ] 确认所有环境已运行 `alembic upgrade head`
- [ ] 删除 `ensure_database_compatibility()` 函数
- [ ] 删除相关调用代码
- [ ] 更新部署文档，要求首次部署运行 alembic 迁移

**验收标准**
- `database.py` 中无手动 SQL 补丁
- 数据库结构完全由 Alembic 管理

---

### 7. Alembic 迁移规范化

**问题描述**

目前仅有 1 个迁移文件，后续每次 schema 变更都需要规范的迁移流程。

**执行步骤**

- [ ] 建立迁移命名规范：`YYYYMMDDHHMM_description.py`
- [ ] 为 Step 3（excellent_examples 表）生成迁移
- [ ] 在 CI 中添加迁移检查步骤
- [ ] 更新开发文档，说明迁移流程

**验收标准**
- 每次 schema 变更都有对应迁移文件
- CI 能检测未提交的迁移

---

## 验收标准

每个技术债项完成后，需要通过以下检查：

```bash
# 后端测试
python -m pytest backend/tests/test_core_api.py -q

# 前端类型检查
cd frontend && npm run typecheck

# 前端构建
cd frontend && npm run build

# E2E 测试
python -m pytest tests/e2e_core -q

# 实验模块测试（可选）
LIVEMIRROR_RUN_EXPERIMENTAL_TESTS=1 python -m pytest -q
```

---

## 进度追踪

| # | 任务 | 优先级 | 状态 | 负责人 | 开始日期 | 完成日期 |
|---|------|--------|------|--------|----------|----------|
| 1 | ECharts 模块化改造 | P0 | ⬜ 未开始 | - | - | - |
| 2 | Vue 大页面拆分 | P0 | ⬜ 未开始 | - | - | - |
| 3 | 移除建议引擎硬编码数据 | P1 | ⬜ 未开始 | - | - | - |
| 4 | Whisper 服务整合 | P1 | ⬜ 未开始 | - | - | - |
| 5 | 任务队列统一 | P1 | ⬜ 未开始 | - | - | - |
| 6 | 移除 SQLite 兼容补丁 | P2 | ⬜ 未开始 | - | - | - |
| 7 | Alembic 迁移规范化 | P2 | ⬜ 未开始 | - | - | - |

---

## 附录：快速命令

```bash
# 查看当前包体积
cd frontend && npm run build -- --report

# 查找 ECharts 全量引入
grep -rn "import \* as echarts" frontend/src/

# 查找大文件
find frontend/src/views -name "*.vue" -exec wc -l {} + | sort -rn | head -20

# 查找 TaskRunner 引用
grep -rn "TaskRunner\|task_runner" backend/

# 查找 Whisper 相关文件
find backend/services -name "*whisper*" -o -name "*transcription*"
```
