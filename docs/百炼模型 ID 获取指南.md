# 阿里云百炼模型 ID 获取指南

> 📌 **最后更新**: 2026-04-08

---

## 🎯 目标
获取通义千问模型 ID，用于 LiveMirror 的 AI 话术分析。

---

## 📝 详细步骤

### 步骤 1: 访问百炼控制台

```
网址：https://bailian.console.aliyun.com
```

**注意**：需要登录你的阿里云账号

---

### 步骤 2: 进入模型广场

1. 登录后，点击左侧菜单 **「模型广场」**
2. 或者顶部导航栏找到 **「模型中心」** → **「模型广场」**

---

### 步骤 3: 选择通义千问模型

在模型列表中找到 **通义千问** 系列：

| 模型名称 | 模型 ID | 特点 | 适用场景 |
|----------|---------|------|----------|
| qwen-turbo | `qwen-turbo` | 速度最快，便宜 | 简单任务 |
| qwen-plus | `qwen-plus` | 平衡 | **推荐用于话术分析** |
| qwen-max | `qwen-max` | 最强，较贵 | 复杂分析 |
| qwen-max-longcontext | `qwen-max-longcontext` | 支持长文本 | 超长直播（>4 小时） |

**推荐**：使用 `qwen-plus`（性价比高，中文理解好）

---

### 步骤 4: 查看模型详情（可选）

1. 点击模型卡片
2. 查看模型介绍、价格、使用限制
3. 点击 **「开通服务」**（如未开通）

---

### 步骤 5: 获取模型 ID

**模型 ID 就是上面表格中的标识**，例如：
- `qwen-plus`
- `qwen-max`

**不需要额外的 Key**，使用阿里云 AccessKey 即可调用。

---

## 🔧 配置文件

将模型 ID 填入 `.env` 文件：

```bash
# 编辑文件
D:\project\LiveMirror\backend\.env

# 修改这一行
DASHSCOPE_MODEL=qwen-plus
```

**可选模型值**：
- `qwen-turbo`（最快）
- `qwen-plus`（推荐）
- `qwen-max`（最强）
- `qwen-max-longcontext`（超长文本）

---

## 💰 免费额度说明

**通义千问免费额度**（以官网为准）：

| 模型 | 免费额度 | 有效期 |
|------|----------|--------|
| qwen-turbo | 100 万 tokens | 首月 |
| qwen-plus | 50 万 tokens | 首月 |
| qwen-max | 10 万 tokens | 首月 |

**查看你的额度**：
```
https://bailian.console.aliyun.com → 费用中心 → 资源包
```

---

## 🧪 测试调用

配置完成后，运行测试：

```bash
cd D:\project\LiveMirror\backend
python -c "from services import analyzer; print(analyzer.test_connection())"
```

**预期输出**：
```
✅ 阿里云百炼连接成功
模型：qwen-plus
剩余额度：XXXXX tokens
```

---

## ⚠️ 常见问题

### Q1: 找不到「模型广场」？
**A**: 可能需要先开通百炼服务，点击首页的「开通服务」按钮。

### Q2: 提示「未授权」？
**A**: 检查 AccessKey 是否正确，确保 RAM 用户有百炼权限。

### Q3: 费用超了怎么办？
**A**: 在百炼控制台设置费用告警，或切换到免费额度更多的模型。

---

## 🔗 相关链接

- 百炼控制台：https://bailian.console.aliyun.com
- 模型文档：https://help.aliyun.com/zh/dashscope/
- API 参考：https://help.aliyun.com/zh/dashscope/developer-reference/

---

*配置完成后，重启后端服务生效*
