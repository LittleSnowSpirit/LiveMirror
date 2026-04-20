<template>
  <div class="roi-analysis-page">
    <div class="page-header">
      <h1>📊 ROI 分析</h1>
      <p class="page-subtitle">投入产出比分析，优化直播成本结构</p>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ 新建场次
      </button>
      <button @click="loadSessions" class="btn btn-secondary" :disabled="loading">
        🔄 刷新
      </button>
      <button @click="showCompareModal = true" class="btn btn-secondary" :disabled="sessions.length < 2">
        ⚖️ 对比分析
      </button>
      <button @click="generateReport" class="btn btn-success">
        📄 生成报告
      </button>
    </div>

    <!-- 总体指标 -->
    <div v-if="overallMetrics" class="metrics-overview">
      <div class="metric-card highlight">
        <div class="metric-icon">💰</div>
        <div class="metric-content">
          <div class="metric-label">总成本</div>
          <div class="metric-value">¥{{ formatNumber(overallMetrics.total_cost) }}</div>
        </div>
      </div>
      
      <div class="metric-card highlight">
        <div class="metric-icon">📈</div>
        <div class="metric-content">
          <div class="metric-label">总收益</div>
          <div class="metric-value">¥{{ formatNumber(overallMetrics.total_revenue) }}</div>
        </div>
      </div>
      
      <div class="metric-card highlight">
        <div class="metric-icon">💵</div>
        <div class="metric-content">
          <div class="metric-label">总 GMV</div>
          <div class="metric-value">¥{{ formatNumber(overallMetrics.total_gmv) }}</div>
        </div>
      </div>
      
      <div class="metric-card" :class="roiClass(overallMetrics.overall_roi)">
        <div class="metric-icon">🎯</div>
        <div class="metric-content">
          <div class="metric-label">整体 ROI</div>
          <div class="metric-value">{{ overallMetrics.overall_roi.toFixed(2) }}%</div>
        </div>
      </div>
    </div>

    <!-- ROI 趋势图表 -->
    <div class="chart-section">
      <div class="chart-header">
        <h2>📈 ROI 趋势</h2>
        <div class="chart-controls">
          <select v-model="trendGroupBy" @change="loadTrendData" class="form-input">
            <option value="day">按天</option>
            <option value="week">按周</option>
            <option value="month">按月</option>
          </select>
        </div>
      </div>
      <div class="chart-container">
        <ROIChart 
          v-if="trendData.length > 0"
          :data="trendData"
          :chart-type="'trend'"
        />
        <div v-else class="empty-chart">
          <p>暂无趋势数据</p>
        </div>
      </div>
    </div>

    <!-- 成本分解 -->
    <div v-if="costBreakdown && Object.keys(costBreakdown).length > 0" class="breakdown-section">
      <h2>💸 成本分解</h2>
      <div class="breakdown-grid">
        <div 
          v-for="(amount, type) in costBreakdown" 
          :key="type"
          class="breakdown-item"
        >
          <div class="breakdown-label">{{ getCostTypeName(type) }}</div>
          <div class="breakdown-amount">¥{{ formatNumber(amount) }}</div>
          <div class="breakdown-bar">
            <div 
              class="breakdown-fill"
              :style="{ width: getCostPercentage(amount) + '%' }"
              :class="getCostTypeClass(type)"
            ></div>
          </div>
          <div class="breakdown-percent">{{ getCostPercentage(amount).toFixed(1) }}%</div>
        </div>
      </div>
    </div>

    <!-- 场次列表 -->
    <div class="sessions-section">
      <div class="section-header">
        <h2>📋 直播场次</h2>
        <div class="section-filters">
          <input 
            type="date" 
            v-model="filters.startDate"
            @change="loadSessions"
            class="form-input"
            placeholder="开始日期"
          />
          <input 
            type="date" 
            v-model="filters.endDate"
            @change="loadSessions"
            class="form-input"
            placeholder="结束日期"
          />
          <select v-model="filters.category" @change="loadSessions" class="form-input">
            <option value="">全部分类</option>
            <option value="general">通用</option>
            <option value="beauty">美妆</option>
            <option value="fashion">服装</option>
            <option value="food">食品</option>
            <option value="electronics">数码</option>
            <option value="home">家居</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="sessions.length === 0" class="empty-state">
        <p>暂无场次数据，点击"新建场次"添加</p>
      </div>

      <div v-else class="sessions-table">
        <table>
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  :checked="allSelected"
                  @change="toggleAllSelection"
                />
              </th>
              <th>日期</th>
              <th>时间段</th>
              <th>分类</th>
              <th>成本</th>
              <th>收益</th>
              <th>GMV</th>
              <th>ROI</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="session in sessions" :key="session.session_id">
              <td>
                <input 
                  type="checkbox" 
                  :value="session.session_id"
                  v-model="selectedSessions"
                />
              </td>
              <td>{{ session.date }}</td>
              <td>{{ session.start_time }} - {{ session.end_time }}</td>
              <td>
                <span class="category-tag" :class="session.category">
                  {{ getCategoryName(session.category) }}
                </span>
              </td>
              <td class="cost">¥{{ formatNumber(session.total_cost) }}</td>
              <td class="revenue">¥{{ formatNumber(session.total_revenue) }}</td>
              <td class="gmv">¥{{ formatNumber(session.gmv) }}</td>
              <td>
                <span class="roi-badge" :class="roiClass(session.roi)">
                  {{ session.roi.toFixed(2) }}%
                </span>
              </td>
              <td class="actions">
                <button @click="viewSession(session)" class="btn-icon" title="查看详情">
                  👁️
                </button>
                <button @click="viewSuggestions(session.session_id)" class="btn-icon" title="优化建议">
                  💡
                </button>
                <button @click="deleteSession(session.session_id)" class="btn-icon delete" title="删除">
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 创建/编辑场次弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>➕ 新建场次</h2>
          <button @click="showCreateModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>日期</label>
            <input type="date" v-model="newSession.date" class="form-input" />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>开始时间</label>
              <input type="time" v-model="newSession.start_time" class="form-input" />
            </div>
            <div class="form-group">
              <label>结束时间</label>
              <input type="time" v-model="newSession.end_time" class="form-input" />
            </div>
          </div>
          
          <div class="form-group">
            <label>分类</label>
            <select v-model="newSession.category" class="form-input">
              <option value="general">通用</option>
              <option value="beauty">美妆</option>
              <option value="fashion">服装</option>
              <option value="food">食品</option>
              <option value="electronics">数码</option>
              <option value="home">家居</option>
            </select>
          </div>
          
          <!-- 成本项 -->
          <div class="form-section">
            <div class="section-title">
              <h3>💸 成本项</h3>
              <button @click="addCostItem" class="btn-add">➕ 添加</button>
            </div>
            <div v-for="(cost, index) in newSession.costs" :key="index" class="cost-item">
              <select v-model="cost.type" class="form-input">
                <option value="labor">人力成本</option>
                <option value="venue">场地成本</option>
                <option value="promotion">推广成本</option>
                <option value="equipment">设备成本</option>
                <option value="other">其他</option>
              </select>
              <input 
                type="text" 
                v-model="cost.name" 
                placeholder="名称"
                class="form-input"
              />
              <input 
                type="number" 
                v-model.number="cost.amount" 
                placeholder="金额"
                class="form-input"
              />
              <button @click="removeCostItem(index)" class="btn-remove">✕</button>
            </div>
          </div>
          
          <!-- 收益项 -->
          <div class="form-section">
            <div class="section-title">
              <h3>📈 收益项</h3>
              <button @click="addRevenueItem" class="btn-add">➕ 添加</button>
            </div>
            <div v-for="(revenue, index) in newSession.revenues" :key="index" class="revenue-item">
              <select v-model="revenue.type" class="form-input">
                <option value="gmv">GMV</option>
                <option value="profit">利润</option>
                <option value="commission">佣金</option>
              </select>
              <input 
                type="text" 
                v-model="revenue.name" 
                placeholder="名称"
                class="form-input"
              />
              <input 
                type="number" 
                v-model.number="revenue.amount" 
                placeholder="金额"
                class="form-input"
              />
              <button @click="removeRevenueItem(index)" class="btn-remove">✕</button>
            </div>
          </div>
          
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="newSession.notes" class="form-input" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-secondary">取消</button>
          <button @click="createSession" class="btn btn-primary" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 对比分析弹窗 -->
    <div v-if="showCompareModal" class="modal-overlay" @click.self="showCompareModal = false">
      <div class="modal modal-large">
        <div class="modal-header">
          <h2>⚖️ 对比分析</h2>
          <button @click="showCompareModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="compareResult" class="compare-result">
            <div class="compare-summary">
              <div class="summary-item">
                <div class="summary-label">平均 ROI</div>
                <div class="summary-value">{{ compareResult.average_roi.toFixed(2) }}%</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">最佳场次</div>
                <div class="summary-value highlight">{{ compareResult.best_roi_session }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">最差场次</div>
                <div class="summary-value low">{{ compareResult.worst_roi_session }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">趋势</div>
                <div class="summary-value" :class="trendClass(compareResult.roi_trend)">
                  {{ getTrendName(compareResult.roi_trend) }}
                </div>
              </div>
            </div>
            
            <div class="compare-insights">
              <h3>💡 分析洞察</h3>
              <ul>
                <li v-for="(insight, index) in compareResult.insights" :key="index">
                  {{ insight }}
                </li>
              </ul>
            </div>
            
            <div class="compare-metrics">
              <h3>📊 详细指标</h3>
              <table class="compare-table">
                <thead>
                  <tr>
                    <th>场次</th>
                    <th>日期</th>
                    <th>成本</th>
                    <th>收益</th>
                    <th>ROI</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(metrics, sessionId) in compareResult.metrics" :key="sessionId">
                    <td>{{ sessionId }}</td>
                    <td>{{ metrics.date }}</td>
                    <td>¥{{ formatNumber(metrics.total_cost) }}</td>
                    <td>¥{{ formatNumber(metrics.total_revenue) }}</td>
                    <td>
                      <span :class="roiClass(metrics.roi_percentage)">
                        {{ metrics.roi_percentage.toFixed(2) }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>请选择至少 2 个场次进行对比</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCompareModal = false" class="btn btn-secondary">关闭</button>
          <button @click="runComparison" class="btn btn-primary" :disabled="selectedSessions.length < 2">
            开始对比
          </button>
        </div>
      </div>
    </div>

    <!-- 优化建议弹窗 -->
    <div v-if="showSuggestionsModal" class="modal-overlay" @click.self="showSuggestionsModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>💡 优化建议</h2>
          <button @click="showSuggestionsModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="suggestions.length > 0" class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestions" 
              :key="index"
              class="suggestion-item"
              :class="suggestion.priority"
            >
              <div class="suggestion-header">
                <span class="suggestion-category">{{ getSuggestionCategory(suggestion.category) }}</span>
                <span class="suggestion-priority" :class="suggestion.priority">
                  {{ getPriorityName(suggestion.priority) }}
                </span>
              </div>
              <div class="suggestion-content">
                {{ suggestion.suggestion }}
              </div>
              <div class="suggestion-footer">
                <span>预期影响：{{ suggestion.expected_impact }}</span>
                <span v-if="suggestion.estimated_savings > 0">
                  预计节省：¥{{ formatNumber(suggestion.estimated_savings) }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>暂无优化建议</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showSuggestionsModal = false" class="btn btn-secondary">关闭</button>
        </div>
      </div>
    </div>

    <!-- 报告预览弹窗 -->
    <div v-if="showReportModal" class="modal-overlay" @click.self="showReportModal = false">
      <div class="modal modal-large">
        <div class="modal-header">
          <h2>📄 ROI 分析报告</h2>
          <button @click="showReportModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="report" class="report-content">
            <div class="report-summary">
              <h3>📊 总体概览</h3>
              <div class="summary-grid">
                <div class="summary-stat">
                  <div class="stat-label">总场次</div>
                  <div class="stat-value">{{ report.summary.total_sessions }}</div>
                </div>
                <div class="summary-stat">
                  <div class="stat-label">总成本</div>
                  <div class="stat-value">¥{{ formatNumber(report.summary.total_cost) }}</div>
                </div>
                <div class="summary-stat">
                  <div class="stat-label">总收益</div>
                  <div class="stat-value">¥{{ formatNumber(report.summary.total_revenue) }}</div>
                </div>
                <div class="summary-stat">
                  <div class="stat-label">总利润</div>
                  <div class="stat-value">¥{{ formatNumber(report.summary.total_profit) }}</div>
                </div>
                <div class="summary-stat">
                  <div class="stat-label">整体 ROI</div>
                  <div class="stat-value" :class="roiClass(report.summary.overall_roi)">
                    {{ report.summary.overall_roi.toFixed(2) }}%
                  </div>
                </div>
              </div>
            </div>
            
            <div class="report-performers">
              <div class="performer-item best">
                <h4>🏆 最佳表现</h4>
                <p>{{ report.best_performer.session_id }}</p>
                <p class="performer-roi">{{ report.best_performer.roi.toFixed(2) }}%</p>
              </div>
              <div class="performer-item worst">
                <h4>📉 最差表现</h4>
                <p>{{ report.worst_performer.session_id }}</p>
                <p class="performer-roi">{{ report.worst_performer.roi.toFixed(2) }}%</p>
              </div>
            </div>
            
            <div class="report-suggestions">
              <h3>💡 优化建议</h3>
              <ul>
                <li v-for="(suggestion, index) in report.optimization_suggestions" :key="index">
                  <strong>{{ getSuggestionCategory(suggestion.category) }}:</strong>
                  {{ suggestion.suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showReportModal = false" class="btn btn-secondary">关闭</button>
          <button @click="downloadReport" class="btn btn-primary">
            📥 下载报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ROIChart from '../components/ROIChart.vue'
import { api } from '../utils/api'

// 状态
const loading = ref(false)
const saving = ref(false)
const sessions = ref<any[]>([])
const trendData = ref<any[]>([])
const overallMetrics = ref<any>(null)
const costBreakdown = ref<any>({})
const trendGroupBy = ref('day')

// 筛选器
const filters = ref({
  startDate: '',
  endDate: '',
  category: ''
})

// 选择
const selectedSessions = ref<string[]>([])
const showCreateModal = ref(false)
const showCompareModal = ref(false)
const showSuggestionsModal = ref(false)
const showReportModal = ref(false)

// 新建场次表单
const newSession = ref({
  date: new Date().toISOString().split('T')[0],
  start_time: '19:00',
  end_time: '22:00',
  category: 'general',
  costs: [] as any[],
  revenues: [] as any[],
  notes: ''
})

// 对比结果
const compareResult = ref<any>(null)

// 优化建议
const suggestions = ref<any[]>([])

// 报告
const report = ref<any>(null)

// 计算属性
const allSelected = computed(() => {
  return sessions.value.length > 0 && selectedSessions.value.length === sessions.value.length
})

// 生命周期
onMounted(() => {
  loadSessions()
  loadTrendData()
})

// 方法
async function loadSessions() {
  loading.value = true
  try {
    const params: any = {}
    if (filters.value.startDate) params.start_date = filters.value.startDate
    if (filters.value.endDate) params.end_date = filters.value.endDate
    if (filters.value.category) params.category = filters.value.category
    
    const res = await api.get('/api/roi/sessions', { params })
    sessions.value = res.data.data || []
    calculateOverallMetrics()
  } catch (error) {
    console.error('加载场次失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadTrendData() {
  try {
    const res = await api.post('/api/roi/trend', {
      group_by: trendGroupBy.value
    })
    trendData.value = res.data.data || []
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
}

function calculateOverallMetrics() {
  if (sessions.value.length === 0) {
    overallMetrics.value = null
    costBreakdown.value = {}
    return
  }
  
  const total_cost = sessions.value.reduce((sum, s) => sum + s.total_cost, 0)
  const total_revenue = sessions.value.reduce((sum, s) => sum + s.total_revenue, 0)
  const total_gmv = sessions.value.reduce((sum, s) => sum + s.gmv, 0)
  const overall_roi = total_cost > 0 ? ((total_revenue - total_cost) / total_cost) * 100 : 0
  
  overallMetrics.value = {
    total_cost,
    total_revenue,
    total_gmv,
    overall_roi
  }
  
  // 计算成本分解
  const breakdown: any = {}
  sessions.value.forEach(session => {
    session.costs.forEach((cost: any) => {
      if (!breakdown[cost.type]) breakdown[cost.type] = 0
      breakdown[cost.type] += cost.amount
    })
  })
  costBreakdown.value = breakdown
}

async function createSession() {
  saving.value = true
  try {
    await api.post('/api/roi/sessions', newSession.value)
    showCreateModal.value = false
    loadSessions()
    loadTrendData()
    resetNewSession()
  } catch (error) {
    console.error('创建场次失败:', error)
    alert('创建失败，请重试')
  } finally {
    saving.value = false
  }
}

function resetNewSession() {
  newSession.value = {
    date: new Date().toISOString().split('T')[0],
    start_time: '19:00',
    end_time: '22:00',
    category: 'general',
    costs: [],
    revenues: [],
    notes: ''
  }
}

function addCostItem() {
  newSession.value.costs.push({
    type: 'labor',
    name: '',
    amount: 0
  })
}

function removeCostItem(index: number) {
  newSession.value.costs.splice(index, 1)
}

function addRevenueItem() {
  newSession.value.revenues.push({
    type: 'gmv',
    name: '',
    amount: 0
  })
}

function removeRevenueItem(index: number) {
  newSession.value.revenues.splice(index, 1)
}

async function deleteSession(sessionId: string) {
  if (!confirm('确定删除该场次吗？')) return
  
  try {
    await api.delete(`/api/roi/sessions/${sessionId}`)
    loadSessions()
    loadTrendData()
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败，请重试')
  }
}

function viewSession(session: any) {
  // TODO: 实现详情查看
  alert('查看详情功能开发中')
}

async function viewSuggestions(sessionId: string) {
  try {
    const res = await api.get(`/api/roi/sessions/${sessionId}/suggestions`)
    suggestions.value = res.data.data || []
    showSuggestionsModal.value = true
  } catch (error) {
    console.error('获取建议失败:', error)
  }
}

function toggleAllSelection() {
  if (allSelected.value) {
    selectedSessions.value = []
  } else {
    selectedSessions.value = sessions.value.map(s => s.session_id)
  }
}

async function runComparison() {
  if (selectedSessions.value.length < 2) return
  
  try {
    const res = await api.post('/api/roi/compare', {
      session_ids: selectedSessions.value
    })
    compareResult.value = res.data.data
  } catch (error) {
    console.error('对比失败:', error)
  }
}

async function generateReport() {
  try {
    const res = await api.post('/api/roi/report')
    report.value = res.data.data
    showReportModal.value = true
  } catch (error) {
    console.error('生成报告失败:', error)
    alert('生成报告失败，请重试')
  }
}

function downloadReport() {
  if (!report.value) return
  
  const blob = new Blob([JSON.stringify(report.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ROI_Report_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 工具函数
function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

function getCostTypeName(type: string): string {
  const names: any = {
    labor: '人力成本',
    venue: '场地成本',
    promotion: '推广成本',
    equipment: '设备成本',
    other: '其他成本'
  }
  return names[type] || type
}

function getCostTypeClass(type: string): string {
  return `cost-${type}`
}

function getCostPercentage(amount: number): number {
  if (!overallMetrics.value || overallMetrics.value.total_cost === 0) return 0
  return (amount / overallMetrics.value.total_cost) * 100
}

function getCategoryName(category: string): string {
  const names: any = {
    general: '通用',
    beauty: '美妆',
    fashion: '服装',
    food: '食品',
    electronics: '数码',
    home: '家居'
  }
  return names[category] || category
}

function roiClass(roi: number): string {
  if (roi >= 100) return 'excellent'
  if (roi >= 50) return 'good'
  if (roi >= 0) return 'normal'
  return 'negative'
}

function getSuggestionCategory(category: string): string {
  const names: any = {
    labor: '人力优化',
    venue: '场地优化',
    promotion: '推广优化',
    equipment: '设备优化',
    duration: '时长优化',
    overall: '整体优化'
  }
  return names[category] || category
}

function getPriorityName(priority: string): string {
  const names: any = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return names[priority] || priority
}

function getTrendName(trend: string): string {
  const names: any = {
    increasing: '上升',
    decreasing: '下降',
    stable: '稳定'
  }
  return names[trend] || trend
}

function trendClass(trend: string): string {
  return trend
}
</script>

<style scoped>
.roi-analysis-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

.quick-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

/* 总体指标 */
.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.metric-card.highlight {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
}

.metric-icon {
  font-size: 2.5rem;
}

.metric-label {
  font-size: 0.875rem;
  opacity: 0.8;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.metric-card.excellent {
  border-left: 4px solid #10b981;
}

.metric-card.good {
  border-left: 4px solid #3b82f6;
}

.metric-card.normal {
  border-left: 4px solid #f59e0b;
}

.metric-card.negative {
  border-left: 4px solid #ef4444;
}

/* 图表区域 */
.chart-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-container {
  height: 300px;
}

.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

/* 成本分解 */
.breakdown-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.breakdown-section h2 {
  margin-bottom: 1rem;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.breakdown-item {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 8px;
}

.breakdown-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.breakdown-amount {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.breakdown-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.breakdown-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.breakdown-fill.cost-labor {
  background: #3b82f6;
}

.breakdown-fill.cost-venue {
  background: #10b981;
}

.breakdown-fill.cost-promotion {
  background: #f59e0b;
}

.breakdown-fill.cost-equipment {
  background: #8b5cf6;
}

.breakdown-fill.cost-other {
  background: #6b7280;
}

.breakdown-percent {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 场次列表 */
.sessions-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-filters {
  display: flex;
  gap: 0.5rem;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--bg-tertiary);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.sessions-table {
  overflow-x: auto;
}

.sessions-table table {
  width: 100%;
  border-collapse: collapse;
}

.sessions-table th,
.sessions-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.sessions-table th {
  background: var(--bg-secondary);
  font-weight: 600;
}

.sessions-table tr:hover {
  background: var(--bg-secondary);
}

.category-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  background: var(--bg-tertiary);
}

.cost {
  color: #ef4444;
}

.revenue {
  color: #10b981;
}

.gmv {
  color: #3b82f6;
}

.roi-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.roi-badge.excellent {
  background: #d1fae5;
  color: #065f46;
}

.roi-badge.good {
  background: #dbeafe;
  color: #1e40af;
}

.roi-badge.normal {
  background: #fef3c7;
  color: #92400e;
}

.roi-badge.negative {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: var(--bg-tertiary);
}

.btn-icon.delete:hover {
  background: #fee2e2;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--card-bg);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

/* 表单样式 */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-section {
  margin: 1.5rem 0;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-add {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}

.cost-item,
.revenue-item {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr auto;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.btn-remove {
  background: #ef4444;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
}

/* 对比结果 */
.compare-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-item {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: bold;
}

.summary-value.highlight {
  color: #10b981;
}

.summary-value.low {
  color: #ef4444;
}

.compare-insights {
  margin-bottom: 2rem;
}

.compare-insights ul {
  list-style: disc;
  padding-left: 1.5rem;
}

.compare-insights li {
  margin-bottom: 0.5rem;
}

.compare-table {
  width: 100%;
  border-collapse: collapse;
}

.compare-table th,
.compare-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.compare-table th {
  background: var(--bg-secondary);
}

/* 优化建议 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.suggestion-item {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid var(--border-color);
}

.suggestion-item.high {
  border-left-color: #ef4444;
}

.suggestion-item.medium {
  border-left-color: #f59e0b;
}

.suggestion-item.low {
  border-left-color: #10b981;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.suggestion-category {
  font-weight: 600;
}

.suggestion-priority {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
}

.suggestion-priority.high {
  background: #fee2e2;
  color: #991b1b;
}

.suggestion-priority.medium {
  background: #fef3c7;
  color: #92400e;
}

.suggestion-priority.low {
  background: #d1fae5;
  color: #065f46;
}

.suggestion-content {
  margin-bottom: 0.5rem;
}

.suggestion-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 报告 */
.report-summary {
  margin-bottom: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
}

.summary-stat {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: bold;
}

.report-performers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.performer-item {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.performer-item.best {
  border: 2px solid #10b981;
}

.performer-item.worst {
  border: 2px solid #ef4444;
}

.performer-roi {
  font-size: 2rem;
  font-weight: bold;
  margin-top: 0.5rem;
}

.report-suggestions ul {
  list-style: disc;
  padding-left: 1.5rem;
}

.report-suggestions li {
  margin-bottom: 0.5rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .roi-analysis-page {
    padding: 1rem;
  }
  
  .quick-actions {
    flex-wrap: wrap;
  }
  
  .metrics-overview {
    grid-template-columns: 1fr 1fr;
  }
  
  .compare-summary {
    grid-template-columns: 1fr 1fr;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .report-performers {
    grid-template-columns: 1fr;
  }
}
</style>
