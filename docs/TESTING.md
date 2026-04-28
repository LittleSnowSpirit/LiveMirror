# LiveMirror 测试规范

最后更新：2026-04-20

## 当前门禁

本地改动完成前至少运行：

```powershell
python -m pytest backend\tests\test_core_api.py -q
npm run typecheck
npm run build
python -m pytest tests\e2e_core -q
```

大范围后端或跨端改动还需要运行：

```powershell
python -m pytest -q
```

历史实验模块的全量验收使用显式开关：

```powershell
$env:LIVEMIRROR_RUN_EXPERIMENTAL_TESTS = "1"
python -m pytest -q
```

## CI

- `.github/workflows/core.yml` 是必过门禁，覆盖后端核心 API、前端 typecheck/build 和核心浏览器闭环。
- `.github/workflows/test.yml` 是 full workflow，只在手动触发和夜间运行，用于逐步恢复历史模块测试。

## 后端模块转正规则

每恢复一个后端模块，必须补：

- import/mount 测试：模块可被 feature registry 挂载。
- 鉴权测试：未登录访问业务 `/api/**` 返回 401。
- 成功路径测试：至少一个核心业务接口返回预期结构。
- 失败路径测试：参数错误、资源缺失或状态不满足时返回稳定错误。

模块通过后，才能开启对应前端路由和导航入口。

## 前端页面转正规则

每恢复一个历史页面，必须补：

- API 封装和 TypeScript 类型。
- 路由懒加载入口，并标记 `meta.requiresAuth`。
- 最小 E2E：导航、渲染、主要操作。
- 如果使用 mock 数据，页面或技术债文档必须标明真实 API 替换任务。

## 核心闭环覆盖

核心 E2E 覆盖：

1. 注册并登录。
2. 上传音频文件。
3. 等待 mock 转写任务完成。
4. 查看报告。
5. 导出报告。
6. 访问归因、建议、趋势页面。

运行失败时，截图、trace 和前后端日志写入：

```text
tests/e2e_core/.runtime/artifacts/
```

## 性能与稳定性检查

- 上传大文件必须分块写入，不能一次性读入内存。
- Whisper 模型应懒加载并复用。
- Vite 构建应使用 route/vendor 分包；业务 route chunk 不应超过默认警告阈值。
- SQLite 文件库使用 WAL；内存测试库才使用 `StaticPool`。
