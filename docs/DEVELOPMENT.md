# LiveMirror 开发规范

> 📌 **版本**: V0.1  
> **最后更新**: 2026-04-08  
> **适用范围**: 所有开发代理

---

## 📋 目录

1. [代码规范](#代码规范)
2. [文档规范](#文档规范)
3. [Git 规范](#git-规范)
4. [前后端协作](#前后端-协作)
5. [测试规范](#测试规范)

---

## 代码规范

### Python (后端)

```python
# 函数必须有类型注解
def process_audio(file_path: str, sample_rate: int = 44100) -> dict:
    """处理音频文件
    
    Args:
        file_path: 音频文件路径
        sample_rate: 采样率，默认 44100
        
    Returns:
        包含处理结果的字典
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 格式不支持
    """
    pass

# 使用 Pydantic 进行数据验证
class UploadRequest(BaseModel):
    file: UploadFile
    speaker_name: Optional[str] = None
    platform: Optional[str] = "抖音"
```

**工具**: `black` 格式化，`flake8` 检查，`mypy` 类型检查

---

### TypeScript/Vue (前端)

```typescript
// 组件必须使用 TypeScript
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AnalysisReport } from '@/types'

// Props 定义
interface Props {
  taskId: string
  autoPoll?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  autoPoll: true
})

// 类型安全的 API 调用
const fetchReport = async (taskId: string): Promise<AnalysisReport> => {
  const res = await api.get(`/api/report/${taskId}`)
  return res.data
}
</script>
```

**工具**: `eslint` + `prettier` 格式化

---

## 文档规范

### 必须写的文档

| 文档类型 | 位置 | 何时写 |
|----------|------|--------|
| API 文档 | `docs/API.md` | 接口开发完成后立即更新 |
| 模块说明 | 模块内 `README.md` | 模块完成后 |
| 变更日志 | `CHANGELOG.md` | 每次功能变更 |
| 测试报告 | `tests/REPORT.md` | 测试完成后 |

### 文档模板

**模块 README 模板**:
```markdown
# 模块名称

## 功能说明
一句话描述模块功能

## 核心函数/组件
- `functionName()`: 功能说明
- `ComponentName`: 功能说明

## 使用示例
```python
# 或 TypeScript 代码示例
```

## 依赖关系
- 依赖模块 A
- 被模块 B 依赖

## 注意事项
- 性能考虑
- 边界情况处理
```

---

## Git 规范

### 分支策略

```
main          # 主分支，可部署
├── dev       # 开发分支
│   ├── feature/backend-upload    # 功能分支
│   ├── feature/frontend-report
│   └── fix/whisper-timeout
```

### Commit 规范

```bash
# 格式：<type>(<scope>): <subject>

# 示例
feat(backend): 实现音频上传接口
fix(frontend): 修复报告页面加载失败
docs(api): 更新任务状态接口文档
test(e2e): 添加上传流程端到端测试
refactor(ai): 重构话术分析逻辑
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 重构
- `chore`: 构建/工具配置

---

## 前后端协作

### 接口变更流程

```
1. 后端先更新 docs/API.md
2. 前端 review API 变更
3. 前端更新 src/api/index.ts
4. 联调测试
5. 更新 CHANGELOG.md
```

### 联调检查清单

**后端开发完成后**:
- [ ] API 文档已更新
- [ ] Swagger UI 可访问
- [ ] 错误响应格式统一
- [ ] 日志记录完善

**前端开发完成后**:
- [ ] 所有 API 调用已封装
- [ ] 错误处理完善
- [ ] 加载状态显示
- [ ] 响应式布局测试

**联调前**:
- [ ] 后端服务启动正常
- [ ] 前端服务启动正常
- [ ] CORS 配置正确
- [ ] 接口联调测试通过

---

## 测试规范

### 单元测试

```python
# 后端测试示例 (pytest)
def test_audio_upload_success(client, test_audio_file):
    response = client.post(
        "/api/upload",
        files={"file": test_audio_file}
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
```

```typescript
// 前端测试示例 (Vitest)
import { describe, it, expect } from 'vitest'
import { AudioUploader } from '@/components'

describe('AudioUploader', () => {
  it('应该接受 MP3 文件', () => {
    // 测试逻辑
  })
})
```

### 端到端测试

```python
# Playwright 测试示例
async def test_full_upload_flow(page):
    await page.goto("http://localhost:5173")
    await page.locator('input[type="file"]').set_files(TEST_AUDIO_PATH)
    await expect(page.locator('.progress-bar')).toBeVisible()
    # ... 继续测试流程
```

### 测试覆盖率要求

| 模块 | 最低覆盖率 |
|------|-----------|
| 后端核心逻辑 | 80% |
| 前端核心组件 | 70% |
| API 接口 | 90% |

---

## 代码审查清单

**提交前自检**:
- [ ] 代码通过 linter 检查
- [ ] 单元测试通过
- [ ] 文档已更新
- [ ] 无敏感信息提交（API Key 等）
- [ ] Commit message 符合规范

---

## 问题上报流程

**代理遇到阻塞问题时**:

1. 先尝试自己解决（查文档/搜索）
2. 记录问题详情：
   - 问题描述
   - 已尝试的解决方案
   - 错误日志
3. 上报给主代理（小雪灵）
4. 等待用户决策（如需）

**上报模板**:
```markdown
## 阻塞问题

**模块**: 后端/前端/AI/测试
**问题描述**: ...
**影响范围**: ...
**已尝试方案**: 
1. ...
2. ...
**需要决策**: ...
```

---

*本规范由所有开发代理共同遵守，变更需讨论后更新*
