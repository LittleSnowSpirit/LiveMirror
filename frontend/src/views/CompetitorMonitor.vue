<template>
  <div class="competitor-monitor">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>🎯 竞品直播间监控</h1>
      <div class="header-actions">
        <span class="monitor-status" :class="{ active: isMonitoring }">
          {{ isMonitoring ? '🟢 监控中' : '🔴 已停止' }}
        </span>
        <el-button 
          :type="isMonitoring ? 'warning' : 'success'" 
          @click="toggleMonitoring"
          :loading="monitoringLoading"
        >
          {{ isMonitoring ? '停止监控' : '启动监控' }}
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">监控竞品数</div>
          <div class="stat-value">{{ stats.competitor_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">告警规则</div>
          <div class="stat-value">{{ stats.rule_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">总告警数</div>
          <div class="stat-value">{{ stats.total_alerts }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-label">今日告警</div>
          <div class="stat-value today-alerts">{{ todayAlertCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：竞品列表 -->
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>📺 竞品列表</span>
              <el-button type="primary" size="small" @click="showAddCompetitorDialog">
                + 添加竞品
              </el-button>
            </div>
          </template>

          <el-table :data="competitors" style="width: 100%" v-loading="loading">
            <el-table-column prop="name" label="竞品名称" />
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }">
                <el-tag :type="getPlatformType(row.platform)" size="small">
                  {{ getPlatformName(row.platform) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '监控中' : '已暂停' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="viewCompetitorDetail(row)">
                  详情
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="removeCompetitor(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 告警规则配置 -->
        <el-card class="section-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>⚠️ 告警规则</span>
              <el-button type="primary" size="small" @click="showAddRuleDialog">
                + 添加规则
              </el-button>
            </div>
          </template>

          <el-table :data="alertRules" style="width: 100%">
            <el-table-column prop="name" label="规则名称" />
            <el-table-column prop="rule_type" label="类型" width="120">
              <template #default="{ row }">
                {{ getRuleTypeName(row.rule_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="threshold" label="阈值" width="100" />
            <el-table-column prop="enabled" label="状态" width="80">
              <template #default="{ row }">
                <el-switch 
                  v-model="row.enabled" 
                  @change="toggleRuleStatus(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="removeRule(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：实时监控和告警 -->
      <el-col :span="12">
        <!-- 实时数据 -->
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>📊 实时监控</span>
              <el-select v-model="selectedCompetitor" size="small" @change="loadLiveData">
                <el-option 
                  v-for="c in competitors" 
                  :key="c.id" 
                  :label="c.name" 
                  :value="c.id"
                />
              </el-select>
            </div>
          </template>

          <div v-if="liveData" class="live-data">
            <div class="data-grid">
              <div class="data-item">
                <div class="data-label">👥 在线观众</div>
                <div class="data-value highlight">{{ liveData.viewer_count.toLocaleString() }}</div>
              </div>
              <div class="data-item">
                <div class="data-label">❤️ 点赞数</div>
                <div class="data-value">{{ liveData.like_count.toLocaleString() }}</div>
              </div>
              <div class="data-item">
                <div class="data-label">💬 评论数</div>
                <div class="data-value">{{ liveData.comment_count.toLocaleString() }}</div>
              </div>
              <div class="data-item">
                <div class="data-label">📤 分享数</div>
                <div class="data-value">{{ liveData.share_count.toLocaleString() }}</div>
              </div>
              <div class="data-item">
                <div class="data-label">🛍️ 商品数</div>
                <div class="data-value">{{ liveData.product_count }}</div>
              </div>
              <div class="data-item">
                <div class="data-label">💰 成交额</div>
                <div class="data-value highlight">¥{{ liveData.gmv.toLocaleString() }}</div>
              </div>
              <div class="data-item">
                <div class="data-label">⏱️ 平均观看</div>
                <div class="data-value">{{ liveData.avg_watch_time }}s</div>
              </div>
              <div class="data-item">
                <div class="data-label">🕐 更新时间</div>
                <div class="data-value small">{{ formatTime(liveData.capture_time) }}</div>
              </div>
            </div>

            <!-- 观众数趋势图 -->
            <div class="chart-container" v-if="viewerTrendData.length > 0">
              <div ref="viewerChart" class="chart"></div>
            </div>
          </div>

          <el-empty v-else description="暂无实时数据" />
        </el-card>

        <!-- 最新告警 -->
        <el-card class="section-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>🔔 最新告警</span>
              <el-button size="small" @click="loadAlerts">
                刷新
              </el-button>
            </div>
          </template>

          <el-timeline>
            <el-timeline-item 
              v-for="alert in recentAlerts" 
              :key="alert.id"
              :type="getAlertType(alert.alert_type)"
              :timestamp="formatTime(alert.triggered_at)"
              placement="top"
            >
              <el-card>
                <h4>{{ alert.rule_name }}</h4>
                <p>{{ alert.competitor_name }}: {{ alert.message }}</p>
                <el-tag size="small" :type="alert.notified ? 'success' : 'warning'">
                  {{ alert.notified ? '已通知' : '未通知' }}
                </el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>

          <el-empty v-if="recentAlerts.length === 0" description="暂无告警" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加竞品对话框 -->
    <el-dialog 
      v-model="addCompetitorDialogVisible" 
      title="添加竞品" 
      width="500px"
    >
      <el-form :model="newCompetitor" label-width="80px">
        <el-form-item label="竞品名称">
          <el-input v-model="newCompetitor.name" placeholder="请输入竞品名称" />
        </el-form-item>
        <el-form-item label="平台">
          <el-select v-model="newCompetitor.platform" placeholder="请选择平台">
            <el-option label="抖音" value="douyin" />
            <el-option label="淘宝" value="taobao" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="视频号" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="直播间 ID">
          <el-input v-model="newCompetitor.room_id" placeholder="请输入直播间 ID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCompetitorDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addCompetitor" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加告警规则对话框 -->
    <el-dialog 
      v-model="addRuleDialogVisible" 
      title="添加告警规则" 
      width="500px"
    >
      <el-form :model="newRule" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="newRule.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="newRule.rule_type" placeholder="请选择规则类型">
            <el-option label="流量突增" value="viewer_spike" />
            <el-option label="话术抄袭" value="script_plagiarism" />
            <el-option label="成交额阈值" value="gmv_threshold" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值">
          <el-input-number v-model="newRule.threshold" :min="0" :step="0.1" />
        </el-form-item>
        <el-form-item label="比较方式">
          <el-select v-model="newRule.comparison" placeholder="请选择比较方式">
            <el-option label="大于" value="gt" />
            <el-option label="小于" value="lt" />
            <el-option label="等于" value="eq" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用竞品">
          <el-select v-model="newRule.competitor_id" placeholder="空表示所有竞品" clearable>
            <el-option 
              v-for="c in competitors" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addRuleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addRule" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 竞品详情对话框 -->
    <el-dialog 
      v-model="competitorDetailVisible" 
      title="竞品详情" 
      width="800px"
    >
      <div v-if="selectedCompetitorData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="竞品名称">
            {{ selectedCompetitorData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="平台">
            {{ getPlatformName(selectedCompetitorData.platform) }}
          </el-descriptions-item>
          <el-descriptions-item label="直播间 ID">
            {{ selectedCompetitorData.room_id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedCompetitorData.status === 'active' ? 'success' : 'info'">
              {{ selectedCompetitorData.status === 'active' ? '监控中' : '已暂停' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="添加时间">
            {{ formatTime(selectedCompetitorData.added_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 话术记录 -->
        <h4 style="margin-top: 20px;">📝 直播话术记录</h4>
        <el-table :data="scriptSegments" style="width: 100%" max-height="300">
          <el-table-column prop="content" label="话术内容" />
          <el-table-column prop="similarity_score" label="相似度" width="100">
            <template #default="{ row }">
              <el-tag :type="row.similarity_score > 0.8 ? 'danger' : 'success'" size="small">
                {{ (row.similarity_score * 100).toFixed(1) }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.timestamp) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CompetitorAlert from '../components/CompetitorAlert.vue'
import * as echarts from 'echarts'

// API 基础 URL
const API_BASE = '/api/monitor'

// 状态
const loading = ref(false)
const monitoringLoading = ref(false)
const submitLoading = ref(false)
const isMonitoring = ref(false)
const selectedCompetitor = ref('')
const stats = reactive({
  competitor_count: 0,
  rule_count: 0,
  total_alerts: 0,
  alerts_by_type: {}
})

// 数据
const competitors = ref([])
const alertRules = ref([])
const liveData = ref(null)
const recentAlerts = ref([])
const viewerTrendData = ref([])
const scriptSegments = ref([])

// 对话框
const addCompetitorDialogVisible = ref(false)
const addRuleDialogVisible = ref(false)
const competitorDetailVisible = ref(false)

// 表单
const newCompetitor = reactive({
  name: '',
  platform: '',
  room_id: ''
})

const newRule = reactive({
  name: '',
  rule_type: 'viewer_spike',
  threshold: 2.0,
  comparison: 'gt',
  competitor_id: ''
})

const selectedCompetitorData = ref(null)

// 计算属性
const todayAlertCount = computed(() => {
  const today = new Date().toDateString()
  return recentAlerts.value.filter(a => 
    new Date(a.triggered_at).toDateString() === today
  ).length
})

// 图表实例
let viewerChartInstance = null

// 生命周期
onMounted(() => {
  loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  if (viewerChartInstance) {
    viewerChartInstance.dispose()
  }
})

// 方法
async function loadData() {
  loading.value = true
  try {
    await Promise.all([
      loadCompetitors(),
      loadAlertRules(),
      loadStats(),
      loadAlerts()
    ])
  } finally {
    loading.value = false
  }
}

async function loadCompetitors() {
  const res = await fetch(`${API_BASE}/competitors`)
  const data = await res.json()
  competitors.value = data
  if (data.length > 0 && !selectedCompetitor.value) {
    selectedCompetitor.value = data[0].id
  }
}

async function loadAlertRules() {
  const res = await fetch(`${API_BASE}/alert-rules`)
  const data = await res.json()
  alertRules.value = data
}

async function loadStats() {
  const res = await fetch(`${API_BASE}/stats`)
  const data = await res.json()
  Object.assign(stats, data)
  isMonitoring.value = data.is_monitoring
}

async function loadAlerts() {
  const res = await fetch(`${API_BASE}/alerts?limit=20`)
  const data = await res.json()
  recentAlerts.value = data
}

async function loadLiveData() {
  if (!selectedCompetitor.value) return
  
  try {
    const res = await fetch(`${API_BASE}/live-data/${selectedCompetitor.value}`)
    if (res.ok) {
      liveData.value = await res.json()
      
      // 加载历史数据用于图表
      const historyRes = await fetch(`${API_BASE}/live-data/${selectedCompetitor.value}/history?limit=50`)
      const historyData = await historyRes.json()
      viewerTrendData.value = historyData
      
      // 更新图表
      updateViewerChart()
    }
  } catch (e) {
    liveData.value = null
  }
}

async function loadScriptSegments() {
  if (!selectedCompetitorData.value) return
  
  const res = await fetch(`${API_BASE}/scripts/${selectedCompetitorData.value.id}?limit=20`)
  const data = await res.json()
  scriptSegments.value = data
}

async function toggleMonitoring() {
  monitoringLoading.value = true
  try {
    if (isMonitoring.value) {
      await fetch(`${API_BASE}/stop`, { method: 'POST' })
      ElMessage.success('监控已停止')
    } else {
      await fetch(`${API_BASE}/start`, { method: 'POST' })
      ElMessage.success('监控已启动')
    }
    await loadStats()
  } finally {
    monitoringLoading.value = false
  }
}

function showAddCompetitorDialog() {
  Object.assign(newCompetitor, { name: '', platform: '', room_id: '' })
  addCompetitorDialogVisible.value = true
}

async function addCompetitor() {
  if (!newCompetitor.name || !newCompetitor.platform || !newCompetitor.room_id) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  submitLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/competitors`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newCompetitor)
    })
    
    if (res.ok) {
      ElMessage.success('竞品添加成功')
      addCompetitorDialogVisible.value = false
      await loadCompetitors()
      await loadStats()
    } else {
      const error = await res.json()
      ElMessage.error(error.detail || '添加失败')
    }
  } finally {
    submitLoading.value = false
  }
}

async function removeCompetitor(row) {
  try {
    await ElMessageBox.confirm('确定要删除该竞品吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  
  const res = await fetch(`${API_BASE}/competitors/${row.id}`, { method: 'DELETE' })
  if (res.ok) {
    ElMessage.success('删除成功')
    await loadCompetitors()
    await loadStats()
  }
}

function showAddRuleDialog() {
  Object.assign(newRule, { 
    name: '', 
    rule_type: 'viewer_spike', 
    threshold: 2.0, 
    comparison: 'gt',
    competitor_id: ''
  })
  addRuleDialogVisible.value = true
}

async function addRule() {
  if (!newRule.name) {
    ElMessage.warning('请填写规则名称')
    return
  }
  
  submitLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/alert-rules`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newRule)
    })
    
    if (res.ok) {
      ElMessage.success('规则添加成功')
      addRuleDialogVisible.value = false
      await loadAlertRules()
      await loadStats()
    } else {
      const error = await res.json()
      ElMessage.error(error.detail || '添加失败')
    }
  } finally {
    submitLoading.value = false
  }
}

async function toggleRuleStatus(row) {
  const res = await fetch(`${API_BASE}/alert-rules/${row.id}/toggle`, { method: 'POST' })
  if (res.ok) {
    ElMessage.success('状态已更新')
  }
}

async function removeRule(row) {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  
  const res = await fetch(`${API_BASE}/alert-rules/${row.id}`, { method: 'DELETE' })
  if (res.ok) {
    ElMessage.success('删除成功')
    await loadAlertRules()
    await loadStats()
  }
}

async function viewCompetitorDetail(row) {
  selectedCompetitorData.value = row
  competitorDetailVisible.value = true
  await loadScriptSegments()
}

// 工具函数
function getPlatformType(platform) {
  const types = {
    douyin: '',
    taobao: 'warning',
    kuaishou: 'success',
    wechat: 'danger'
  }
  return types[platform] || ''
}

function getPlatformName(platform) {
  const names = {
    douyin: '抖音',
    taobao: '淘宝',
    kuaishou: '快手',
    wechat: '视频号'
  }
  return names[platform] || platform
}

function getRuleTypeName(type) {
  const names = {
    viewer_spike: '流量突增',
    script_plagiarism: '话术抄袭',
    gmv_threshold: '成交额阈值'
  }
  return names[type] || type
}

function getAlertType(type) {
  const types = {
    viewer_spike: 'warning',
    script_plagiarism: 'danger',
    gmv_threshold: 'success'
  }
  return types[type] || ''
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}

// 图表
function updateViewerChart() {
  if (!viewerTrendData.value.length) return
  
  const chartDom = document.querySelector('.chart')
  if (!chartDom) return
  
  if (!viewerChartInstance) {
    viewerChartInstance = echarts.init(chartDom)
  }
  
  const times = viewerTrendData.value.map(d => 
    new Date(d.capture_time).toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  )
  const viewers = viewerTrendData.value.map(d => d.viewer_count)
  
  viewerChartInstance.setOption({
    title: { text: '观众数趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { 
      type: 'category', 
      data: times,
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [{
      data: viewers,
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
        ])
      },
      itemStyle: { color: '#409EFF' }
    }]
  })
}

// 自动刷新
let refreshTimer = null

function startAutoRefresh() {
  refreshTimer = setInterval(() => {
    if (isMonitoring.value && selectedCompetitor.value) {
      loadLiveData()
    }
    loadStats()
  }, 30000) // 30 秒刷新一次
}

function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}
</script>

<style scoped>
.competitor-monitor {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.monitor-status {
  padding: 5px 12px;
  border-radius: 4px;
  background: #f5f5f5;
  font-size: 14px;
}

.monitor-status.active {
  background: #f0f9ff;
  color: #409EFF;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-value.highlight {
  color: #409EFF;
}

.stat-value.today-alerts {
  color: #F56C6C;
}

.main-content {
  min-height: 600px;
}

.section-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.live-data {
  padding: 10px 0;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.data-item {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.data-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.data-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.data-value.highlight {
  color: #67C23A;
  font-size: 24px;
}

.data-value.small {
  font-size: 12px;
  font-weight: normal;
}

.chart-container {
  height: 250px;
  margin-top: 20px;
}

.chart {
  width: 100%;
  height: 100%;
}

:deep(.el-timeline-item__content .el-card) {
  margin-bottom: 10px;
}

:deep(.el-timeline-item__content h4) {
  margin: 0 0 8px 0;
  font-size: 14px;
}

:deep(.el-timeline-item__content p) {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #606266;
}
</style>
