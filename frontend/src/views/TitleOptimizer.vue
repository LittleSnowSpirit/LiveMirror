<template>
  <div class="title-optimizer">
    <div class="page-header">
      <h1 class="page-title">🎯 直播间标题优化</h1>
      <p class="page-subtitle">AI 生成吸引人文案，智能评分预测点击率</p>
    </div>

    <!-- 标题生成器 -->
    <div class="section card">
      <h2 class="section-title">✨ AI 标题生成</h2>
      
      <div class="form-group">
        <label class="form-label">产品/主题</label>
        <input
          v-model="form.product"
          type="text"
          class="form-input"
          placeholder="例如：美白精华、显瘦连衣裙、网红零食..."
          @keyup.enter="generateTitles"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">行业分类</label>
          <select v-model="form.category" class="form-select">
            <option value="general">通用</option>
            <option value="beauty">美妆</option>
            <option value="fashion">服装</option>
            <option value="food">食品</option>
            <option value="electronics">数码</option>
            <option value="home">家居</option>
            <option value="entertainment">娱乐</option>
            <option value="education">教育</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">生成数量</label>
          <select v-model="form.count" class="form-select">
            <option value="3">3 个</option>
            <option value="5">5 个</option>
            <option value="8">8 个</option>
            <option value="10">10 个</option>
          </select>
        </div>
      </div>

      <button 
        class="btn btn-primary btn-lg" 
        @click="generateTitles"
        :disabled="loading.generating"
      >
        {{ loading.generating ? '生成中...' : '🚀 生成标题' }}
      </button>

      <!-- 生成的标题列表 -->
      <div class="generated-titles" v-if="generatedTitles.length > 0">
        <h3 class="list-title">生成结果</h3>
        <div 
          class="title-card" 
          v-for="(item, index) in generatedTitles" 
          :key="index"
          :class="{ selected: selectedTitle === item.title }"
          @click="selectTitle(item)"
        >
          <div class="title-card-header">
            <span class="title-card-text">{{ item.title }}</span>
            <span class="title-card-score" :class="getScoreClass(item.score.total)">
              {{ item.score.total }}
            </span>
          </div>
          <div class="title-card-footer">
            <span class="title-card-template">{{ item.template }}</span>
            <span class="title-card-ctr">预测 CTR: {{ item.score.predicted_ctr.toFixed(2) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 标题评分 -->
    <div class="section card">
      <h2 class="section-title">📊 标题评分</h2>
      
      <div class="form-group">
        <label class="form-label">输入标题进行评分</label>
        <textarea
          v-model="scoreForm.title"
          class="form-textarea"
          rows="2"
          placeholder="输入要评分的标题..."
        ></textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">行业分类</label>
          <select v-model="scoreForm.category" class="form-select">
            <option value="general">通用</option>
            <option value="beauty">美妆</option>
            <option value="fashion">服装</option>
            <option value="food">食品</option>
            <option value="electronics">数码</option>
            <option value="home">家居</option>
          </select>
        </div>
      </div>

      <button 
        class="btn btn-secondary" 
        @click="scoreTitle"
        :disabled="loading.scoring"
      >
        {{ loading.scoring ? '评分中...' : '📈 开始评分' }}
      </button>

      <!-- 评分结果 -->
      <div class="score-result" v-if="currentScore">
        <TitleScore 
          :score="currentScore.score" 
          :suggestions="currentScore.suggestions"
        />
      </div>
    </div>

    <!-- A/B 测试 -->
    <div class="section card">
      <h2 class="section-title">🧪 A/B 测试</h2>
      
      <div class="ab-test-form">
        <div class="form-group">
          <label class="form-label">标题 A</label>
          <input
            v-model="abTestForm.title_a"
            type="text"
            class="form-input"
            placeholder="输入标题 A..."
          />
        </div>

        <div class="form-group">
          <label class="form-label">标题 B</label>
          <input
            v-model="abTestForm.title_b"
            type="text"
            class="form-input"
            placeholder="输入标题 B..."
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">行业分类</label>
            <select v-model="abTestForm.category" class="form-select">
              <option value="general">通用</option>
              <option value="beauty">美妆</option>
              <option value="fashion">服装</option>
              <option value="food">食品</option>
              <option value="electronics">数码</option>
              <option value="home">家居</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">测试时长</label>
            <select v-model="abTestForm.duration_hours" class="form-select">
              <option value="12">12 小时</option>
              <option value="24">24 小时</option>
              <option value="48">48 小时</option>
              <option value="72">72 小时</option>
            </select>
          </div>
        </div>

        <button 
          class="btn btn-primary" 
          @click="createABTest"
          :disabled="loading.abTest"
        >
          {{ loading.abTest ? '创建中...' : '🎲 创建 A/B 测试' }}
        </button>
      </div>

      <!-- A/B 测试结果 -->
      <div class="ab-test-result" v-if="currentABTest">
        <div class="ab-test-info">
          <h3 class="ab-test-title">测试 ID: {{ currentABTest.test_id }}</h3>
          <div class="ab-test-prediction">
            <span>预测获胜：</span>
            <span class="winner-badge" :class="currentABTest.predicted_winner.toLowerCase()">
              {{ currentABTest.predicted_winner }}
            </span>
          </div>
        </div>

        <div class="ab-comparison">
          <div class="ab-variant">
            <div class="variant-label">标题 A</div>
            <div class="variant-content">{{ currentABTest.title_a }}</div>
            <div class="variant-score">评分：{{ currentABTest.score_a }}</div>
          </div>

          <div class="ab-variant">
            <div class="variant-label">标题 B</div>
            <div class="variant-content">{{ currentABTest.title_b }}</div>
            <div class="variant-score">评分：{{ currentABTest.score_b }}</div>
          </div>
        </div>
      </div>

      <!-- A/B 测试列表 -->
      <div class="ab-tests-list" v-if="abTests.length > 0">
        <h3 class="list-title">历史测试</h3>
        <div 
          class="ab-test-item" 
          v-for="test in abTests" 
          :key="test.id"
          @click="viewABTest(test.id)"
        >
          <div class="ab-test-item-header">
            <span class="ab-test-id">{{ test.id }}</span>
            <span class="ab-test-status" :class="test.status">
              {{ test.status === 'active' ? '进行中' : '已完成' }}
            </span>
          </div>
          <div class="ab-test-item-content">
            <span class="ab-test-title-a">A: {{ test.title_a }}</span>
            <span class="ab-test-title-b">B: {{ test.title_b }}</span>
          </div>
          <div class="ab-test-item-footer" v-if="test.winner">
            <span class="ab-test-winner">🏆 获胜：{{ test.winner.toUpperCase() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史记录 -->
    <div class="section card">
      <h2 class="section-title">📜 历史标题分析</h2>
      
      <div class="history-controls">
        <select v-model="historyDays" class="form-select" @change="loadHistory">
          <option value="7">最近 7 天</option>
          <option value="30">最近 30 天</option>
          <option value="90">最近 90 天</option>
        </select>

        <button class="btn btn-secondary" @click="loadHistory">
          🔄 刷新
        </button>
      </div>

      <!-- 分析统计 -->
      <div class="history-stats" v-if="historyAnalysis">
        <div class="stat-card">
          <div class="stat-value">{{ historyAnalysis.total_titles }}</div>
          <div class="stat-label">标题总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ historyAnalysis.avg_score?.toFixed(1) || 0 }}</div>
          <div class="stat-label">平均评分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ historyAnalysis.avg_ctr?.toFixed(2) || 0 }}%</div>
          <div class="stat-label">平均 CTR</div>
        </div>
      </div>

      <!-- 历史标题列表 -->
      <div class="history-list" v-if="history.length > 0">
        <div 
          class="history-item" 
          v-for="(item, index) in history" 
          :key="index"
        >
          <div class="history-item-title">{{ item.title }}</div>
          <div class="history-item-meta">
            <span class="history-item-category">{{ item.category }}</span>
            <span class="history-item-date">{{ formatDate(item.created_at) }}</span>
            <span class="history-item-score" v-if="item.metrics?.score">
              评分：{{ item.metrics.score }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 行业最佳实践 -->
    <div class="section card">
      <h2 class="section-title">📚 行业最佳实践</h2>
      
      <div class="practice-tabs">
        <button
          class="practice-tab"
          :class="{ active: practiceCategory === cat }"
          v-for="cat in practiceCategories"
          :key="cat.value"
          @click="loadBestPractices(cat.value)"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="practice-content" v-if="bestPractices">
        <div class="practice-section">
          <h4 class="practice-subtitle">建议标题长度</h4>
          <p class="practice-text">{{ bestPractices.title_length }}</p>
        </div>

        <div class="practice-section">
          <h4 class="practice-subtitle">关键要素</h4>
          <div class="practice-tags">
            <span 
              class="practice-tag" 
              v-for="(element, index) in bestPractices.key_elements" 
              :key="index"
            >
              {{ element }}
            </span>
          </div>
        </div>

        <div class="practice-section">
          <h4 class="practice-subtitle">优化技巧</h4>
          <ul class="practice-list">
            <li v-for="(tip, index) in bestPractices.tips" :key="index">
              {{ tip }}
            </li>
          </ul>
        </div>

        <div class="practice-section">
          <h4 class="practice-subtitle">优秀案例</h4>
          <div class="practice-examples">
            <div 
              class="practice-example" 
              v-for="(example, index) in bestPractices.examples" 
              :key="index"
            >
              {{ example }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import TitleScore from '../components/TitleScore.vue'

// API 基础 URL
const API_BASE = '/api'

// 表单数据
const form = reactive({
  product: '',
  category: 'general',
  count: 5
})

const scoreForm = reactive({
  title: '',
  category: 'general'
})

const abTestForm = reactive({
  title_a: '',
  title_b: '',
  category: 'general',
  duration_hours: 24
})

// 加载状态
const loading = reactive({
  generating: false,
  scoring: false,
  abTest: false
})

// 生成的标题
const generatedTitles = ref<any[]>([])
const selectedTitle = ref<string>('')

// 评分结果
const currentScore = ref<any>(null)

// A/B 测试
const currentABTest = ref<any>(null)
const abTests = ref<any[]>([])

// 历史记录
const history = ref<any[]>([])
const historyAnalysis = ref<any>(null)
const historyDays = ref('30')

// 最佳实践
const bestPractices = ref<any>(null)
const practiceCategory = ref('general')
const practiceCategories = [
  { value: 'general', label: '通用' },
  { value: 'beauty', label: '美妆' },
  { value: 'fashion', label: '服装' },
  { value: 'food', label: '食品' },
  { value: 'electronics', label: '数码' },
  { value: 'home', label: '家居' }
]

// 生成标题
async function generateTitles() {
  if (!form.product.trim()) {
    alert('请输入产品/主题')
    return
  }

  loading.generating = true
  try {
    const response = await fetch(`${API_BASE}/title/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })

    const result = await response.json()
    
    if (result.success) {
      generatedTitles.value = result.data.titles
      if (generatedTitles.value.length > 0) {
        selectTitle(generatedTitles.value[0])
      }
    } else {
      alert('生成失败：' + (result.detail || '未知错误'))
    }
  } catch (error) {
    console.error('生成标题失败:', error)
    alert('生成失败，请检查网络连接')
  } finally {
    loading.generating = false
  }
}

// 选择标题
function selectTitle(item: any) {
  selectedTitle.value = item.title
  scoreForm.title = item.title
  scoreForm.category = item.category
  scoreTitle()
}

// 评分标题
async function scoreTitle() {
  if (!scoreForm.title.trim()) {
    return
  }

  loading.scoring = true
  try {
    // 获取评分
    const scoreResponse = await fetch(`${API_BASE}/title/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scoreForm)
    })

    const scoreResult = await scoreResponse.json()
    
    // 获取关键词建议
    const suggestionResponse = await fetch(`${API_BASE}/title/keywords/suggest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scoreForm)
    })

    const suggestionResult = await suggestionResponse.json()
    
    if (scoreResult.success) {
      currentScore.value = {
        score: scoreResult.data.score,
        suggestions: suggestionResult.success ? suggestionResult.data.suggestions : null
      }
    }
  } catch (error) {
    console.error('评分失败:', error)
  } finally {
    loading.scoring = false
  }
}

// 创建 A/B 测试
async function createABTest() {
  if (!abTestForm.title_a.trim() || !abTestForm.title_b.trim()) {
    alert('请输入标题 A 和标题 B')
    return
  }

  loading.abTest = true
  try {
    const response = await fetch(`${API_BASE}/title/ab-test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(abTestForm)
    })

    const result = await response.json()
    
    if (result.success) {
      currentABTest.value = result.data
      loadABTests()
    } else {
      alert('创建失败：' + (result.detail || '未知错误'))
    }
  } catch (error) {
    console.error('创建 A/B 测试失败:', error)
    alert('创建失败，请检查网络连接')
  } finally {
    loading.abTest = false
  }
}

