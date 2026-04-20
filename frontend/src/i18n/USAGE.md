# LiveMirror 国际化 (i18n) 使用指南

## 概述

LiveMirror 支持 4 种语言：
- 🇨🇳 中文 (zh)
- 🇺🇸 English (en)
- 🇯🇵 日本語 (ja)
- 🇰🇷 한국어 (ko)

## 快速开始

### 1. 在组件中使用翻译

```vue
<template>
  <div>
    <h1>{{ t('common.welcome') }}</h1>
    <p>{{ t('messages.no_data') }}</p>
    <button>{{ t('common.save') }}</button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>
```

### 2. 带参数的翻译

```vue
<template>
  <div>
    <p>{{ t('time.minute_ago', { n: 5 }) }}</p>
    <!-- 输出：5 分钟前 / 5 minutes ago -->
    
    <p>{{ t('templates.product_features', { features: featureList }) }}</p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const featureList = '高质量、低价格';
</script>
```

### 3. 语言切换

```vue
<template>
  <div>
    <!-- 使用语言切换组件 -->
    <LanguageSwitcher />
    
    <!-- 或自定义切换 -->
    <select @change="changeLanguage($event)">
      <option v-for="lang in languages" :key="lang.code" :value="lang.code">
        {{ lang.flag }} {{ lang.name }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { setLocale, getLocaleOptions } from '@/i18n';
import LanguageSwitcher from '@/components/LanguageSwitcher.vue';

const languages = getLocaleOptions();

async function changeLanguage(event: Event) {
  const target = event.target as HTMLSelectElement;
  await setLocale(target.value);
}
</script>
```

### 4. 在 JavaScript/TypeScript 中使用

```typescript
import { i18n } from '@/i18n';

// 获取翻译
const welcome = i18n.global.t('common.welcome');

// 切换语言
await i18n.global.locale.value = 'en';

// 或使用辅助函数
import { setLocale, t } from '@/i18n';

await setLocale('ja');
const message = t('messages.save_success');
```

### 5. 自动语言检测

```typescript
import { detectLocale, detectTextLanguage } from '@/i18n';

// 检测用户界面语言
const userLocale = detectLocale();
// 优先级：localStorage > 浏览器设置 > 默认语言

// 检测文本语言
const lang = detectTextLanguage('これはテストです');
// 返回：'ja'
```

## 语言包结构

### 前端语言包

位置：`frontend/src/locales/{lang}.json`

```json
{
  "common": {
    "welcome": "欢迎",
    "loading": "加载中..."
  },
  "features": {
    "ab_testing": "A/B 测试"
  },
  "messages": {
    "save_success": "保存成功"
  },
  "templates": {
    "greeting": "您好！欢迎来到我们的直播间"
  }
}
```

### 后端语言包

位置：`backend/locales/{lang}.json`

结构与前端类似，通过 Python 的 `I18nService` 加载。

## 添加新语言

### 1. 创建语言包

```bash
# 前端
cp frontend/src/locales/zh.json frontend/src/locales/fr.json

# 后端
cp backend/locales/zh.json backend/locales/fr.json
```

### 2. 更新配置

**前端** - `frontend/src/i18n/index.ts`:
```typescript
export const supportedLocales: Locale[] = ['zh', 'en', 'ja', 'ko', 'fr'];

export const localeNames: Record<Locale, string> = {
  // ...
  fr: 'Français'
};

export const localeFlags: Record<Locale, string> = {
  // ...
  fr: '🇫🇷'
};
```

**后端** - `backend/services/i18n.py`:
```python
class SupportedLanguage(Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"
    KO = "ko"
    FR = "fr"  # 添加新语言
```

### 3. 翻译所有键

确保新语言包包含所有必需的翻译键。

## 最佳实践

### ✅ 推荐

1. **使用嵌套键名**
   ```typescript
   // 好
   t('common.buttons.save')
   
   // 不好
   t('save_button_text')
   ```

2. **使用参数化翻译**
   ```typescript
   // 好
   t('time.ago', { n: 5, unit: '分钟' })
   
   // 不好
   `${5} 分钟前`
   ```

3. **保持语言包同步**
   - 添加新翻译时，确保所有语言都有对应键
   - 使用 `test_all_languages_have_same_keys` 测试验证

4. **使用语义化键名**
   ```typescript
   // 好
   t('errors.network.unavailable')
   
   // 不好
   t('error_123')
   ```

### ❌ 避免

1. **硬编码文本**
   ```vue
   <!-- 不好 -->
   <button>保存</button>
   
   <!-- 好 -->
   <button>{{ t('common.save') }}</button>
   ```

2. **字符串拼接**
   ```typescript
   // 不好
   const msg = '保存' + (success ? '成功' : '失败')
   
   // 好
   const msg = t(success ? 'messages.save_success' : 'messages.save_failed')
   ```

3. **混合语言**
   - 不要在同一界面混合多种语言
   - 语言切换后应刷新整个界面

## 测试

### 运行测试

```bash
# 后端测试
cd backend
python -m pytest tests/test_i18n.py -v

# 前端测试
cd frontend
npm run test
```

### 测试语言切换

1. 打开应用
2. 点击右上角语言切换器
3. 选择不同语言
4. 验证所有文本已正确翻译
5. 刷新页面，验证语言设置已保存

## API 参考

### 前端函数

| 函数 | 描述 | 返回值 |
|------|------|--------|
| `detectLocale()` | 检测用户语言 | `Locale` |
| `setLocale(locale)` | 设置语言 | `Promise<void>` |
| `saveLocale(locale)` | 保存语言设置 | `void` |
| `getLocaleOptions()` | 获取语言选项 | `Array<{code, name, flag}>` |
| `detectTextLanguage(text)` | 检测文本语言 | `Locale` |

### 后端类

| 类/函数 | 描述 |
|---------|------|
| `I18nService` | 国际化服务主类 |
| `LanguageDetector` | 语言检测器 |
| `get_i18n()` | 获取全局实例 |
| `t(key, lang, **kwargs)` | 翻译函数 |
| `detect_language(text)` | 语言检测 |

## 故障排除

### 问题：翻译显示为键名

**原因**: 语言包未加载或键不存在

**解决**:
1. 检查语言包文件是否存在
2. 验证键名拼写正确
3. 查看浏览器控制台错误

### 问题：语言切换不生效

**原因**: localStorage 缓存或组件未更新

**解决**:
1. 清除 localStorage: `localStorage.removeItem('livemirror_locale')`
2. 确保使用 `setLocale` 而非直接修改
3. 检查组件是否正确响应 locale 变化

### 问题：某些文本未翻译

**原因**: 文本硬编码或未使用 t() 函数

**解决**:
1. 搜索代码中的硬编码文本
2. 替换为 t() 调用
3. 添加缺失的翻译键

## 更多信息

- Vue I18n 文档：https://vue-i18n.intlify.dev/
- 语言代码标准：ISO 639-1
- 旗帜 emoji: 因平台而异，建议测试目标平台
