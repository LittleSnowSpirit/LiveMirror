<template>
  <div class="ad-creative-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 广告素材分析</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传素材
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 数据概览卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-label">总素材数</div>
            <div class="stat-value">{{ dashboard.total_creatives }}</div>
            <div class="stat-sub">活跃：{{ dashboard.active_creatives }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-label">总展示量</div>
            <div class="stat-value">{{ formatNumber(dashboard.total_impressions) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-label">平均点击率</div>
            <div class="stat-value">{{ (dashboard.average_ctr * 100).toFixed(2) }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-label">平均 ROAS</div>
            <div class="stat-value">{{ dashboard.average_roas.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-card>
        <el-form :inline="true">
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="全部状态" clearable>
              <el-option label="草稿" value="draft" />
              <el-option label="投放中" value="active" />
              <el-option label="已暂停" value="paused" />
              <el-option label="已归档" value="archived" />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="filters.creative_type" placeholder="全部类型" clearable>
              <el-option label="图片" value="image" />
              <el-option label="视频" value="video" />
              <el-option label="轮播" value="carousel" />
            </el-select>
          </el-form-item>
          <el-form-item label="排序">
            <el-select v-model="filters.sort" placeholder="按评分">
              <el-option label="评分从高到低" value="score_desc" />
              <el-option label="评分从低到高" value="score_asc" />
              <el-option label="最新创建" value="created_desc" />
              <el-option label="展示量从高到低" value="impressions_desc" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="filters.search"
              placeholder="搜索素材名称..."
              clearable
              @clear="loadCreatives"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadCreatives">筛选</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 素材列表 -->
    <div class="creative-list">
      <el-row :gutter="20">
        <el-col
          v-for="creative in creatives"
          :key="creative.id"
          :span="8"
          class="creative-col"
        >
          <CreativeCard
            :creative="creative"
            @analyze="showAnalysis"
            @abtest="createABTest"
            @status-change="updateStatus"
            @delete="deleteCreative"
          />
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty v-if="creatives.length === 0" description="暂无素材，点击上方按钮上传">
        <el-button type="primary" @click="showUploadDialog = true">上传素材</el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="creatives.length > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @change="loadCreatives"
      />
    </div>

    <!-- 素材上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传广告素材"
      width="600px"
      @close="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="素材名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="输入素材名称" />
        </el-form-item>
        <el-form-item label="素材类型" prop="creative_type">
          <el-select v-model="uploadForm.creative_type" placeholder="选择类型">
            <el-option label="图片" value="image" />
            <el-option label="视频" value="video" />
            <el-option label="轮播" value="carousel" />
          </el-select>
        </el-form-item>
        <el-form-item label="素材文件" prop="file">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="uploadForm.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="submitUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 素材分析对话框 -->
    <el-dialog
      v-model="showAnalysisDialog"
      title="素材效果分析"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedCreative" class="analysis-content">
        <!-- 基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="素材名称">
            {{ selectedCreative.name }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ getTypeLabel(selectedCreative.creative_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="综合评分">
            <el-tag :type="getScoreType(selectedCreative.score)" size="large">
              {{ selectedCreative.score }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="表现等级">
            {{ getPerformanceLabel(selectedCreative.score) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 效果指标 -->
        <h3 class="section-title">📈 效果指标</h3>
        <el-row :gutter="20" class="metrics-grid">
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-label">展示量</div>
              <div class="metric-value">{{ formatNumber(selectedCreative.metrics.impressions) }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-label">点击量</div>
              <div class="metric-value">{{ formatNumber(selectedCreative.metrics.clicks) }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-label">转化量</div>
              <div class="metric-value">{{ formatNumber(selectedCreative.metrics.conversions) }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-label">点击率 (CTR)</div>
              <div class="metric-value">{{ (selectedCreative.metrics.ctr * 100).toFixed(2) }}%</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-label">转化率 (CVR)</div>
              <div class="metric-value">{{ (selectedCreative.metrics.cvr * 100).toFixed(2) }}%</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-label">ROAS</div>
              <div class="metric-value">{{ selectedCreative.metrics.roas.toFixed(2) }}</div>
            </div>
          </el-col>
        </el-row>

        <!-- 优势分析 -->
        <h3 class="section-title">✅ 优势</h3>
        <el-alert
          v-for="(strength, index) in currentAnalysis?.strengths"
          :key="index"
          :title="strength"
          type="success"
          :closable="false"
          show-icon
          class="mb-2"
        />
        <el-empty v-if="!currentAnalysis?.strengths?.length" description="暂无明显优势" :image-size="80" />

        <!-- 劣势分析 -->
        <h3 class="section-title">⚠️ 待优化</h3>
        <el-alert
          v-for="(weakness, index) in currentAnalysis?.weaknesses"
          :key="index"
          :title="weakness"
          type="warning"
          :closable="false"
          show-icon
          class="mb-2"
        />
        <el-empty v-if="!currentAnalysis?.weaknesses?.length" description="表现良好，继续保持" :image-size="80" />

        <!-- 优化建议 -->
        <h3 class="section-title">💡 优化建议</h3>
        <el-collapse v-if="currentAnalysis?.suggestions?.length">
          <el-collapse-item
            v-for="(suggestion, index) in currentAnalysis.suggestions"
            :key="index"
            :title="suggestion.suggestion"
          >
            <el-tag :type="getPriorityType(suggestion.priority)" class="mr-2">
              {{ getPriorityLabel(suggestion.priority) }}
            </el-tag>
            <el-tag>{{ getSuggestionTypeLabel(suggestion.type) }}</el-tag>
            <el-divider />
            <div class="suggestion-actions">
              <div v-for="(action, aIndex) in suggestion.actions" :key="aIndex" class="action-item">
                <el-icon><Check /></el-icon>
                <span>{{ action }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      <template #footer>
        <el-button @click="showAnalysisDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportAnalysis">导出报告</el-button>
      </template>
    </el-dialog>

    <!-- A/B 测试创建对话框 -->
    <el-dialog
      v-model="showABTestDialog"
      title="创建 A/B 测试"
      width="600px"
    >
      <el-form ref="abTestFormRef" :model="abTestForm" label-width="100px">
        <el-form-item label="测试名称">
          <el-input v-model="abTestForm.name" placeholder="输入测试名称" />
        </el-form-item>
        <el-form-item label="参与素材">
          <el-select
            v-model="abTestForm.creative_ids"
            multiple
            placeholder="选择参与测试的素材"
            style="width: 100%"
          >
            <el-option
              v-for="c in creatives"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
          <div class="form-tip">至少选择 2 个素材进行对比测试</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showABTestDialog = false">取消</el-button>
        <el-button type="primary" @click="submitABTest" :disabled="abTestForm.creative_ids.length < 2">
          创建测试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, Search, UploadFilled, Check } from '@element-plus/icons-vue'
import CreativeCard from '../components/CreativeCard.vue'
import axios from 'axios'

// API 基础 URL
const API_BASE = '/api/creative'

// 响应式数据
const dashboard = ref({
  total_creatives: 0,
  active_creatives: 0,
  total_impressions: 0,
  total_clicks: 0,
  total_conversions: 0,
  total_spend: 0,
  total_revenue: 0,
  average_ctr: 0,
  average_cvr: 0,
  average_roas: 0,
  top_performer: null
})

const creatives = ref([])
const filters = reactive({
  status: '',
  creative_type: '',
  sort: 'score_desc',
  search: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框状态
const showUploadDialog = ref(false)
const showAnalysisDialog = ref(false)
const showABTestDialog = ref(false)

// 上传相关
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const uploading = ref(false)
const uploadForm = reactive({
  name: '',
  creative_type: '',
  file: null,
  tags: []
})

const uploadRules = {
  name: [{ required: true, message: '请输入素材名称', trigger: 'blur' }],
  creative_type: [{ required: true, message: '请选择素材类型', trigger: 'change' }],
  file: [{ required: true, message: '请上传素材文件', trigger: 'change' }]
}

// 分析相关
const selectedCreative = ref(null)
const currentAnalysis = ref(null)

// A/B 测试相关
const abTestFormRef = ref(null)
const abTestForm = reactive({
  name: '',
  creative_ids: []
})

// 生命周期
onMounted(() => {
  loadDashboard()
  loadCreatives()
})

// 方法
async function loadDashboard() {
  try {
    const res = await axios.get(`${API_BASE}/dashboard/summary`)
    if (res.data.success) {
      dashboard.value = res.data.summary
    }
  } catch (error) {
    console.error('加载仪表板失败:', error)
  }
}

async function loadCreatives() {
  try {
    const params = {
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize
    }
    
    if (filters.status) params.status = filters.status
    if (filters.creative_type) params.creative_type = filters.creative_type
    
    const res = await axios.get(`${API_BASE}/list`, { params })
    
    if (res.data.success) {
      creatives.value = res.data.creatives
      pagination.total = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载素材列表失败')
    console.error(error)
  }
}

function refreshData() {
  loadDashboard()
  loadCreatives()
  ElMessage.success('数据已刷新')
}

function handleFileChange(file) {
  uploadForm.file = file.raw
}

async function submitUpload() {
  if (!uploadFormRef.value) return
  
  await uploadFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    if (!uploadForm.file) {
      ElMessage.warning('请选择要上传的文件')
      return
    }
    
    uploading.value = true
    
    try {
      const formData = new FormData()
      formData.append('name', uploadForm.name)
      formData.append('creative_type', uploadForm.creative_type)
      formData.append('file', uploadForm.file)
      formData.append('tags', JSON.stringify(uploadForm.tags))
      
      const res = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (res.data.success) {
        ElMessage.success('素材上传成功')
        showUploadDialog.value = false
        loadCreatives()
        loadDashboard()
      }
    } catch (error) {
      ElMessage.error('上传失败：' + (error.response?.data?.detail || error.message))
    } finally {
      uploading.value = false
    }
  })
}

function resetUploadForm() {
  uploadForm.name = ''
  uploadForm.creative_type = ''
  uploadForm.file = null
  uploadForm.tags = []
  if (uploadRef.value) uploadRef.value.clearFiles()
}

async function showAnalysis(creative) {
  selectedCreative.value = creative
  
  try {
    const res = await axios.get(`${API_BASE}/${creative.id}/analyze`)
    if (res.data.success) {
      currentAnalysis.value = res.data.analysis
      showAnalysisDialog.value = true
    }
  } catch (error) {
    ElMessage.error('加载分析失败')
  }
}

async function updateStatus(creative, newStatus) {
  try {
    const formData = new FormData()
    formData.append('status', newStatus)
    
    const res = await axios.put(`${API_BASE}/${creative.id}/status`, formData)
    
    if (res.data.success) {
      ElMessage.success('状态更新成功')
      creative.status = newStatus
      loadDashboard()
    }
  } catch (error) {
    ElMessage.error('更新状态失败')
  }
}

async function deleteCreative(creative) {
  try {
    await ElMessageBox.confirm(`确定要删除素材 "${creative.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    
    const res = await axios.delete(`${API_BASE}/${creative.id}`)
    
    if (res.data.success) {
      ElMessage.success('素材已删除')
      loadCreatives()
      loadDashboard()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function createABTest(creative) {
  abTestForm.creative_ids = [creative.id]
  showABTestDialog.value = true
}

async function submitABTest() {
  try {
    const res = await axios.post(`${API_BASE}/ab-test`, abTestForm)
    
    if (res.data.success) {
      ElMessage.success('A/B 测试创建成功')
      showABTestDialog.value = false
      abTestForm.name = ''
      abTestForm.creative_ids = []
    }
  } catch (error) {
    ElMessage.error('创建失败：' + (error.response?.data?.detail || error.message))
  }
}

async function exportAnalysis() {
  try {
    const res = await axios.get(`${API_BASE}/export`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([res.data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `素材分析报告_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('报告导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 工具函数
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function getTypeLabel(type) {
  const map = {
    image: '图片',
    video: '视频',
    carousel: '轮播'
  }
  return map[type] || type
}

function getScoreType(score) {
  if (score >= 80) return 'success'
  if (score >= 60) return ''
  if (score >= 40) return 'warning'
  return 'danger'
}

function getPerformanceLabel(score) {
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '需优化'
}

function getPriorityType(priority) {
  const map = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || ''
}

function getPriorityLabel(priority) {
  const map = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return map[priority] || priority
}

function getSuggestionTypeLabel(type) {
  const map = {
    ctr: '点击率优化',
    cvr: '转化率优化',
    roas: 'ROI 优化',
    general: '综合建议'
  }
  return map[type] || type
}
</script>

<style scoped>
.ad-creative-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px 0;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.filter-section {
  margin-bottom: 20px;
}

.creative-list {
  margin-bottom: 20px;
}

.creative-col {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.analysis-content {
  max-height: 600px;
  overflow-y: auto;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 10px;
  color: #303133;
}

.metrics-grid {
  margin-bottom: 20px;
}

.metric-item {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.metric-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.mb-2 {
  margin-bottom: 8px;
}

.mr-2 {
  margin-right: 8px;
}

.suggestion-actions {
  margin-top: 10px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: #606266;
}

.action-item .el-icon {
  color: #67c23a;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
