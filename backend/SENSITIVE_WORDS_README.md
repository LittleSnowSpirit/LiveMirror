# LiveMirror 敏感词检测系统

## 功能概述

敏感词检测系统提供完整的敏感词管理、实时检测、分级预警和智能替换功能。

### 核心功能

1. **敏感词库管理**
   - 添加/删除/更新敏感词
   - 批量导入导出
   - 分类管理（通用、美妆、食品、服装等）
   - 分页查询和搜索

2. **实时检测**
   - 文本敏感词检测
   - 语音转写同步检测
   - 流式检测支持
   - 上下文提取

3. **分级预警**
   - 警告级别 (warning) - 建议优化
   - 严重级别 (serious) - 需要修改
   - 封禁级别 (banned) - 禁止发布

4. **智能替换**
   - 自动提供替换建议
   - 一键应用替换
   - 保留原文语义

5. **使用统计**
   - 检测次数统计
   - 命中率分析
   - 分类分布
   - 每日趋势

6. **行业词包**
   - 美妆行业词包
   - 食品行业词包
   - 服装行业词包
   - 自定义词包安装

## 文件结构

```
workspace/
├── backend/
│   ├── services/
│   │   └── sensitive_words.py      # 核心服务
│   ├── routes/
│   │   └── sensitive.py            # API 路由
│   └── tests/
│       └── test_sensitive_words.py # 测试脚本
├── frontend/
│   └── src/
│       ├── views/
│       │   └── SensitiveWords.vue      # 管理页面
│       └── components/
│           └── SensitiveWordAlert.vue  # 预警组件
└── data/
    └── sensitive_words/
        ├── word_library.json       # 词库数据
        ├── usage_stats.json        # 使用统计
        └── industry_packages.json  # 行业词包
```

## API 接口

### 词库管理

```bash
# 添加敏感词
POST /api/sensitive/words
{
  "word": "敏感词",
  "severity": "warning",
  "category": "general",
  "replacement": "替换词",
  "reason": "添加原因"
}

# 删除敏感词
DELETE /api/sensitive/words/{word}

# 更新敏感词
PUT /api/sensitive/words/{word}
{
  "severity": "serious",
  "replacement": "新替换词"
}

# 查询词列表
GET /api/sensitive/words?category=general&severity=warning&page=1&page_size=50

# 批量添加
POST /api/sensitive/words/batch
{
  "words": ["词 1", "词 2"],
  "severity": "warning",
  "category": "general"
}
```

### 检测接口

```bash
# 检测文本
POST /api/sensitive/detect
{
  "text": "待检测文本",
  "realtime": false
}

# 流式检测（语音转写）
POST /api/sensitive/detect/stream
{
  "text": "实时转写文本"
}
```

### 统计接口

```bash
# 获取统计
GET /api/sensitive/statistics

# 分类统计
GET /api/sensitive/statistics/categories

# 每日统计
GET /api/sensitive/statistics/daily?days=7
```

### 行业词包

```bash
# 获取已安装包
GET /api/sensitive/industry-packages

# 安装预定义词包
POST /api/sensitive/industry-packages/predefined/beauty
POST /api/sensitive/industry-packages/predefined/food
POST /api/sensitive/industry-packages/predefined/clothing

# 卸载词包
DELETE /api/sensitive/industry-packages/{category}
```

## 使用示例

### Python 调用

```python
from backend.services.sensitive_words import get_service, detect_sensitive_words

# 获取服务实例
service = get_service()

# 检测文本
hits = detect_sensitive_words("这是测试文本")
print(f"发现 {len(hits)} 个敏感词")

# 实时检测
result = service.detect_realtime("包含敏感词的文本")
if result["has_sensitive"]:
    print(f"检测到敏感词，建议：{result['suggested_text']}")
    if result["should_block"]:
        print("包含禁止内容，需要拦截")
```

### 前端组件使用

```vue
<template>
  <div>
    <!-- 管理页面 -->
    <SensitiveWords />
    
    <!-- 预警组件 -->
    <SensitiveWordAlert
      v-model="alertVisible"
      :hits="sensitiveHits"
      :context="currentText"
      :suggested-text="suggestedText"
      mode="modal"
      @modify="handleModify"
      @apply-suggestion="applySuggestion"
    />
  </div>
</template>

<script setup>
import SensitiveWords from '@/views/SensitiveWords.vue'
import SensitiveWordAlert from '@/components/SensitiveWordAlert.vue'
</script>
```

## 测试

运行测试脚本验证所有功能：

```bash
python backend/tests/test_sensitive_words.py
```

测试覆盖：
- ✅ 词库管理（添加/删除/更新/查询）
- ✅ 实时检测功能
- ✅ 分级预警（警告/严重/封禁）
- ✅ 替换建议
- ✅ 使用统计
- ✅ 行业词包

## 词库配置

### 敏感词级别

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| warning | 警告级别 | 建议优化，可继续 |
| serious | 严重级别 | 需要修改，建议拦截 |
| banned | 封禁级别 | 禁止发布，必须拦截 |

### 行业分类

| 分类 | 说明 | 适用场景 |
|------|------|----------|
| general | 通用敏感词 | 所有场景 |
| beauty | 美妆行业 | 化妆品、护肤品 |
| food | 食品行业 | 食品、保健品 |
| clothing | 服装行业 | 服饰、鞋帽 |
| finance | 金融 | 理财、投资 |
| health | 医疗健康 | 药品、医疗器械 |
| advertising | 广告违禁 | 所有商业宣传 |

## 最佳实践

1. **词库维护**
   - 定期更新词库
   - 根据业务场景添加行业词
   - 记录添加原因便于追溯

2. **检测策略**
   - 发布前必检
   - 语音转写实时检
   - 定时批量复检

3. **分级处理**
   - 警告级别：提示用户优化
   - 严重级别：要求修改
   - 封禁级别：直接拦截

4. **性能优化**
   - 大文本分段检测
   - 缓存检测结果
   - 异步处理批量检测

## 注意事项

1. 敏感词检测使用精确匹配，注意词边界
2. 替换建议需要根据语境调整
3. 行业词包按需安装，避免误判
4. 定期备份词库数据
5. 遵守相关法律法规

## 扩展开发

### 添加新行业词包

```python
from backend.services.sensitive_words import get_service

service = get_service()

# 定义词包
electronics_package = [
    {"word": "最先进", "severity": "warning", "replacement": "领先技术", "reason": "广告法禁用"},
    {"word": "国家级专利", "severity": "serious", "replacement": "多项专利", "reason": "需验证"}
]

# 安装词包
service.install_industry_package("electronics", electronics_package)
```

### 自定义检测回调

```python
def on_sensitive_detected(result):
    """敏感词检测回调"""
    if result["should_block"]:
        # 发送告警
        send_alert(result)
    # 记录日志
    log_detection(result)

# 使用回调
service.detect_realtime(text, callback=on_sensitive_detected)
```

## 版本历史

- v1.0.0 (2026-04-08)
  - 初始版本
  - 基础词库管理
  - 实时检测
  - 分级预警
  - 智能替换
  - 使用统计
  - 行业词包
