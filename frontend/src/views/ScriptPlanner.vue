<template>
  <div class="script-planner-page">
    <div class="page-header">
      <h1>📝 直播剧本生成</h1>
      <p class="subtitle">AI 生成完整直播剧本，包含分时段规划、产品上下架、互动环节、应急预案</p>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #409EFF;">
              <i class="el-icon-document"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_scripts }}</div>
              <div class="stat-label">已生成剧本</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #67C23A;">
              <i class="el-icon-time"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_templates }}</div>
              <div class="stat-label">模板数量</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #E6A23C;">
              <i class="el-icon-shopping-bag"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_products }}</div>
              <div class="stat-label">产品库</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #F56C6C;">
              <i class="el-icon-download"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ getTotalSegments() }}</div>
              <div class="stat-label">总片段数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 剧本生成 -->
      <el-tab-pane label="剧本生成" name="generate">
        <div class="generate-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>🚀 快速生成</span>
              </div>
            </template>
            
            <el-form :model="generateForm" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="直播主题">
                    <el-input 
                      v-model="generateForm.theme" 
                      placeholder="例如：双 11 美妆专场、家居好物推荐"
                      maxlength="50"
                      show-word-limit
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="直播时长">
                    <el-select v-model="generateForm.duration" style="width: 100%;">
                      <el-option label="1 小时（快闪直播）" value="1h" />
                      <el-option label="2 小时（标准直播）" value="2h" />
                      <el-option label="3 小时（深度直播）" value="3h" />
                      <el-option label="4 小时（马拉松直播）" value="4h" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="目标观众">
                    <el-input 
                      v-model="generateForm.target_audience" 
                      placeholder="例如：上班族、学生党、美妆爱好者"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="主播名称">
                    <el-input 
                      v-model="generateForm.streamer_name" 
                      placeholder="主播昵称"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="选择模板">
                    <el-select 
                      v-model="generateForm.template_id" 
                      placeholder="使用默认模板" 
                      clearable 
                      style="width: 100%;"
                    >
                      <el-option
                        v-for="tpl in templates"
                        :key="tpl.template_id"
                        :label="tpl.name"
                        :value="tpl.template_id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="选择产品">
                    <el-select 
                      v-model="generateForm.selected_products" 
                      placeholder="使用全部产品" 
                      multiple
                      collapse-tags
                      style="width: 100%;"
                    >
                      <el-option
                        v-for="prod in products"
                        :key="prod.product_id"
                        :label="prod.name"
                        :value="prod.product_id"
                      >
                        <span>{{ prod.name }}</span>
                        <span style="float: right; color: #8492a6; font-size: 13px">
                          ¥{{ prod.price }}
                        </span>
                      </el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-form-item>
                <el-button type="primary" size="large" @click="generateScript" :loading="generating">
                  <i class="el-icon-magic-stick"></i> 生成剧本
                </el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 生成结果预览 -->
          <el-card v-if="currentScript" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>✅ 生成成功</span>
                <div class="header-actions">
                  <el-button size="small" @click="exportScript('json')">导出 JSON</el-button>
                  <el-button size="small" @click="exportScript('txt')">导出 TXT</el-button>
                  <el-button size="small" @click="exportScript('pdf')">导出 PDF</el-button>
                  <el-button size="small" type="danger" @click="deleteCurrentScript">删除</el-button>
                </div>
              </div>
            </template>
            
            <div class="script-preview">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="剧本 ID">{{ currentScript.script_id }}</el-descriptions-item>
                <el-descriptions-item label="主题">{{ currentScript.theme }}</el-descriptions-item>
                <el-descriptions-item label="时长">{{ getDurationLabel(currentScript.duration) }}</el-descriptions-item>
                <el-descriptions-item label="生成时间">{{ formatDate(currentScript.generated_at) }}</el-descriptions-item>
                <el-descriptions-item label="片段数">{{ currentScript.segments_count }}</el-descriptions-item>
                <el-descriptions-item label="产品数">{{ currentScript.products_count }}</el-descriptions-item>
              </el-descriptions>
              
              <el-divider>整体流程</el-divider>
              <div class="flow-content">{{ currentScript.overall_flow }}</div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 时间轴视图 -->
      <el-tab-pane label="时间轴" name="timeline">
        <ScriptTimeline 
          v-if="currentScriptDetail" 
          :script="currentScriptDetail" 
        />
        <el-empty v-else description="请先生成或选择一个剧本" />
      </el-tab-pane>

      <!-- 剧本列表 -->
      <el-tab-pane label="剧本列表" name="list">
        <div class="toolbar">
          <div class="filters">
            <el-select v-model="listFilter.duration" placeholder="全部时长" clearable @change="loadScripts">
              <el-option label="1 小时" value="1h" />
              <el-option label="2 小时" value="2h" />
              <el-option label="3 小时" value="3h" />
              <el-option label="4 小时" value="4h" />
            </el-select>
          </div>
          <div class="actions">
            <el-button @click="loadScripts">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
          </div>
        </div>

        <el-table :data="scriptList" v-loading="loading" border @row-click="viewScript">
          <el-table-column prop="script_id" label="剧本 ID" width="200" />
          <el-table-column prop="title" label="标题" show-overflow-tooltip />
          <el-table-column label="时长" width="100">
            <template #default="{ row }">
              <el-tag :type="getDurationColor(row.duration)" size="small">
                {{ getDurationLabel(row.duration) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="theme" label="主题" width="200" />
          <el-table-column label="片段数" width="80">
            <template #default="{ row }">
              {{ row.segments_count }}
            </template>
          </el-table-column>
          <el-table-column label="产品数" width="80">
            <template #default="{ row }">
              {{ row.products_count }}
            </template>
          </el-table-column>
          <el-table-column label="互动数" width="80">
            <template #default="{ row }">
              {{ row.interactions_count }}
            </template>
          </el-table-column>
          <el-table-column prop="generated_at" label="生成时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click.stop="viewScript(row)">
                查看
              </el-button>
              <el-button type="text" size="small" @click.stop="exportScript('txt', row.script_id)">
                导出
              </el-button>
              <el-button 
                type="text" 
                size="small" 
                @click.stop="deleteScript(row.script_id)"
                style="color: #F56C6C;"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @change="loadScripts"
          style="margin-top: 20px; justify-content: flex-end;"
        />
      </el-tab-pane>

      <!-- 产品库管理 -->
      <el-tab-pane label="产品库" name="products">
        <div class="toolbar">
          <div class="actions">
            <el-button type="primary" @click="showAddProductDialog">
              <i class="el-icon-plus"></i> 添加产品
            </el-button>
          </div>
        </div>

        <el-table :data="products" v-loading="loading" border>
          <el-table-column prop="product_id" label="ID" width="120" />
          <el-table-column prop="name" label="产品名称" width="200" />
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column label="价格" width="150">
            <template #default="{ row }">
              <span style="color: #F56C6C; font-weight: bold;">¥{{ row.price }}</span>
              <span style="color: #909399; text-decoration: line-through; margin-left: 5px;">
                ¥{{ row.original_price }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="discount" label="折扣" width="80" />
          <el-table-column prop="target_audience" label="目标人群" show-overflow-tooltip />
          <el-table-column label="卖点" width="200" show-overflow-tooltip>
            <template #default="{ row }">
              {{ (row.selling_points || []).slice(0, 2).join('、') }}
              {{ (row.selling_points || []).length > 2 ? '...' : '' }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 模板信息 -->
      <el-tab-pane label="模板" name="templates">
        <el-table :data="templates" v-loading="loading" border>
          <el-table-column prop="template_id" label="模板 ID" width="150" />
          <el-table-column prop="name" label="模板名称" width="200" />
          <el-table-column label="时长" width="100">
            <template #default="{ row }">
              <el-tag :type="getDurationColor(row.duration)" size="small">
                {{ getDurationLabel(row.duration) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="默认模板" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_default ? 'success' : 'info'" size="small">
                {{ row.is_default ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="结构" show-overflow-tooltip>
            <template #default="{ row }">
              <div v-for="(section, idx) in (row.structure || []).slice(0, 5)" :key="idx" class="template-structure-item">
                <el-tag size="small" type="info">{{ section.title }}</el-tag>
                <span style="margin-left: 5px; color: #909399;">{{ section.duration }}分钟</span>
              </div>
              <div v-if="(row.structure || []).length > 5" style="color: #909399; font-size: 12px;">
                ... 共{{ row.structure.length }}个片段
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加产品对话框 -->
    <el-dialog v-model="addProductVisible" title="添加产品" width="60%">
      <el-form :model="productForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产品名称" required>
              <el-input v-model="productForm.name" placeholder="输入产品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="productForm.category" placeholder="例如：家居用品" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="直播价" required>
              <el-input-number v-model="productForm.price" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="原价" required>
              <el-input-number v-model="productForm.original_price" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="折扣描述">
              <el-input v-model="productForm.discount" placeholder="例如：5 折" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标人群">
              <el-input v-model="productForm.target_audience" placeholder="例如：上班族、学生党" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="推荐话术">
              <el-input v-model="productForm.script_template" placeholder="推荐的产品介绍话术" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="产品卖点">
          <el-input 
            v-model="productForm.selling_points_str" 
            placeholder="多个卖点用逗号分隔"
            type="textarea"
            :rows="3"
          />
          <div class="form-tip">例如：24 小时长效保温，智能测温显示，316 不锈钢内胆</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addProductVisible = false">取消</el-button>
        <el-button type="primary" @click="addProduct">添加</el-button>
      </template>
    </el-dialog>

    <!-- 剧本详情对话框 -->
    <el-dialog v-model="scriptDetailVisible" title="剧本详情" width="90%" top="5vh">
      <div v-if="currentScriptDetail" class="script-detail">
        <el-tabs v-model="detailTab">
          <el-tab-pane label="整体流程" name="flow">
            <div class="flow-content">{{ currentScriptDetail.overall_flow }}</div>
          </el-tab-pane>
          <el-tab-pane label="详细剧本" name="segments">
            <div v-for="seg in currentScriptDetail.segments" :key="seg.segment_id" class="segment-card">
              <div class="segment-header">
                <el-tag :type="getSegmentTypeColor(seg.segment_type)">{{ getSegmentTypeLabel(seg.segment_type) }}</el-tag>
                <span class="segment-time">{{ seg.start_time }} - {{ seg.end_time }}</span>
                <span class="segment-duration">{{ seg.duration_minutes }}分钟</span>
              </div>
              <h4>{{ seg.title }}</h4>
              <p class="segment-description">{{ seg.description }}</p>
              <el-divider />
              <div class="segment-content" v-html="formatScriptContent(seg.script_content)"></div>
              <div v-if="seg.notes && seg.notes.length" class="segment-notes">
                <strong>⚠️ 注意事项：</strong>
                <ul>
                  <li v-for="(note, idx) in seg.notes" :key="idx">{{ note }}</li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="产品上下架" name="products">
            <el-table :data="currentScriptDetail.products || []" border size="small">
              <el-table-column prop="product_name" label="产品名称" width="200" />
              <el-table-column label="价格" width="150">
                <template #default="{ row }">
                  <span style="color: #F56C6C; font-weight: bold;">¥{{ row.price }}</span>
                  <span style="color: #909399; text-decoration: line-through; margin-left: 5px;">
                    ¥{{ row.original_price }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="discount" label="折扣" width="80" />
              <el-table-column prop="start_time" label="上架时间" width="120" />
              <el-table-column prop="end_time" label="下架时间" width="120" />
              <el-table-column label="卖点">
                <template #default="{ row }">
                  {{ (row.selling_points || []).join('、') }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="互动环节" name="interactions">
            <el-table :data="currentScriptDetail.interactions || []" border size="small">
              <el-table-column prop="name" label="互动名称" width="150" />
              <el-table-column prop="start_time" label="开始时间" width="120" />
              <el-table-column prop="duration_minutes" label="时长" width="80">
                <template #default="{ row }">{{ row.duration_minutes }}分钟</template>
              </el-table-column>
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column label="规则" show-overflow-tooltip>
                <template #default="{ row }">
                  <div v-for="(rule, idx) in (row.rules || [])" :key="idx" class="rule-item">
                    {{ idx + 1 }}. {{ rule }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="奖品">
                <template #default="{ row }">
                  <el-tag v-for="(prize, idx) in (row.prizes || [])" :key="idx" size="small" style="margin-right: 5px;">
                    {{ prize }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="应急预案" name="emergency">
            <el-table :data="currentScriptDetail.emergency_plans || []" border size="small">
              <el-table-column prop="scenario" label="突发场景" width="200" show-overflow-tooltip />
              <el-table-column label="概率" width="80">
                <template #default="{ row }">
                  <el-tag :type="getProbabilityColor(row.probability)" size="small">
                    {{ getProbabilityLabel(row.probability) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="影响" width="80">
                <template #default="{ row }">
                  <el-tag :type="getImpactColor(row.impact)" size="small">
                    {{ getImpactLabel(row.impact) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="responsible_person" label="负责人" width="120" />
              <el-table-column label="应对步骤" show-overflow-tooltip>
                <template #default="{ row }">
                  <div v-for="(step, idx) in (row.response_steps || [])" :key="idx">
                    {{ step }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="backup_script" label="备用台词" show-overflow-tooltip />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="准备清单" name="checklist">
            <div class="checklist-content">
              <div v-for="(item, idx) in (currentScriptDetail.preparation_checklist || [])" :key="idx" class="checklist-item">
                <el-checkbox>{{ item }}</el-checkbox>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ScriptTimeline from '../components/ScriptTimeline.vue'

const API_BASE = '/api/planner'

// 状态
const activeTab = ref('generate')
const detailTab = ref('flow')
const loading = ref(false)
const generating = ref(false)
const stats = ref({})
const scriptList = ref([])
const templates = ref([])
const products = ref([])
const currentScript = ref(null)
const currentScriptDetail = ref(null)

// 对话框
const addProductVisible = ref(false)
const scriptDetailVisible = ref(false)

// 表单
const generateForm = reactive({
  theme: '',
  duration: '2h',
  target_audience: '所有人',
  streamer_name: '主播',
  template_id: null,
  selected_products: []
})

const productForm = reactive({
  name: '',
  category: '',
  price: 0,
  original_price: 0,
  discount: '',
  target_audience: '',
  script_template: '',
  selling_points_str: '',
  selling_points: []
})

const listFilter = reactive({
  duration: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 工具函数
const getDurationLabel = (duration) => {
  const map = {
    '1h': '1 小时',
    '2h': '2 小时',
    '3h': '3 小时',
    '4h': '4 小时'
  }
  return map[duration] || duration
}

const getDurationColor = (duration) => {
  const map = {
    '1h': 'success',
    '2h': 'primary',
    '3h': 'warning',
    '4h': 'danger'
  }
  return map[duration] || 'info'
}

const getSegmentTypeLabel = (type) => {
  const map = {
    'opening': '开场',
    'product_intro': '产品介绍',
    'interaction': '互动',
    'promotion': '促销',
    'break': '休息',
    'closing': '结尾'
  }
  return map[type] || type
}

const getSegmentTypeColor = (type) => {
  const map = {
    'opening': 'success',
    'product_intro': 'primary',
    'interaction': 'warning',
    'promotion': 'danger',
    'break': 'info',
    'closing': 'success'
  }
  return map[type] || 'info'
}

const getProbabilityLabel = (prob) => {
  const map = {
    'low': '低',
    'medium': '中',
    'high': '高'
  }
  return map[prob] || prob
}

const getProbabilityColor = (prob) => {
  const map = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger'
  }
  return map[prob] || 'info'
}

const getImpactLabel = (impact) => {
  const map = {
    'low': '低',
    'medium': '中',
    'high': '高'
  }
  return map[impact] || impact
}

const getImpactColor = (impact) => {
  const map = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger'
  }
  return map[impact] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatScriptContent = (content) => {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/🎤/g, '<span style="font-size: 16px;">🎤</span>')
    .replace(/⚠️/g, '<span style="font-size: 16px;">⚠️</span>')
}

const getTotalSegments = () => {
  return scriptList.value.reduce((sum, s) => sum + (s.segments_count || 0), 0)
}

// API 调用
const fetchStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/statistics`)
    const data = await res.json()
    if (data.success) {
      stats.value = data.data
    }
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const loadScripts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      limit: pagination.page_size,
      offset: (pagination.page - 1) * pagination.page_size
    })
    
    const res = await fetch(`${API_BASE}/list?${params}`)
    const data = await res.json()
    if (data.success) {
      scriptList.value = data.data.scripts
      pagination.total = data.data.pagination.total
    }
  } catch (error) {
    ElMessage.error('加载剧本列表失败')
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    const res = await fetch(`${API_BASE}/templates`)
    const data = await res.json()
    if (data.success) {
      templates.value = data.data.templates || []
    }
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

const loadProducts = async () => {
  try {
    const res = await fetch(`${API_BASE}/products`)
    const data = await res.json()
    if (data.success) {
      products.value = data.data.products || []
    }
  } catch (error) {
    console.error('加载产品失败:', error)
  }
}

// 生成剧本
const generateScript = async () => {
  if (!generateForm.theme) {
    ElMessage.warning('请输入直播主题')
    return
  }
  
  generating.value = true
  try {
    const payload = {
      ...generateForm,
      selected_products: generateForm.selected_products.length > 0 
        ? generateForm.selected_products 
        : undefined
    }
    
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('剧本生成成功')
      currentScript.value = data.data
      await loadScripts()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error('生成剧本失败')
  } finally {
    generating.value = false
  }
}

const resetForm = () => {
  generateForm.theme = ''
  generateForm.duration = '2h'
  generateForm.target_audience = '所有人'
  generateForm.streamer_name = '主播'
  generateForm.template_id = null
  generateForm.selected_products = []
}

// 查看剧本
const viewScript = async (row) => {
  try {
    const res = await fetch(`${API_BASE}/${row.script_id}`)
    const data = await res.json()
    if (data.success) {
      currentScriptDetail.value = data.data
      currentScript.value = {
        script_id: data.data.script_id,
        title: data.data.title,
        duration: data.data.duration,
        theme: data.data.theme,
        generated_at: data.data.generated_at,
        segments_count: (data.data.segments || []).length,
        products_count: (data.data.products || []).length,
        interactions_count: (data.data.interactions || []).length,
        overall_flow: data.data.overall_flow
      }
      scriptDetailVisible.value = true
      detailTab.value = 'flow'
    } else {
      ElMessage.error('获取剧本详情失败')
    }
  } catch (error) {
    ElMessage.error('获取剧本详情失败')
  }
}

// 导出剧本
const exportScript = async (format, scriptId = null) => {
  const id = scriptId || (currentScript.value ? currentScript.value.script_id : null)
  if (!id) {
    ElMessage.warning('没有可导出的剧本')
    return
  }
  
  try {
    const res = await fetch(`${API_BASE}/${id}/export/${format}`)
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`剧本已导出为${format.toUpperCase()}格式：${data.data.output_path}`)
    } else {
      ElMessage.error(data.message || '导出失败')
    }
  } catch (error) {
    ElMessage.error('导出剧本失败')
  }
}

// 删除剧本
const deleteScript = async (scriptId) => {
  try {
    if (!await ElMessageBox.confirm('确定删除此剧本？', '提示')) return
    
    const res = await fetch(`${API_BASE}/${scriptId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('剧本删除成功')
      await loadScripts()
      await fetchStats()
      if (currentScript.value && currentScript.value.script_id === scriptId) {
        currentScript.value = null
      }
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除剧本失败')
  }
}

const deleteCurrentScript = () => {
  if (currentScript.value) {
    deleteScript(currentScript.value.script_id)
  }
}

// 添加产品
const showAddProductDialog = () => {
  productForm.name = ''
  productForm.category = ''
  productForm.price = 0
  productForm.original_price = 0
  productForm.discount = ''
  productForm.target_audience = ''
  productForm.script_template = ''
  productForm.selling_points_str = ''
  addProductVisible.value = true
}

const addProduct = async () => {
  if (!productForm.name) {
    ElMessage.warning('请输入产品名称')
    return
  }
  
  try {
    const payload = {
      ...productForm,
      selling_points: productForm.selling_points_str 
        ? productForm.selling_points_str.split(/[,,]/).map(s => s.trim()).filter(s => s)
        : []
    }
    
    const res = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('产品添加成功')
      addProductVisible.value = false
      await loadProducts()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '添加失败')
    }
  } catch (error) {
    ElMessage.error('添加产品失败')
  }
}

// 初始化
onMounted(() => {
  fetchStats()
  loadScripts()
  loadTemplates()
  loadProducts()
})
</script>

<style scoped>
.script-planner-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
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
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.main-tabs {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filters {
  display: flex;
  gap: 10px;
}

.actions {
  display: flex;
  gap: 10px;
}

.script-preview {
  padding: 10px;
}

.flow-content {
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 5px;
  line-height: 1.6;
}

.template-structure-item {
  display: inline-flex;
  align-items: center;
  margin-right: 10px;
  margin-bottom: 5px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.script-detail {
  padding: 10px;
}

.segment-card {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 5px;
  background: #fafafa;
}

.segment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.segment-time {
  color: #606266;
  font-weight: bold;
}

.segment-duration {
  color: #909399;
  font-size: 13px;
}

.segment-card h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.segment-description {
  color: #606266;
  margin-bottom: 15px;
}

.segment-content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #303133;
}

.segment-notes {
  margin-top: 15px;
  padding: 10px;
  background: #fef0f0;
  border-left: 3px solid #F56C6C;
  border-radius: 3px;
}

.segment-notes ul {
  margin: 5px 0 0 20px;
  padding: 0;
}

.segment-notes li {
  margin: 5px 0;
  color: #F56C6C;
}

.checklist-content {
  padding: 10px;
}

.checklist-item {
  margin-bottom: 10px;
}

.rule-item {
  margin-bottom: 5px;
  font-size: 13px;
}
</style>