// 加载 A/B 测试列表
async function loadABTests() {
  try {
    const response = await fetch(`${API_BASE}/title/ab-tests`)
    const result = await response.json()
    
    if (result.success) {
      abTests.value = result.data.tests.slice(0, 5) // 只显示最近 5 个
    }
  } catch (error) {
    console.error('加载 A/B 测试失败:', error)
  }
}

// 查看 A/B 测试详情
async function viewABTest(testId: string) {
  try {
    const response = await fetch(`${API_BASE}/title/ab-test/${testId}`)
    const result = await response.json()
    
    if (result.success) {
      currentABTest.value = result.data
    }
  } catch (error) {
    console.error('加载 A/B 测试详情失败:', error)
  }
}

// 加载历史记录
async function loadHistory() {
  try {
    const [historyRes, analysisRes] = await Promise.all([
      fetch(`${API_BASE}/title/history?days=${historyDays.value}&limit=20`),
      fetch(`${API_BASE}/title/history/analyze?days=${historyDays.value}`)
    ])

    const historyResult = await historyRes.json()
    const analysisResult = await analysisRes.json()
    
    if (historyResult.success) {
      history.value = historyResult.data.history
    }
    
    if (analysisResult.success) {
      historyAnalysis.value = analysisResult.data
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

// 加载最佳实践
async function loadBestPractices(category: string) {
  practiceCategory.value = category
  try {
    const response = await fetch(`${API_BASE}/title/best-practices/${category}`)
    const result = await response.json()
    
    if (result.success) {
      bestPractices.value = result.data.practices
    }
  } catch (error) {
    console.error('加载最佳实践失败:', error)
  }
}

// 获取评分样式
function getScoreClass(score: number): string {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  if (score >= 60) return 'poor'
  return 'bad'
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载时加载数据
onMounted(() => {
  loadABTests()
  loadHistory()
  loadBestPractices('general')
})
</script>

<style scoped>
.title-optimizer {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: #6b7280;
}

/* 卡片 */
.card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

/* 表单 */
.form-group {
  margin-bottom: 16px;
  flex: 1;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

.form-row {
  display: flex;
  gap: 16px;
}

/* 按钮 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-lg {
  padding: 12px 28px;
  font-size: 16px;
}

/* 生成的标题 */
.generated-titles {
  margin-top: 24px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.title-card {
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.title-card:hover {
  border-color: #667eea;
  background: #f9fafb;
}

.title-card.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.title-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.title-card-text {
  font-size: 15px;
  color: #1f2937;
  font-weight: 500;
  flex: 1;
}

.title-card-score {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-left: 12px;
}

.title-card-score.excellent { background: #d1fae5; color: #065f46; }
.title-card-score.good { background: #dbeafe; color: #1e40af; }
.title-card-score.average { background: #fef3c7; color: #92400e; }
.title-card-score.poor { background: #fee2e2; color: #991b1b; }
.title-card-score.bad { background: #f3f4f6; color: #6b7280; }

.title-card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #6b7280;
}

.title-card-template {
  font-style: italic;
}

/* A/B 测试 */
.ab-test-form {
  margin-bottom: 20px;
}

.ab-test-result {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
}

.ab-test-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ab-test-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.ab-test-prediction {
  font-size: 14px;
  color: #6b7280;
}

.winner-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 8px;
}

.winner-badge.a { background: #dbeafe; color: #1e40af; }
.winner-badge.b { background: #fef3c7; color: #92400e; }

.ab-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.ab-variant {
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
}

.variant-label {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
}

.variant-content {
  font-size: 15px;
  color: #1f2937;
  margin-bottom: 8px;
}

.variant-score {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
}

/* A/B 测试列表 */
.ab-tests-list {
  margin-top: 24px;
}

.ab-test-item {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.ab-test-item:hover {
  border-color: #667eea;
  background: #f9fafb;
}

.ab-test-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.ab-test-id {
  font-size: 13px;
  color: #6b7280;
  font-family: monospace;
}

.ab-test-status {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.ab-test-status.active { background: #dbeafe; color: #1e40af; }
.ab-test-status.completed { background: #d1fae5; color: #065f46; }

.ab-test-item-content {
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
}

.ab-test-title-a,
.ab-test-title-b {
  display: block;
  margin-bottom: 4px;
}

.ab-test-item-footer {
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
}

.ab-test-winner {
  font-size: 14px;
  font-weight: 600;
  color: #059669;
}

/* 历史记录 */
.history-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.history-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  text-align: center;
  color: white;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.history-list {
  margin-top: 16px;
}

.history-item {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 10px;
}

.history-item-title {
  font-size: 15px;
  color: #1f2937;
  margin-bottom: 8px;
}

.history-item-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}

.history-item-category {
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 4px;
}

.history-item-score {
  font-weight: 600;
  color: #667eea;
}

/* 最佳实践 */
.practice-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.practice-tab {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.practice-tab:hover {
  border-color: #667eea;
}

.practice-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.practice-content {
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
}

.practice-section {
  margin-bottom: 20px;
}

.practice-subtitle {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.practice-text {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
}

.practice-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.practice-tag {
  padding: 6px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  font-size: 13px;
  color: #374151;
}

.practice-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.practice-list li {
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
  font-size: 14px;
  color: #6b7280;
}

.practice-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #10b981;
  font-weight: bold;
}

.practice-examples {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.practice-example {
  padding: 12px;
  background: white;
  border-left: 3px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .card {
    background: #1f2937;
  }
  
  .page-title,
  .section-title,
  .list-title {
    color: #f9fafb;
  }
  
  .page-subtitle {
    color: #9ca3af;
  }
  
  .form-label {
    color: #e5e7eb;
  }
  
  .form-input,
  .form-select,
  .form-textarea {
    background: #374151;
    border-color: #4b5563;
    color: #f9fafb;
  }
  
  .btn-secondary {
    background: #374151;
    color: #e5e7eb;
  }
  
  .title-card {
    background: #374151;
    border-color: #4b5563;
  }
  
  .title-card:hover,
  .title-card.selected {
    background: #4b5563;
  }
  
  .title-card-text {
    color: #f9fafb;
  }
  
  .ab-variant {
    background: #374151;
    border-color: #4b5563;
  }
  
  .variant-content {
    color: #f9fafb;
  }
  
  .ab-test-item {
    background: #374151;
    border-color: #4b5563;
  }
  
  .ab-test-item:hover {
    background: #4b5563;
  }
  
  .history-item {
    background: #374151;
    border-color: #4b5563;
  }
  
  .history-item-title {
    color: #f9fafb;
  }
  
  .practice-content {
    background: #374151;
  }
  
  .practice-tab {
    background: #374151;
    border-color: #4b5563;
    color: #e5e7eb;
  }
  
  .practice-tag {
    background: #4b5563;
    border-color: #6b7280;
    color: #f9fafb;
  }
  
  .practice-example {
    background: #4b5563;
  }
}
</style>
