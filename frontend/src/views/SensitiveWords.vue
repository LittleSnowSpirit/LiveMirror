<template>
  <div class="sensitive-words-page">
    <div class="page-header">
      <h1>🛡️ 敏感词管理</h1>
      <p class="subtitle">实时检测、分级预警、智能替换</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #409EFF;">
              <i class="el-icon-collection"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.library_size }}</div>
              <div class="stat-label">词库总量</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #67C23A;">
              <i class="el-icon-check"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_checks }}</div>
              <div class="stat-label">检测次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #E6A23C;">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_hits }}</div>
              <div class="stat-label">命中次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #F56C6C;">
              <i class="el-icon-trend-chart"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ (stats.hit_rate * 100).toFixed(1) }}%</div>
              <div class="stat-label">命中率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 词库管理 -->
      <el-tab-pane label="词库管理" name="library">
        <div class="toolbar">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索敏感词..."
              prefix-icon="el-icon-search"
              clearable
              @input="handleSearch"
            />
          </div>
          <div class="filters">
            <el-select v-model="filterCategory" placeholder="全部分类" clearable @change="handleFilter">
              <el-option label="通用" value="general" />
              <el-option label="美妆" value="beauty" />
              <el-option label="食品" value="food" />
              <el-option label="服装" value="clothing" />
              <el-option label="金融" value="finance" />
              <el-option label="医疗" value="health" />
              <el-option label="广告" value="advertising" />
            </el-select>
            <el-select v-model="filterSeverity" placeholder="全部级别" clearable @change="handleFilter">
              <el-option label="警告" value="warning" />
              <el-option label="严重" value="serious" />
              <el-option label="封禁" value="banned" />
            </el-select>
          </div>
          <div class="actions">
            <el-button type="primary" @click="showAddDialog">
              <i class="el-icon-plus"></i> 添加敏感词
            </el-button>
            <el-button @click="showBatchAddDialog">
              <i class="el-icon-upload"></i> 批量添加
            </el-button>
            <el-button @click="exportLibrary">
              <i class="el-icon-download"></i> 导出
            </el-button>
            <el-button @click="importDialogVisible = true">
              <i class="el-icon-upload2"></i> 导入
            </el-button>
          </div>
        </div>

        <el-table
          :data="wordList"
          v-loading="loading"
          style="width: 100%"
          border
        >
          <el-table-column prop="word" label="敏感词" width="150" />
          <el-table-column label="级别" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">
                {{ getSeverityLabel(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="分类" width="100">
            <template #default="{ row }">
              <el-tag type="info" size="small" effect="plain">
                {{ getCategoryLabel(row.category) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="replacement" label="替换建议" width="120" />
          <el-table-column prop="reason" label="原因" show-overflow-tooltip />
          <el-table-column prop="hit_count" label="命中次数" width="100" sortable />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click="editWord(row)">
                编辑
              </el-button>
              <el-button type="text" size="small" @click="testWord(row.word)">
                测试
              </el-button>
              <el-button type="text" size="small" @click="removeWord(row.word)" style="color: #F56C6C;">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="loadWords"
          style="margin-top: 20px; justify-content: flex-end;"
        />
      </el-tab-pane>

      <!-- 实时检测 -->
      <el-tab-pane label="实时检测" name="detection">
        <div class="detection-panel">
          <el-input
            v-model="detectionText"
            type="textarea"
            :rows="8"
            placeholder="输入或粘贴需要检测的文本..."
            @input="handleDetectionInput"
          />
          <div class="detection-actions">
            <el-button type="primary" @click="detectText">
              <i class="el-icon-search"></i> 检测
            </el-button>
            <el-button @click="detectionText = ''">
              <i class="el-icon-delete"></i> 清空
            </el-button>
            <el-switch v-model="realtimeMode" active-text="实时模式" />
          </div>

          <!-- 检测结果 -->
          <div v-if="detectionResult" class="detection-result">
            <div class="result-header">
              <el-tag :type="getResultType(detectionResult)" size="large">
                {{ detectionResult.has_sensitive ? '发现敏感词' : '检测通过' }}
              </el-tag>
              <span v-if="detectionResult.has_sensitive" class="result-count">
                共发现 {{ detectionResult.hits.length }} 个敏感词
              </span>
            </div>

            <div v-if="detectionResult.hits.length > 0" class="hits-list">
              <div v-for="(hit, index) in detectionResult.hits" :key="index" class="hit-item">
                <el-alert
                  :title="hit.word"
                  :type="getSeverityType(hit.severity)"
                  :closable="false"
                  show-icon
                >
                  <template #default>
                    <div class="hit-details">
                      <div class="hit-context">
                        <span class="context-label">上下文：</span>
                        <span class="context-text">{{ hit.context }}</span>
                      </div>
                      <div class="hit-meta">
                        <span v-if="hit.replacement">
                          <strong>建议替换：</strong>{{ hit.replacement }}
                        </span>
                        <span v-if="hit.reason">
                          <strong>原因：</strong>{{ hit.reason }}
                        </span>
                      </div>
                    </div>
                  </template>
                </el-alert>
              </div>
            </div>

            <div v-if="detectionResult.suggested_text" class="suggested-text">
              <h4>建议文本：</h4>
              <el-input
                :model-value="detectionResult.suggested_text"
                type="textarea"
                :rows="4"
                readonly
              />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 行业词包 -->
      <el-tab-pane label="行业词包" name="packages">
        <div class="packages-panel">
          <el-row :gutter="20">
            <el-col :span="8" v-for="pkg in predefinedPackages" :key="pkg.category">
              <el-card class="package-card">
                <template #header>
                  <div class="package-header">
                    <span class="package-name">{{ pkg.name }}</span>
                    <el-tag :type="pkg.installed ? 'success' : 'info'" size="small">
                      {{ pkg.installed ? '已安装' : '未安装' }}
                    </el-tag>
                  </div>
                </template>
                <div class="package-info">
                  <p>包含 {{ pkg.word_count }} 个敏感词</p>
                  <p class="package-desc">{{ pkg.description }}</p>
                </div>
                <div class="package-actions">
                  <el-button
                    v-if="!pkg.installed"
                    type="primary"
                    size="small"
                    @click="installPackage(pkg.category)"
                  >
                    安装
                  </el-button>
                  <el-button
                    v-else
                    type="danger"
                    size="small"
                    @click="uninstallPackage(pkg.category)"
                  >
                    卸载
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <div class="installed-packages" v-if="installedPackages.length > 0">
            <h3>已安装词包</h3>
            <el-table :data="installedPackages" border>
              <el-table-column prop="category" label="分类" />
              <el-table-column prop="word_count" label="词数" />
              <el-table-column prop="installed_at" label="安装时间">
                <template #default="{ row }">
                  {{ formatDate(row.installed_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="danger" size="small" @click="uninstallPackage(row.category)">
                    卸载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 统计分析 -->
      <el-tab-pane label="统计分析" name="statistics">
        <div class="statistics-panel">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>命中级别分布</template>
                <div class="chart-container">
                  <div v-for="(count, level) in stats.hits_by_level" :key="level" class="stat-bar">
                    <div class="bar-label">{{ getSeverityLabel(level) }}</div>
                    <el-progress
                      :percentage="calculatePercentage(count, stats.total_hits)"
                      :color="getSeverityColor(level)"
                    />
                    <div class="bar-value">{{ count }}</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>命中分类分布</template>
                <div class="chart-container">
                  <div v-for="(count, category) in stats.hits_by_category" :key="category" class="stat-bar">
                    <div class="bar-label">{{ getCategoryLabel(category) }}</div>
                    <el-progress
                      :percentage="calculatePercentage(count, stats.total_hits)"
                      color="#409EFF"
                    />
                    <div class="bar-value">{{ count }}</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card style="margin-top: 20px;">
            <template #header>近 7 天检测趋势</template>
            <div class="daily-stats">
              <el-table :data="dailyStats" border>
                <el-table-column prop="date" label="日期" />
                <el-table-column prop="checks" label="检测次数" />
                <el-table-column prop="hits" label="命中次数" />
                <el-table-column label="命中率">
                  <template #default="{ row }">
                    {{ ((row.hits / Math.max(1, row.checks)) * 100).toFixed(1) }}%
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑敏感词' : '添加敏感词'"
      width="500px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="敏感词">
          <el-input v-model="form.word" :disabled="isEdit" placeholder="输入敏感词" />
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="form.severity" placeholder="请选择">
            <el-option label="⚠️ 警告" value="warning" />
            <el-option label="🔴 严重" value="serious" />
            <el-option label="🚫 封禁" value="banned" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择">
            <el-option label="通用" value="general" />
            <el-option label="美妆" value="beauty" />
            <el-option label="食品" value="food" />
            <el-option label="服装" value="clothing" />
            <el-option label="金融" value="finance" />
            <el-option label="医疗" value="health" />
            <el-option label="广告" value="advertising" />
          </el-select>
        </el-form-item>
        <el-form-item label="替换建议">
          <el-input v-model="form.replacement" placeholder="可选，建议替换的词语" />
        </el-form-item>
        <el-form-item label="添加原因">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="3"
            placeholder="说明添加原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWord">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量添加对话框 -->
    <el-dialog v-model="batchDialogVisible" title="批量添加敏感词" width="600px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="敏感词列表">
          <el-input
            v-model="batchForm.words"
            type="textarea"
            :rows="8"
            placeholder="每行一个敏感词"
          />
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="batchForm.severity" placeholder="请选择">
            <el-option label="⚠️ 警告" value="warning" />
            <el-option label="🔴 严重" value="serious" />
            <el-option label="🚫 封禁" value="banned" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="batchForm.category" placeholder="请选择">
            <el-option label="通用" value="general" />
            <el-option label="美妆" value="beauty" />
            <el-option label="食品" value="food" />
            <el-option label="服装" value="clothing" />
            <el-option label="金融" value="finance" />
            <el-option label="医疗" value="health" />
            <el-option label="广告" value="advertising" />
          </el-select>
        </el-form-item>
        <el-form-item label="替换建议">
          <el-input v-model="batchForm.replacement" placeholder="可选" />
        </el-form-item>
        <el-form-item label="添加原因">
          <el-input
            v-model="batchForm.reason"
            type="textarea"
            :rows="2"
            placeholder="说明添加原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="batchAddWords">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入词库" width="500px">
      <el-upload
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".json"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">
          拖拽文件到此处，或<em>点击上传</em>
        </div>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// API 基础地址
const API_BASE = '/api/sensitive'

// 状态
const activeTab = ref('library')
const loading = ref(false)
const wordList = ref([])
const stats = reactive({
  library_size: 0,
  total_checks: 0,
  total_hits: 0,
  hit_rate: 0,
  hits_by_level: {},
  hits_by_category: {},
  daily_stats: {}
})

// 筛选和分页
const searchKeyword = ref('')
const filterCategory = ref('')
const filterSeverity = ref('')
const pagination = reactive({
  page: 1,
  page_size: 50,
  total: 0
})

// 检测
const detectionText = ref('')
const detectionResult = ref(null)
const realtimeMode = ref(false)
let detectionTimer = null

// 对话框
const dialogVisible = ref(false)
const batchDialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEdit = ref(false)
const form = reactive({
  word: '',
  severity: 'warning',
  category: 'general',
  replacement: '',
  reason: ''
})
const batchForm = reactive({
  words: '',
  severity: 'warning',
  category: 'general',
  replacement: '',
  reason: ''
})

// 行业词包
const predefinedPackages = ref([
  { category: 'beauty', name: '美妆行业', word_count: 5, description: '化妆品禁用词、医疗术语等', installed: false },
  { category: 'food', name: '食品行业', word_count: 6, description: '食品功效宣称禁用词', installed: false },
  { category: 'clothing', name: '服装行业', word_count: 4, description: '材质、功能宣称敏感词', installed: false }
])
const installedPackages = ref([])

// 导入文件
let importFile = null

// 计算属性
const dailyStats = computed(() => {
  const result = []
  for (const [date, data] of Object.entries(stats.daily_stats || {})) {
    result.push({
      date,
      checks: data.checks || 0,
      hits: data.hits || 0
    })
  }
  return result.reverse()
})

// 生命周期
onMounted(() => {
  loadWords()
  loadStatistics()
  loadIndustryPackages()
})

// 方法
async function loadWords() {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.page,
      page_size: pagination.page_size
    })
    if (filterCategory.value) params.append('category', filterCategory.value)
    if (filterSeverity.value) params.append('severity', filterSeverity.value)
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)

    const res = await fetch(`${API_BASE}/words?${params}`)
    const data = await res.json()
    
    if (data.success) {
      wordList.value = data.data.words
      pagination.total = data.data.pagination.total
    }
  } catch (error) {
    ElMessage.error('加载词库失败：' + error.message)
  } finally {
    loading.value = false
  }
}

async function loadStatistics() {
  try {
    const res = await fetch(`${API_BASE}/statistics`)
    const data = await res.json()
    
    if (data.success) {
      Object.assign(stats, data.data)
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

async function loadIndustryPackages() {
  try {
    const res = await fetch(`${API_BASE}/industry-packages`)
    const data = await res.json()
    
    if (data.success) {
      installedPackages.value = data.data
      // 更新预定义包状态
      predefinedPackages.value.forEach(pkg => {
        pkg.installed = data.data.some(p => p.category === pkg.category)
      })
    }
  } catch (error) {
    console.error('加载词包失败:', error)
  }
}

function handleSearch() {
  pagination.page = 1
  loadWords()
}

function handleFilter() {
  pagination.page = 1
  loadWords()
}

function showAddDialog() {
  isEdit.value = false
  Object.assign(form, {
    word: '',
    severity: 'warning',
    category: 'general',
    replacement: '',
    reason: ''
  })
  dialogVisible.value = true
}

function editWord(row) {
  isEdit.value = true
  Object.assign(form, {
    word: row.word,
    severity: row.severity,
    category: row.category,
    replacement: row.replacement || '',
    reason: row.reason || ''
  })
  dialogVisible.value = true
}

async function saveWord() {
  try {
    const url = isEdit.value ? `${API_BASE}/words/${form.word}` : `${API_BASE}/words`
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    const data = await res.json()
    
    if (data.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      loadWords()
      loadStatistics()
    } else {
      ElMessage.error(data.detail || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  }
}

async function removeWord(word) {
  try {
    await ElMessageBox.confirm(`确定删除敏感词 "${word}" 吗？`, '确认删除', {
      type: 'warning'
    })
    
    const res = await fetch(`${API_BASE}/words/${encodeURIComponent(word)}`, {
      method: 'DELETE'
    })
    
    const data = await res.json()
    
    if (data.success) {
      ElMessage.success('删除成功')
      loadWords()
      loadStatistics()
    } else {
      ElMessage.error(data.detail || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

function showBatchAddDialog() {
  Object.assign(batchForm, {
    words: '',
    severity: 'warning',
    category: 'general',
    replacement: '',
    reason: ''
  })
  batchDialogVisible.value = true
}

async function batchAddWords() {
  const words = batchForm.words.split('\n').filter(w => w.trim())
  
  if (words.length === 0) {
    ElMessage.warning('请输入至少一个敏感词')
    return
  }
  
  try {
    const res = await fetch(`${API_BASE}/words/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        words,
        severity: batchForm.severity,
        category: batchForm.category,
        replacement: batchForm.replacement,
        reason: batchForm.reason
      })
    })
    
    const data = await res.json()
    
    if (data.success) {
      ElMessage.success(data.message)
      batchDialogVisible.value = false
      loadWords()
      loadStatistics()
    } else {
      ElMessage.error(data.detail || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  }
}

async function testWord(word) {
  const testText = `这是一个测试文本，包含${word}这个词。`
  detectionText.value = testText
  activeTab.value = 'detection'
  await detectText()
}

async function detectText() {
  if (!detectionText.value.trim()) {
    ElMessage.warning('请输入待检测文本')
    return
  }
  
  try {
    const res = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: detectionText.value,
        realtime: realtimeMode.value
      })
    })
    
    const data = await res.json()
    
    if (data.success) {
      detectionResult.value = data.data
    }
  } catch (error) {
    ElMessage.error('检测失败：' + error.message)
  }
}

function handleDetectionInput() {
  if (realtimeMode.value) {
    clearTimeout(detectionTimer)
    detectionTimer = setTimeout(() => {
      detectText()
    }, 500)
  }
}

async function installPackage(category) {
  try {
    const res = await fetch(`${API_BASE}/industry-packages/predefined/${category}`, {
      method: 'POST'
    })
    
    const data = await res.json()
    
    if (data.success) {
      ElMessage.success(data.message)
      loadIndustryPackages()
      loadWords()
    } else {
      ElMessage.error(data.detail || '安装失败')
    }
  } catch (error) {
    ElMessage.error('安装失败：' + error.message)
  }
}

async function uninstallPackage(category) {
  try {
    await ElMessageBox.confirm(`确定卸载行业词包 "${category}" 吗？`, '确认卸载', {
      type: 'warning'
    })
    
    const res = await fetch(`${API_BASE}/industry-packages/${category}`, {
      method: 'DELETE'
    })
    
    const data = await res.json()
    
    if (data.success) {
      ElMessage.success(data.message)
      loadIndustryPackages()
      loadWords()
    } else {
      ElMessage.error(data.detail || '卸载失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('卸载失败：' + error.message)
    }
  }
}

async function exportLibrary() {
  try {
    const res = await fetch(`${API_BASE}/export`)
    const data = await res.json()
    
    if (data.success) {
      const blob = new Blob([JSON.stringify(data.data.library, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `sensitive_words_${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

function handleFileChange(file) {
  importFile = file.raw
}

async function confirmImport() {
  if (!importFile) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  try {
    const text = await importFile.text()
    const library = JSON.parse(text)
    
    const res = await fetch(`${API_BASE}/import?merge=true`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(library)
    })
    
    const data = await res.json()
    
    if (data.success) {
      ElMessage.success(data.message)
      importDialogVisible.value = false
      loadWords()
      loadStatistics()
    } else {
      ElMessage.error(data.detail || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败：' + error.message)
  }
}

// 工具函数
function getSeverityType(severity) {
  const types = {
    warning: 'warning',
    serious: 'danger',
    banned: 'danger'
  }
  return types[severity] || 'info'
}

function getSeverityLabel(severity) {
  const labels = {
    warning: '警告',
    serious: '严重',
    banned: '封禁'
  }
  return labels[severity] || severity
}

function getSeverityColor(severity) {
  const colors = {
    warning: '#E6A23C',
    serious: '#F56C6C',
    banned: '#F56C6C'
  }
  return colors[severity] || '#409EFF'
}

function getCategoryLabel(category) {
  const labels = {
    general: '通用',
    beauty: '美妆',
    food: '食品',
    clothing: '服装',
    finance: '金融',
    health: '医疗',
    advertising: '广告'
  }
  return labels[category] || category
}

function getResultType(result) {
  if (!result.has_sensitive) return 'success'
  if (result.max_severity === 'banned') return 'danger'
  if (result.max_severity === 'serious') return 'warning'
  return 'info'
}

function calculatePercentage(value, total) {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.sensitive-words-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.stats-overview {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: white;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.main-tabs {
  background: white;
  padding: 20px;
  border-radius: 4px;
}

.toolbar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.filters {
  display: flex;
  gap: 10px;
}

.actions {
  display: flex;
  gap: 10px;
}

.detection-panel {
  max-width: 900px;
}

.detection-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.detection-result {
  margin-top: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.result-count {
  color: #909399;
  font-size: 14px;
}

.hits-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.hit-details {
  padding: 5px 0;
}

.hit-context {
  margin-bottom: 8px;
}

.context-label {
  font-weight: bold;
  color: #606266;
}

.context-text {
  color: #909399;
  font-family: monospace;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.hit-meta {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #606266;
}

.suggested-text {
  margin-top: 20px;
}

.suggested-text h4 {
  margin: 0 0 10px 0;
  color: #606266;
}

.packages-panel {
  max-width: 1000px;
}

.package-card {
  margin-bottom: 20px;
}

.package-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.package-name {
  font-weight: bold;
  font-size: 16px;
}

.package-info {
  color: #606266;
  font-size: 14px;
}

.package-desc {
  color: #909399;
  font-size: 13px;
  margin-top: 5px;
}

.package-actions {
  margin-top: 15px;
}

.installed-packages {
  margin-top: 30px;
}

.installed-packages h3 {
  margin-bottom: 15px;
  color: #303133;
}

.statistics-panel {
  max-width: 1200px;
}

.chart-container {
  padding: 10px 0;
}

.stat-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.bar-label {
  width: 80px;
  font-size: 14px;
  color: #606266;
}

.bar-value {
  width: 60px;
  text-align: right;
  font-size: 14px;
  color: #303133;
  font-weight: bold;
}

.daily-stats {
  margin-top: 10px;
}
</style>
