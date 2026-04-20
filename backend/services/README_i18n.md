# LiveMirror 后端国际化 (i18n) 使用指南

## 概述

后端 i18n 服务提供多语言支持，包括：
- 文本翻译
- 自动语言检测
- 话术模板
- 语言切换

## 快速开始

### 1. 基本使用

```python
from services.i18n import get_i18n, t, detect_language

# 获取 i18n 实例
i18n = get_i18n()

# 翻译文本
welcome = t('common.welcome')  # 欢迎使用 LiveMirror

# 指定语言翻译
welcome_en = t('common.welcome', lang='en')  # Welcome to LiveMirror

# 带参数的翻译
msg = t('time.minute_ago', n=5)  # 5 分钟前

# 检测语言
lang = detect_language('这是中文')  # 'zh'
```

### 2. 在 Flask 路由中使用

```python
from flask import Flask, request, jsonify
from services.i18n import get_i18n, FlaskI18nMiddleware

app = Flask(__name__)

# 注册中间件（可选）
if FlaskI18nMiddleware:
    i18n_middleware = FlaskI18nMiddleware()
    app.before_request(i18n_middleware.before_request)
    app.after_request(i18n_middleware.after_request)

@app.route('/api/welcome')
def welcome():
    i18n = get_i18n()
    
    # 自动使用请求中的语言
    return jsonify({
        'message': i18n.t('common.welcome'),
        'language': i18n.get_language()
    })

@app.route('/api/data')
def get_data():
    i18n = get_i18n()
    
    # 处理数据
    data = {
        'status': 'success',
        'message': i18n.t('messages.save_success')
    }
    
    return jsonify(data)
```

### 3. 话术模板使用

```python
from services.i18n import get_i18n

i18n = get_i18n()

# 获取单个模板
greeting = i18n.get_template('greeting')
# 输出：您好！欢迎来到我们的直播间

# 获取所有模板
templates = i18n.get_all_templates()
# 返回：{'greeting': '...', 'product_intro': '...', ...}

# 指定语言获取
greeting_en = i18n.get_template('greeting', lang='en')
# 输出：Hello! Welcome to our live stream
```

### 4. 语言检测

```python
from services.i18n import LanguageDetector, detect_language

# 检测单个文本
lang = detect_language('这是中文')  # 'zh'
lang = detect_language('English text')  # 'en'
lang = detect_language('日本語テキスト')  # 'ja'
lang = detect_language('한국어 텍스트')  # 'ko'

# 批量检测
texts = ['中文', 'English', '日本語', '한국어']
results = LanguageDetector.detect_batch(texts)
# 返回：{'中文': SupportedLanguage.ZH, 'English': SupportedLanguage.EN, ...}
```

### 5. 动态添加翻译

```python
from services.i18n import get_i18n

i18n = get_i18n()

# 添加新翻译
i18n.add_translation('zh', 'custom.greeting', '自定义问候')
i18n.add_translation('en', 'custom.greeting', 'Custom Greeting')

# 使用新翻译
msg = i18n.t('custom.greeting')  # 自定义问候
```

### 6. 获取支持的语言

```python
from services.i18n import get_i18n

i18n = get_i18n()

languages = i18n.get_supported_languages()
# 返回：[
#   {'code': 'zh', 'name': '中文'},
#   {'code': 'en', 'name': 'English'},
#   {'code': 'ja', 'name': '日本語'},
#   {'code': 'ko', 'name': '한국어'}
# ]
```

## 在现有服务中集成 i18n

### 示例：敏感词检测服务

```python
# services/sensitive_words.py
from services.i18n import get_i18n

class SensitiveWordService:
    def __init__(self):
        self.i18n = get_i18n()
    
    def check_text(self, text: str, lang: str = None) -> dict:
        """检测敏感词"""
        # 自动检测语言
        if not lang:
            lang = self.i18n.detect_language(text)
        
        # 设置语言
        self.i18n.set_language(lang)
        
        # 检测结果
        result = {
            'has_sensitive': False,
            'words': [],
            'message': self.i18n.t('messages.scan_complete')
        }
        
        # ... 检测逻辑 ...
        
        return result
    
    def get_category_name(self, category: str) -> str:
        """获取分类名称（多语言）"""
        return self.i18n.t(f'categories.{category}')
```

### 示例：报告生成服务

```python
# services/report_generator.py
from services.i18n import get_i18n

class ReportGenerator:
    def __init__(self):
        self.i18n = get_i18n()
    
    def generate(self, data: dict, lang: str = 'zh') -> str:
        """生成报告"""
        self.i18n.set_language(lang)
        
        report = f"""
        # {self.i18n.t('report.title')}
        
        ## {self.i18n.t('report.summary')}
        {data['summary']}
        
        ## {self.i18n.t('report.details')}
        {data['details']}
        
        ---
        {self.i18n.t('report.footer')}
        """
        
        return report
```

### 示例：API 响应标准化

