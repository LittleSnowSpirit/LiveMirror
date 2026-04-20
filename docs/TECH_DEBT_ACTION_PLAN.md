# LiveMirror 技术债务执行计划

更新时间：2026-04-15

## 目标

先保护当前可运行的核心闭环，再逐步收口历史实验模块。核心闭环包括注册登录、上传、任务状态、报告、导出、归因、建议和趋势页面。

## P0 已执行

- 清空本地 `.env` 中的 DashScope 明文 key，并在环境示例中补充 `SECRET_KEY`。
- 核心上传、任务、报告和导出接口统一要求登录态。
- 上传文件改为分块写入，超过 `MAX_FILE_SIZE` 时立即停止并删除半成品文件。
- 后台分析任务改用固定大小线程池，避免每次上传无限创建 daemon thread。
- 更新核心 API 测试和浏览器核心闭环测试，覆盖登录后主流程和未登录拒绝访问。

## P1 下一步

- 已完成：新增根级 `pytest.ini`，默认只运行当前支持的核心 API 测试。
- 已完成：新增 `core.yml` CI，覆盖核心后端 API、前端 typecheck/build、核心浏览器闭环。
- 已完成：旧 GitHub workflow 改为 legacy，默认分支触发已关闭。
- 已完成：核心模型、核心认证 token、任务完成时间已迁移为 timezone-aware datetime。
- 已完成：`backend/tests` 默认只收集核心测试；设置 `LIVEMIRROR_RUN_EXPERIMENTAL_TESTS=1` 时才收集历史实验测试。
- 已完成：A/B、竞品监控、预测三个漂移最明显的实验测试改为旧接口缺失时模块级跳过，避免收集阶段中断。
- 已完成：压缩 `config.py`、`database.py` 和 `services/database.py` 中的历史兼容层，核心配置和数据库连接只保留一套初始化入口。
- 已验证：`python -m pytest -q`、后端语法解析和 `tests/e2e_core` 均通过。
- 待处理：逐个修复历史实验测试的真实失败，包括异步 fixture、Windows 临时目录权限、monitor API 断言漂移和敏感词测试清理失败。

## P2 后续

- 决定真实转写路径：本地 faster-whisper 或 DashScope，不再保留多套半成品入口。
- 趋势分析接入真实历史任务数据，替换当前 mock sessions。
- 归因报告和配置改为持久化存储。
- 清理历史前端页面依赖，决定哪些实验页重新纳入构建和类型检查。
