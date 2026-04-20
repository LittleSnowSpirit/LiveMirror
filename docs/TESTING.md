# LiveMirror 测试规范

> 📌 **版本**: V0.1  
> **最后更新**: 2026-04-08  
> **执行代理**: 自动化测试代理

---

## 📋 测试策略

### 测试金字塔

```
        ╱╲
       ╱  ╲      E2E 测试 (10%)
      ╱────╲    
     ╱      ╲   集成测试 (20%)
    ╱────────╲  
   ╱          ╲ 单元测试 (70%)
  ╱────────────╲
```

---

## 🧪 测试类型

### 1. 单元测试

**目标**: 测试单个函数/组件

**后端示例**:
```python
# tests/unit/test_audio.py
def test_convert_audio_format():
    result = audio_service.convert_format("input.wav", "mp3")
    assert result.format == "mp3"
    assert result.duration > 0
```

**前端示例**:
```typescript
// tests/unit/components/AudioUploader.test.ts
describe('AudioUploader', () => {
  it('应该拒绝超过 2GB 的文件', async () => {
    // 测试逻辑
  })
})
```

---

### 2. 集成测试

**目标**: 测试模块间交互

**示例**:
```python
# tests/integration/test_upload_flow.py
def test_upload_to_transcription(client):
    # 1. 上传音频
    response = client.post("/api/upload", files={...})
    task_id = response.json()["task_id"]
    
    # 2. 查询状态
    status = client.get(f"/api/task/{task_id}")
    assert status.json()["status"] in ["processing", "completed"]
```

---

### 3. 端到端测试 (E2E)

**目标**: 模拟真实用户操作

**Playwright 示例**:
```python
# tests/e2e/test_full_flow.py
async def test_user_upload_and_view_report(page):
    # 1. 打开首页
    await page.goto("http://localhost:5173")
    
    # 2. 上传音频
    await page.locator('input[type="file"]').set_files(
        "tests/fixtures/sample.mp3"
    )
    
    # 3. 等待转写完成
    await expect(page.locator('.status')).toHaveText('分析完成', timeout=60000)
    
    # 4. 查看报告
    await page.click('text=查看报告')
    await expect(page.locator('.emotion-chart')).toBeVisible()
    
    # 5. 测试筛选功能
    await page.click('text=只看翻车')
    await expect(page.locator('.issue-card')).toBeVisible()
```

---

## 📊 测试用例清单

### 音频上传模块

| 用例 ID | 测试场景 | 预期结果 | 优先级 |
|--------|----------|----------|--------|
| UP-01 | 上传合法 MP3 文件 | 返回 task_id，状态 processing | P0 |
| UP-02 | 上传 WAV 文件 | 返回 task_id，状态 processing | P0 |
| UP-03 | 上传 M4A 文件 | 返回 task_id，状态 processing | P0 |
| UP-04 | 上传不支持格式 (FLAC) | 返回 415 错误 | P0 |
| UP-05 | 上传超过 2GB 文件 | 返回 413 错误 | P0 |
| UP-06 | 空文件上传 | 返回 400 错误 | P1 |
| UP-07 | 网络中断后重试 | 支持断点续传（可选） | P2 |

### 任务状态查询

| 用例 ID | 测试场景 | 预期结果 | 优先级 |
|--------|----------|----------|--------|
| TS-01 | 查询处理中任务 | 返回 processing + 进度 | P0 |
| TS-02 | 查询已完成任务 | 返回 completed | P0 |
| TS-03 | 查询失败任务 | 返回 failed + 错误信息 | P0 |
| TS-04 | 查询不存在任务 | 返回 404 | P0 |

### 报告展示

| 用例 ID | 测试场景 | 预期结果 | 优先级 |
|--------|----------|----------|--------|
| RP-01 | 查看完整报告 | 显示所有话术卡片 | P0 |
| RP-02 | 筛选爆点话术 | 只显示爆点卡片 | P0 |
| RP-03 | 筛选翻车话术 | 只显示翻车卡片 | P0 |
| RP-04 | 情绪曲线渲染 | ECharts 正常显示 | P0 |
| RP-05 | 导出 PDF | 下载成功 | P1 |
| RP-06 | 长报告性能 | 虚拟滚动，无卡顿 | P1 |

---

## 🔄 持续测试流程

### 开发阶段

```
代码提交 → 运行单元测试 → 失败则通知开发代理 → 修复后重试
```

### 联调阶段

```
前后端完成 → 运行集成测试 → 运行 E2E 测试 → 生成测试报告
```

### 监控阶段

```
每 30 分钟 → 运行核心 E2E 测试 → 失败则记录并通知
```

---

## 📝 测试报告模板

```markdown
# 测试报告 - YYYY-MM-DD

## 测试概览
- 测试开始时间：...
- 测试结束时间：...
- 总用例数：...
- 通过：...
- 失败：...
- 跳过：...

## 失败用例详情

### 用例 ID: UP-04
**场景**: 上传不支持格式
**预期**: 返回 415 错误
**实际**: 返回 500 错误
**错误日志**: ...
**截图**: `screenshots/UP-04-fail.png`
**建议修复**: ...

## 性能数据
- 平均上传时间：2.3s
- 平均转写时间：45s (3 分钟音频)
- 报告渲染时间：1.2s

## 阻塞性问题
- [ ] 无
- [x] 问题描述：...

## 下一步建议
1. 修复 UP-04 用例
2. 优化大文件上传性能
3. 添加更多边界测试
```

---

## 🛠️ 测试工具配置

### 后端 (pytest)

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --cov=backend --cov-report=html
```

### 前端 (Vitest)

```typescript
// vitest.config.ts
export default {
  test: {
    environment: 'jsdom',
    coverage: {
      reporter: ['html', 'text'],
    },
  },
}
```

### E2E (Playwright)

```typescript
// playwright.config.ts
export default {
  testDir: './tests/e2e',
  timeout: 60000,
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
}
```

---

## ⚠️ 注意事项

1. **测试数据隔离**: 使用临时数据库/文件，不影响开发环境
2. **失败截图**: E2E 失败时自动截图保存
3. **测试时长控制**: 单测<30 秒，E2E<5 分钟
4. **环境检查**: 测试前确认后端/前端服务已启动
5. **清理工作**: 测试后清理临时文件

---

*测试代理持续维护此文档，发现新测试场景及时补充*