```python
# utils/response.py
from services.i18n import get_i18n

def success_response(data=None, message='messages.success'):
    """成功响应"""
    i18n = get_i18n()
    return {
        'code': 200,
        'message': i18n.t(message),
        'data': data
    }

def error_response(message='messages.operation_failed', code=400):
    """错误响应"""
    i18n = get_i18n()
    return {
        'code': code,
        'message': i18n.t(message),
        'data': None
    }

# 使用
@app.route('/api/save')
def save():
    # ... 保存逻辑 ...
    return success_response(data={'id': 123})
```

## 语言包管理

### 目录结构

```
backend/
├── locales/
│   ├── zh.json    # 中文
│   ├── en.json    # 英文
│   ├── ja.json    # 日文
│   └── ko.json    # 韩文
└── services/
    └── i18n.py    # i18n 服务
```

### 语言包格式

```json
{
  "common": {
    "welcome": "欢迎",
    "loading": "加载中..."
  },
  "features": {
    "feature_name": "功能名称"
  },
  "messages": {
    "success": "成功",
    "error": "错误"
  },
  "templates": {
    "greeting": "问候语模板"
  }
}
```

### 添加新翻译

1. 在所有语言包中添加相同键
2. 保持键的命名一致性
3. 使用嵌套结构组织翻译

```json
{
  "module": {
    "action": {
      "success": "操作成功",
      "failure": "操作失败"
    }
  }
}
```

## 最佳实践

### ✅ 推荐

1. **使用全局实例**
   ```python
   # 好
   from services.i18n import get_i18n
   i18n = get_i18n()
   
   # 不推荐
   i18n = I18nService()  # 每次创建新实例
   ```

2. **在请求开始时设置语言**
   ```python
   @app.before_request
   def set_language():
       lang = request.args.get('lang', 'zh')
       get_i18n().set_language(lang)
   ```

3. **使用语义化键名**
   ```python
   # 好
   t('errors.validation.email_invalid')
   
   # 不好
   t('error_123')
   ```

4. **提供回退机制**
   ```python
   # i18n 会自动回退到英文
   t('custom.key')  # 如果中文不存在，使用英文
   ```

### ❌ 避免

1. **硬编码文本**
   ```python
   # 不好
   return {'message': '操作成功'}
   
   # 好
   return {'message': t('messages.success')}
   ```

2. **在循环中创建 i18n 实例**
   ```python
   # 不好
   for item in items:
       i18n = I18nService()
       translate(item)
   
   # 好
   i18n = get_i18n()
   for item in items:
       translate(item)
   ```

## 测试

运行 i18n 测试：

```bash
cd backend
python -m pytest tests/test_i18n.py -v
```

测试覆盖：
- 语言检测
- 翻译功能
- 话术模板
- 语言切换
- 参数化翻译
- 回退机制

## 故障排除

### 问题：翻译返回键名

**原因**: 语言包未加载或键不存在

**解决**:
```python
# 检查语言包是否加载
i18n = get_i18n()
print(i18n.translations.keys())  # 应包含 'zh', 'en', 'ja', 'ko'

# 重新加载语言包
i18n.reload_locale('zh')
```

### 问题：语言切换不生效

**原因**: 多个 i18n 实例

**解决**:
```python
# 始终使用全局实例
from services.i18n import get_i18n

i18n = get_i18n()  # 正确
# i18n = I18nService()  # 错误
```

## API 参考

### I18nService 类

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `set_language(lang)` | 设置当前语言 | `lang: str` | `None` |
| `get_language()` | 获取当前语言 | - | `str` |
| `t(key, lang, **kwargs)` | 翻译文本 | `key: str`, `lang: str`, `**kwargs` | `str` |
| `get_template(name, lang)` | 获取模板 | `name: str`, `lang: str` | `str` |
| `get_all_templates(lang)` | 获取所有模板 | `lang: str` | `Dict` |
| `detect_language(text)` | 检测语言 | `text: str` | `str` |
| `get_supported_languages()` | 获取支持的语言 | - | `List[Dict]` |
| `add_translation(lang, key, value)` | 添加翻译 | `lang, key, value` | `None` |

### LanguageDetector 类

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `detect(text)` | 检测文本语言 | `text: str` | `SupportedLanguage` |
| `detect_batch(texts)` | 批量检测 | `texts: List[str]` | `Dict[str, SupportedLanguage]` |

### 全局函数

| 函数 | 描述 | 等价于 |
|------|------|--------|
| `get_i18n()` | 获取全局实例 | `I18nService()` 单例 |
| `t(key, lang, **kwargs)` | 快捷翻译 | `get_i18n().t(...)` |
| `detect_language(text)` | 快捷语言检测 | `LanguageDetector.detect(...)` |

## 更多信息

- 前端 i18n 使用：`frontend/src/i18n/USAGE.md`
- 测试用例：`backend/tests/test_i18n.py`
- 语言包：`backend/locales/*.json`
