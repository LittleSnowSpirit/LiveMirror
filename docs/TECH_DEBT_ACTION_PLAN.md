# LiveMirror 技术债执行计划

更新时间：2026-04-20

## 目标

先保护当前可运行的核心闭环，再逐个转正历史实验模块。核心闭环包括注册登录、上传、任务状态、报告、导出、归因、建议、趋势和浏览器 E2E。

## 已完成

- 根目录已初始化 Git，并建立 `chore: establish project baseline` 基线提交。
- `.gitignore` 已补齐本地生成物、缓存、日志、数据库、覆盖率和 E2E runtime 忽略规则。
- 后端主入口改为 app factory，并通过 feature registry 统一挂载路由。
- 新增 `/api/features`，返回模块清单、启用状态、前端导航入口和健康状态。
- `/api/features`、归因、建议、趋势等业务 API 已纳入登录态保护。
- SQLAlchemy SQLite 文件库启用 WAL 和 `synchronous=NORMAL`；`StaticPool` 只用于内存 SQLite。
- `tasks` 表新增向后兼容字段：`current_step`、`provider`、`started_at`。
- `LIVEMIRROR_RUN_EXPERIMENTAL_TESTS=1 python -m pytest -q` 已能收集并通过后端历史实验测试；目前仍有旧测试函数 `return` 非 None 的 pytest 警告。
- 实时/运营监控模块的旧测试契约已恢复，包括异步场控测试、竞品监控服务测试和监控路由兼容别名。
- 前端路由已改为懒加载，受保护页面未登录时跳转登录并保留返回地址。
- 前端正式加入 `pinia` 和 `echarts`；Pinia 已在应用入口注册。
- 前端鉴权逻辑收敛到 `src/api/index.ts` 的单一 axios 客户端，旧 `utils/auth.js` 仅保留兼容导出。
- Vite 已按 Vue、Element Plus、ECharts 和其他 vendor 做基础分包。
- `core.yml` 继续作为核心门禁；`test.yml` 改为手动/夜间 full workflow。

## 待转正模块

每个模块按同一流程推进：后端 import/mount 测试、鉴权测试、成功路径、失败路径、前端 API 封装、类型、导航入口、最小 E2E。

- 实时/运营：WebSocket、实时看板、敏感词、竞品监控
- 商业增长：ROI、投放、A/B、选品、标题优化
- 工具模块：批量导出、脚本策划、培训、装修、票券

## 仍需处理

- 引入 Alembic，替代当前 SQLite 兼容补丁作为正式迁移机制。
- 将趋势、归因、建议中的示例数据迁入数据库查询。
- 用统一后台任务队列替代散落的线程、旧 runner 和临时 async loop。
- 本地 Whisper 继续补强：模型懒加载缓存、FFmpeg/模型预检、长音频分段、可读错误和测试环境 mock 回退边界。
- 超过 700 行的 Vue 页面按“页面容器 + API composable + 表格/图表/表单组件”拆分。
- 图表组件统一走 ECharts wrapper，避免每页重复初始化、resize 和 dispose。
- 生产构建仍有 `vendor-element-plus` 超过 Vite 默认 500 kB 警告；当前原因是应用全量注册 Element Plus，后续应改为按需导入或组件级分包。

## 验收命令

```powershell
python -m pytest -q
python -m pytest backend\tests\test_core_api.py -q
npm run typecheck
npm run build
python -m pytest tests\e2e_core -q
```

全量实验模块验收：

```powershell
$env:LIVEMIRROR_RUN_EXPERIMENTAL_TESTS = "1"
python -m pytest -q
```
