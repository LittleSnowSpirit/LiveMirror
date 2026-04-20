<template>
  <div class="ab-testing-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>🧪 话术 A/B 测试</h1>
      <p class="subtitle">优化直播话术，提升转化效果</p>
    </div>

    <!-- 创建新测试 -->
    <el-card class="create-test-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📝 创建新测试</span>
          <el-button type="primary" @click="showCreateDialog = true">
            + 新建测试
          </el-button>
        </div>
      </template>
    </el-card>

    <!-- 测试列表 -->
    <el-card class="test-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📊 测试列表</span>
          <el-button @click="loadTests">刷新</el-button>
        </div>
      </template>

      <el-table :data="tests" style="width: 100%" v-loading="loading">
        <el-table-column prop="test_id" label="测试 ID" width="180" />
        <el-table-column prop="name" label="测试名称" width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="流量分配" width="200">
          <template #default="{ row }">
            <div class="traffic-allocation">
              <span v-for="(allocation, version) in row.variants" :key="version" class="allocation-tag">
                {{ version }}: {{ (allocation * 100).toFixed(0) }}%
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewTest(row.test_id)">查看</el-button>
            <el-button size="small" type="primary" @click="showManageDialog(row.test_id)">管理</el-button>
            <el-button 
              v-if="row.is_active" 
              size="small" 
              type="warning" 
              @click="stopTest(row.test_id)"
            >
              停止
            </el-button>
            <el-button size="small" type="success" @click="exportReport(row.test_id)">
              导出报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建测试对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建 A/B 测试" width="600px">
      <el-form :model="createForm" label-width="120px">
        <el-form-item label="测试名称">
          <el-input v-model="createForm.name" placeholder="例如：开场话术优化测试" />
        </el-form-item>
        <el-form-item label="测试版本">
          <div v-for="(variant, index) in createForm.variants" :key="index" class="variant-row">
            <el-input v-model="variant.version" placeholder="版本 (A/B/C)" style="width: 80px; margin-right: 10px;" />
            <el-input v-model="variant.content" placeholder="话术内容" style="flex: 1; margin-right: 10px;" />
            <el-input-number v-model="variant.allocation" :min="0" :max="1" :step="0.1" style="width: 100px;" />
            <el-button @click="removeVariant(index)" type="danger" size="small">删除</el-button>
          </div>
          <el-button @click="addVariant" type="primary" size="small" style="margin-top: 10px;">
            + 添加版本
          </el-button>
        </el-form-item>
        <el-form-item label="总流量分配">
          <el-progress 
            :percentage="totalAllocation * 100" 
            :status="totalAllocation === 1 ? 'success' : 'exception'"
          />
          <span v-if="totalAllocation !== 1" class="warning-text">
            流量分配总和必须为 100% (当前：{{ (totalAllocation * 100).toFixed(0) }}%)
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTest" :disabled="totalAllocation !== 1">
          创建测试
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试管理对话框 -->
    <el-dialog v-model="showManageDialogVisible" :title="`管理测试：${currentTestId}`" width="900px">
      <el-tabs v-model="activeTab">
        <!-- 话术版本管理 -->
        <el-tab-pane label="话术版本" name="variants">
          <div v-for="variant in currentVariants" :key="variant.id" class="variant-card">
            <div class="variant-header">
              <el-tag size="large">{{ variant.version }}</el-tag>
              <el-tag :type="variant.is_active ? 'success' : 'info'">
                {{ variant.is_active ? '启用' : '停用' }}
              </el-tag>
            </div>
            <div class="variant-content">{{ variant.content }}</div>
            <div class="variant-actions">
              <el-button size="small" @click="editVariant(variant)">编辑</el-button>
              <el-button 
                size="small" 
                :type="variant.is_active ? 'warning' : 'success'"
                @click="toggleVariant(variant)"
              >
                {{ variant.is_active ? '停用' : '启用' }}
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 流量分配 -->
        <el-tab-pane label="流量分配" name="traffic">
          <el-form label-width="100px">
            <div v-for="(allocation, version) in currentTraffic" :key="version" class="traffic-row">
              <span class="version-label">版本 {{ version }}:</span>
              <el-slider 
                v-model="currentTraffic[version]" 
                :min="0" 
                :max="1" 
                :step="0.05"
                style="flex: 1;"
              />
              <span class="allocation-value">{{ (allocation * 100).toFixed(0) }}%</span>
            </div>
            <el-button type="primary" @click="updateTraffic" :disabled="trafficTotal !== 1">
              更新分配
            </el-button>
          </el-form>
        </el-tab-pane>

        <!-- 效果对比 -->
        <el-tab-pane label="效果对比" name="comparison">
          <ABTestChart :comparison="comparisonData" />
          
          <el-table :data="comparisonTableData" style="margin-top: 20px;">
            <el-table-column prop="version" label="版本" width="100" />
            <el-table-column prop="impressions" label="曝光" width="100" />
            <el-table-column prop="click_rate" label="点击率" width="100">
              <template #default="{ row }">
                {{ (row.click_rate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="conversion_rate" label="转化率" width="100">
              <template #default="{ row }">
                {{ (row.conversion_rate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="interaction_rate" label="互动率" width="100">
              <template #default="{ row }">
                {{ (row.interaction_rate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="avg_watch_time" label="平均观看时长" width="120">
              <template #default="{ row }">
                {{ row.avg_watch_time.toFixed(1) }}s
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 统计检验 -->
        <el-tab-pane label="统计检验" name="significance">
          <el-card class="significance-card">
            <div class="significance-result">
              <div class="result-item">
                <span class="label">P 值:</span>
                <span class="value" :class="{ 'significant': significanceData.p_value < 0.05 }">
                  {{ significanceData.p_value.toFixed(4) }}
                </span>
              </div>
              <div class="result-item">
                <span class="label">置信度:</span>
                <span class="value">{{ (significanceData.confidence_level * 100).toFixed(2) }}%</span>
              </div>
              <div class="result-item">
                <span class="label">统计显著:</span>
                <el-tag :type="significanceData.is_significant ? 'success' : 'warning'">
                  {{ significanceData.is_significant ? '是' : '否' }}
                </el-tag>
              </div>
              <div class="result-item" v-if="significanceData.winner">
                <span class="label">优胜版本:</span>
                <el-tag type="success">{{ significanceData.winner }}</el-tag>
              </div>
              <div class="result-item" v-if="significanceData.improvement">
                <span class="label">相对提升:</span>
                <span class="value improvement">
                  {{ (significanceData.improvement * 100).toFixed(2) }}%
                </span>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 推荐结果 -->
        <el-tab-pane label="推荐结果" name="recommendation">
          <el-alert
            :title="recommendationData.message || getRecommendationTitle()"
            :type="getRecommendationType()"
            show-icon
            :closable="false"
          />
          <div v-if="recommendationData.recommendation === 'winner'" class="winner-content">
            <h3>🏆 优胜话术</h3>
            <el-card>
              <div class="winner-version">版本 {{ recommendationData.winning_version }}</div>
              <div class="winner-improvement">相对提升：{{ recommendationData.improvement }}</div>
              <div class="winner-confidence">置信度：{{ recommendationData.confidence }}</div>
              <div class="winner-talk">
                <h4>话术内容:</h4>
                <blockquote>{{ recommendationData.content }}</blockquote>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 测试报告 -->
        <el-tab-pane label="测试报告" name="report">
          <el-button @click="loadReport" type="primary">刷新报告</el-button>
          <div v-if="reportData" class="report-content">
            <h2>{{ reportData.test_name }}</h2>
            <p><strong>测试 ID:</strong> {{ reportData.test_id }}</p>
            <p><strong>状态:</strong> {{ reportData.status }}</p>
            <p><strong>时间:</strong> {{ reportData.duration.start }} - {{ reportData.duration.end || '进行中' }}</p>
            
            <h3>流量分配</h3>
            <ul>
              <li v-for="(allocation, version) in reportData.traffic_allocation" :key="version">
                版本 {{ version }}: {{ (allocation * 100).toFixed(0) }}%
              </li>
            </ul>

            <h3>统计检验结果</h3>
            <p>P 值：{{ reportData.statistical_test.p_value.toFixed(4) }}</p>
            <p>置信度：{{ (reportData.statistical_test.confidence_level * 100).toFixed(2) }}%</p>
            <p>显著：{{ reportData.statistical_test.is_significant ? '是' : '否' }}</p>
            <p v-if="reportData.statistical_test.winner">优胜版本：{{ reportData.statistical_test.winner }}</p>
            <p v-if="reportData.statistical_test.improvement">相对提升：{{ reportData.statistical_test.improvement }}</p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 导出报告对话框 -->
    <el-dialog v-model="showExportDialog" title="导出测试报告" width="500px">
      <el-form label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportFormat">
            <el-radio label="json">JSON</el-radio>
            <el-radio label="markdown">Markdown</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="downloadReport">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ABTestChart from '../components/ABTestChart.vue'

// API 基础 URL
const API_BASE = '/api/abtest'

// 状态
const loading = ref(false)
const tests = ref([])
const showCreateDialog = ref(false)
const showManageDialogVisible = ref(false)
const showExportDialog = ref(false)
const currentTestId = ref('')
const activeTab = ref('variants')
const exportFormat = ref('json')

// 创建表单
const createForm = ref({
  name: '',
  variants: [
    { version: 'A', content: '', allocation: 0.5 },
    { version: 'B', content: '', allocation: 0.5 }
  ]
})

// 当前测试数据
const currentVariants = ref([])
const currentTraffic = ref({})
const comparisonData = ref({})
const comparisonTableData = ref([])
const significanceData = ref({
  is_significant: false,
  p_value: 1,
  confidence_level: 0,
  winner: null,
  improvement: 0
})
const recommendationData = ref({})
const reportData = ref(null)

// 计算属性
const totalAllocation = computed(() => {
  return createForm.value.variants.reduce((sum, v) => sum + v.allocation, 0)
})

const trafficTotal = computed(() => {
  return Object.values(currentTraffic.value).reduce((sum, v) => sum + v, 0)
})

// 方法
const loadTests = async () => {
  loading.value = true
  try {
    // 模拟加载测试列表
    tests.value = []
  } catch (error) {
    ElMessage.error('加载测试列表失败')
  } finally {
    loading.value = false
  }
}

const addVariant = () => {
  const versions = ['A', 'B', 'C', 'D', 'E']
  const usedVersions = createForm.value.variants.map(v => v.version)
  const nextVersion = versions.find(v => !usedVersions.includes(v)) || 'Z'
  
  createForm.value.variants.push({
    version: nextVersion,
    content: '',
    allocation: 0
  })
}

const removeVariant = (index) => {
  createForm.value.variants.splice(index, 1)
}

const createTest = async () => {
  if (totalAllocation.value !== 1) {
    ElMessage.warning('流量分配总和必须为 100%')
    return
  }

  try {
    // 创建测试
    const trafficAllocation = {}
    createForm.value.variants.forEach(v => {
      trafficAllocation[v.version] = v.allocation
    })

    // TODO: 实际 API 调用
    // const response = await fetch(`${API_BASE}/tests`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     name: createForm.value.name,
    //     traffic_allocation: trafficAllocation
    //   })
    // })

    // 创建话术变体
    for (const variant of createForm.value.variants) {
      // TODO: 实际 API 调用
      // await fetch(`${API_BASE}/variants`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     test_id: newTestId,
      //     version: variant.version,
      //     content: variant.content
      //   })
      // })
    }

    ElMessage.success('测试创建成功')
    showCreateDialog.value = false
    loadTests()
    
    // 重置表单
    createForm.value = {
      name: '',
      variants: [
        { version: 'A', content: '', allocation: 0.5 },
        { version: 'B', content: '', allocation: 0.5 }
      ]
    }
  } catch (error) {
    ElMessage.error('创建测试失败')
  }
}

const viewTest = (testId) => {
  currentTestId.value = testId
  showManageDialogVisible.value = true
  loadTestDetails(testId)
}

const showManageDialog = (testId) => {
  currentTestId.value = testId
  showManageDialogVisible.value = true
  activeTab.value = 'variants'
  loadTestDetails(testId)
}

const loadTestDetails = async (testId) => {
  try {
    await Promise.all([
      loadVariants(testId),
      loadTraffic(testId),
      loadComparison(testId),
      loadSignificance(testId),
      loadRecommendation(testId)
    ])
  } catch (error) {
    ElMessage.error('加载测试详情失败')
  }
}

const loadVariants = async (testId) => {
  // TODO: 实际 API 调用
  // const response = await fetch(`${API_BASE}/variants/${testId}`)
  // currentVariants.value = await response.json()
  
  // 模拟数据
  currentVariants.value = [
    { id: '1', version: 'A', content: '欢迎来到直播间！今天给大家带来超值优惠...', is_active: true },
    { id: '2', version: 'B', content: '嗨大家好！我是你们的主播，今天有惊喜...', is_active: true }
  ]
}

const loadTraffic = async (testId) => {
  // TODO: 实际 API 调用
  // const response = await fetch(`${API_BASE}/tests/${testId}`)
  // const data = await response.json()
  // currentTraffic.value = data.variants
  
  // 模拟数据
  currentTraffic.value = { A: 0.5, B: 0.5 }
}

const loadComparison = async (testId) => {
  // TODO: 实际 API 调用
  // const response = await fetch(`${API_BASE}/compare/${testId}`)
  // const data = await response.json()
  // comparisonData.value = data.comparison
  
  // 模拟数据
  comparisonData.value = {
    A: {
      metrics: { impressions: 1000, clicks: 150, conversions: 50, interactions: 200 },
      rates: { click_rate: 0.15, conversion_rate: 0.05, interaction_rate: 0.2, avg_watch_time: 120 }
    },
    B: {
      metrics: { impressions: 1000, clicks: 200, conversions: 80, interactions: 250 },
      rates: { click_rate: 0.2, conversion_rate: 0.08, interaction_rate: 0.25, avg_watch_time: 150 }
    }
  }

  comparisonTableData.value = [
    { version: 'A', ...comparisonData.value.A.rates, impressions: 1000 },
    { version: 'B', ...comparisonData.value.B.rates, impressions: 1000 }
  ]
}

const loadSignificance = async (testId) => {
  // TODO: 实际 API 调用
  // const response = await fetch(`${API_BASE}/significance`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ test_id: testId })
  // })
  // significanceData.value = await response.json()
  
  // 模拟数据
  significanceData.value = {
    is_significant: true,
    p_value: 0.0234,
    confidence_level: 0.9766,
    winner: 'B',
    improvement: 0.6
  }
}

const loadRecommendation = async (testId) => {
  // TODO: 实际 API 调用
  // const response = await fetch(`${API_BASE}/recommend/${testId}`)
  // recommendationData.value = await response.json()
  
  // 模拟数据
  recommendationData.value = {
    recommendation: 'winner',
    winning_version: 'B',
    content: '嗨大家好！我是你们的主播，今天有惊喜...',
    improvement: '60.00%',
    confidence: '97.66%'
  }
}

const loadReport = async () => {
  // TODO: 实际 API 调用
  // const response = await fetch(`${API_BASE}/report/${currentTestId.value}`)
  // reportData.value = await response.json()
  
  // 模拟数据
  reportData.value = {
    test_id: currentTestId.value,
    test_name: '开场话术优化测试',
    status: 'active',
    duration: { start: '2024-01-01T10:00:00', end: null },
    traffic_allocation: { A: 0.5, B: 0.5 },
    variants: [
      { version: 'A', content: '欢迎来到直播间！...', is_active: true },
      { version: 'B', content: '嗨大家好！...', is_active: true }
    ],
    comparison: comparisonData.value,
    statistical_test: significanceData.value,
    recommendation: recommendationData.value
  }
}

const editVariant = (variant) => {
  ElMessageBox.prompt('编辑话术内容', '编辑', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputValue: variant.content
  }).then(async ({ value }) => {
    // TODO: 实际 API 调用
    // await fetch(`${API_BASE}/variants/${currentTestId.value}/${variant.version}`, {
    //   method: 'PUT',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ content: value })
    // })
    
    variant.content = value
    ElMessage.success('更新成功')
  }).catch(() => {})
}

const toggleVariant = async (variant) => {
  // TODO: 实际 API 调用
  // await fetch(`${API_BASE}/variants/${currentTestId.value}/${variant.version}`, {
  //   method: 'DELETE'
  // })
  
  variant.is_active = !variant.is_active
  ElMessage.success(variant.is_active ? '已启用' : '已停用')
}

const updateTraffic = async () => {
  if (trafficTotal.value !== 1) {
    ElMessage.warning('流量分配总和必须为 100%')
    return
  }

  try {
    // TODO: 实际 API 调用
    // await fetch(`${API_BASE}/tests/${currentTestId.value}/traffic`, {
    //   method: 'PUT',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ traffic_allocation: currentTraffic.value })
    // })
    
    ElMessage.success('流量分配已更新')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const stopTest = async (testId) => {
  try {
    await ElMessageBox.confirm('确定要停止此测试吗？', '确认', {
      type: 'warning'
    })

    // TODO: 实际 API 调用
    // await fetch(`${API_BASE}/tests/${testId}/stop`, { method: 'POST' })
    
    ElMessage.success('测试已停止')
    loadTests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止测试失败')
    }
  }
}

const exportReport = (testId) => {
  currentTestId.value = testId
  showExportDialog.value = true
}

const downloadReport = async () => {
  try {
    // TODO: 实际 API 调用
    // const response = await fetch(`${API_BASE}/report/${currentTestId.value}/export?format=${exportFormat.value}`)
    // const data = await response.json()
    // downloadFile(data.content, `abtest-report-${currentTestId.value}.${exportFormat.value}`)
    
    ElMessage.success('报告已导出')
    showExportDialog.value = false
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const getRecommendationTitle = () => {
  if (recommendationData.value.recommendation === 'winner') {
    return '🎉 已找到优胜话术！'
  } else {
    return recommendationData.value.message || '暂无推荐'
  }
}

const getRecommendationType = () => {
  if (recommendationData.value.recommendation === 'winner') {
    return 'success'
  } else {
    return 'warning'
  }
}

// 生命周期
onMounted(() => {
  loadTests()
})
</script>

<style scoped>
.ab-testing-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-test-card {
  margin-bottom: 20px;
}

.variant-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.warning-text {
  color: #f56c6c;
  font-size: 12px;
}

.variant-card {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.variant-header {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.variant-content {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.6;
}

.variant-actions {
  display: flex;
  gap: 10px;
}

.traffic-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.version-label {
  width: 80px;
  font-weight: bold;
}

.allocation-value {
  width: 60px;
  text-align: right;
  font-weight: bold;
}

.significance-card {
  margin-top: 20px;
}

.significance-result {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  color: #909399;
}

.value {
  font-weight: bold;
  font-size: 18px;
}

.value.significant {
  color: #67c23a;
}

.value.improvement {
  color: #e6a23c;
}

.winner-content {
  margin-top: 20px;
}

.winner-version {
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
  margin-bottom: 10px;
}

.winner-improvement,
.winner-confidence {
  font-size: 16px;
  color: #606266;
  margin-bottom: 5px;
}

.winner-talk {
  margin-top: 20px;
}

.winner-talk blockquote {
  background: #f5f7fa;
  padding: 15px;
  border-left: 4px solid #67c23a;
  margin: 10px 0;
  font-style: italic;
}

.report-content {
  margin-top: 20px;
  line-height: 1.8;
}

.report-content h2,
.report-content h3 {
  color: #303133;
}

.traffic-allocation {
  display: flex;
  gap: 10px;
}

.allocation-tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
</style>
