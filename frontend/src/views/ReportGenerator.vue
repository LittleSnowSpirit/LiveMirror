<template>
  <div class="report-generator-page">
    <div class="page-header">
      <h1>📊 数据报表</h1>
      <p class="subtitle">自动生成日报/周报/月报，支持多格式导出</p>
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
              <div class="stat-value">{{ stats.total_reports }}</div>
              <div class="stat-label">已生成报表</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #67C23A;">
              <i class="el-icon-time"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active_schedules }}</div>
              <div class="stat-label">定时任务</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #E6A23C;">
              <i class="el-icon-connection"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_templates }}</div>
              <div class="stat-label">模板数量</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon" style="background: #F56C6C;">
              <i class="el-icon-download"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.reports_by_type?.daily || 0 }}</div>
              <div class="stat-label">今日日报</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 报表生成 -->
      <el-tab-pane label="报表生成" name="generate">
        <div class="generate-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>🚀 快速生成</span>
              </div>
            </template>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-button 
                  type="primary" 
                  size="large"
                  @click="quickGenerate('daily')"
                  :loading="generating"
                  style="width: 100%; height: 100px;"
                >
                  <div class="quick-generate-btn">
                    <i class="el-icon-date" style="font-size: 24px;"></i>
                    <div style="margin-top: 10px;">生成日报</div>
                    <div style="font-size: 12px; opacity: 0.8;">今日数据汇总</div>
                  </div>
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button 
                  type="success" 
                  size="large"
                  @click="quickGenerate('weekly')"
                  :loading="generating"
                  style="width: 100%; height: 100px;"
                >
                  <div class="quick-generate-btn">
                    <i class="el-icon-calendar" style="font-size: 24px;"></i>
                    <div style="margin-top: 10px;">生成周报</div>
                    <div style="font-size: 12px; opacity: 0.8;">本周数据汇总</div>
                  </div>
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button 
                  type="warning" 
                  size="large"
                  @click="quickGenerate('monthly')"
                  :loading="generating"
                  style="width: 100%; height: 100px;"
                >
                  <div class="quick-generate-btn">
                    <i class="el-icon-date" style="font-size: 24px;"></i>
                    <div style="margin-top: 10px;">生成月报</div>
                    <div style="font-size: 12px; opacity: 0.8;">本月数据汇总</div>
                  </div>
                </el-button>
              </el-col>
            </el-row>
          </el-card>

          <el-card style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>⚙️ 自定义生成</span>
              </div>
            </template>
            
            <el-form :model="generateForm" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="报表类型">
                    <el-select v-model="generateForm.report_type" style="width: 100%;">
                      <el-option label="日报" value="daily" />
                      <el-option label="周报" value="weekly" />
                      <el-option label="月报" value="monthly" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="开始日期">
                    <el-date-picker
                      v-model="generateForm.start_date"
                      type="date"
                      placeholder="选择开始日期"
                      style="width: 100%;"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="结束日期">
                    <el-date-picker
                      v-model="generateForm.end_date"
                      type="date"
                      placeholder="选择结束日期"
                      style="width: 100%;"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="选择模板">
                    <el-select v-model="generateForm.template_id" placeholder="使用默认模板" clearable style="width: 100%;">
                      <el-option
                        v-for="tpl in templates"
                        :key="tpl.template_id"
                        :label="tpl.name"
                        :value="tpl.template_id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item>
                <el-button type="primary" @click="generateReport" :loading="generating">
                  生成报表
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 报表列表 -->
      <el-tab-pane label="报表列表" name="list">
        <div class="toolbar">
          <div class="filters">
            <el-select v-model="listFilter.type" placeholder="全部类型" clearable @change="loadReports">
              <el-option label="日报" value="daily" />
              <el-option label="周报" value="weekly" />
              <el-option label="月报" value="monthly" />
            </el-select>
          </div>
          <div class="actions">
            <el-button @click="loadReports">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
          </div>
        </div>

        <el-table :data="reportList" v-loading="loading" border>
          <el-table-column prop="report_id" label="报表 ID" width="200" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeColor(row.report_type)" size="small">
                {{ getTypeLabel(row.report_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="period" label="周期" width="200" />
          <el-table-column prop="summary" label="摘要" show-overflow-tooltip />
          <el-table-column prop="generated_at" label="生成时间" width="180" />
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click="viewReport(row.report_id)">
                查看
              </el-button>
              <el-button type="text" size="small" @click="exportReport(row.report_id, 'pdf')">
                PDF
              </el-button>
              <el-button type="text" size="small" @click="exportReport(row.report_id, 'excel')">
                Excel
              </el-button>
              <el-button type="text" size="small" @click="exportReport(row.report_id, 'json')" style="color: #909399;">
                JSON
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
          @change="loadReports"
          style="margin-top: 20px; justify-content: flex-end;"
        />
      </el-tab-pane>

      <!-- 模板管理 -->
      <el-tab-pane label="模板管理" name="templates">
        <div class="toolbar">
          <div class="actions">
            <el-button type="primary" @click="showCreateTemplateDialog">
              <i class="el-icon-plus"></i> 新建模板
            </el-button>
          </div>
        </div>

        <el-table :data="templates" v-loading="loading" border>
          <el-table-column prop="name" label="模板名称" width="200" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeColor(row.type)" size="small">
                {{ getTypeLabel(row.type) }}
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
          <el-table-column prop="sections_count" label="章节数" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="text" 
                size="small" 
                @click="useTemplate(row.template_id)"
                :disabled="row.is_default"
              >
                使用
              </el-button>
              <el-button 
                type="text" 
                size="small" 
                @click="deleteTemplate(row.template_id)"
                :disabled="row.is_default"
                style="color: #F56C6C;"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 定时任务 -->
      <el-tab-pane label="定时任务" name="schedules">
        <div class="toolbar">
          <div class="actions">
            <el-button type="primary" @click="showCreateScheduleDialog">
              <i class="el-icon-plus"></i> 新建任务
            </el-button>
          </div>
        </div>

        <el-table :data="schedules" v-loading="loading" border>
          <el-table-column prop="schedule_id" label="任务 ID" width="200" />
          <el-table-column label="报表类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getTypeColor(row.report_type)" size="small">
                {{ getTypeLabel(row.report_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="cron_expression" label="Cron 表达式" width="150" />
          <el-table-column prop="export_format" label="导出格式" width="100" />
          <el-table-column label="邮件发送" width="100">
            <template #default="{ row }">
              <el-tag :type="row.send_email ? 'success' : 'info'" size="small">
                {{ row.send_email ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="微信发送" width="100">
            <template #default="{ row }">
              <el-tag :type="row.send_wechat ? 'success' : 'info'" size="small">
                {{ row.send_wechat ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'danger'" size="small">
                {{ row.enabled ? '启用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click="toggleSchedule(row)">
                {{ row.enabled ? '停用' : '启用' }}
              </el-button>
              <el-button type="text" size="small" @click="editSchedule(row)">
                编辑
              </el-button>
              <el-button 
                type="text" 
                size="small" 
                @click="deleteSchedule(row.schedule_id)"
                style="color: #F56C6C;"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 报表详情对话框 -->
    <el-dialog v-model="reportDetailVisible" title="报表详情" width="80%">
      <div v-if="currentReport" class="report-detail">
        <div class="report-header">
          <h3>{{ getTypeLabel(currentReport.report_type) }}</h3>
          <p>{{ currentReport.period }}</p>
          <p class="summary">{{ currentReport.overall_summary }}</p>
        </div>
        
        <div v-for="section in currentReport.sections" :key="section.title" class="report-section">
          <h4>{{ section.title }}</h4>
          <el-table :data="section.metrics" size="small" border>
            <el-table-column prop="name" label="指标" width="150" />
            <el-table-column prop="value" label="数值" width="120">
              <template #default="{ row }">
                {{ formatValue(row.value, row.unit) }}
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column label="变化率" width="100">
              <template #default="{ row }">
                <span v-if="row.change_rate !== null" :class="getTrendClass(row.change_rate)">
                  {{ row.change_rate > 0 ? '+' : '' }}{{ row.change_rate.toFixed(2) }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="趋势" width="80">
              <template #default="{ row }">
                <i 
                  v-if="row.trend === 'up'" 
                  class="el-icon-top" 
                  style="color: #67C23A;"
                ></i>
                <i 
                  v-else-if="row.trend === 'down'" 
                  class="el-icon-bottom" 
                  style="color: #F56C6C;"
                ></i>
                <i v-else class="el-icon-minus" style="color: #909399;"></i>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 创建模板对话框 -->
    <el-dialog v-model="createTemplateVisible" title="创建模板" width="60%">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="templateForm.name" placeholder="输入模板名称" />
        </el-form-item>
        <el-form-item label="报表类型">
          <el-select v-model="templateForm.report_type" style="width: 100%;">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="章节配置">
          <el-button type="primary" size="small" @click="addTemplateSection">
            添加章节
          </el-button>
          <div v-for="(section, idx) in templateForm.sections" :key="idx" class="template-section-item">
            <el-input 
              v-model="section.title" 
              placeholder="章节标题" 
              style="width: 200px; margin-right: 10px;"
            />
            <el-button type="danger" size="small" @click="removeTemplateSection(idx)">删除</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTemplateVisible = false">取消</el-button>
        <el-button type="primary" @click="createTemplate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 创建定时任务对话框 -->
    <el-dialog v-model="createScheduleVisible" title="创建定时任务" width="60%">
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="报表类型">
          <el-select v-model="scheduleForm.report_type" style="width: 100%;">
            <el-option label="日报" value="daily" />
            <el-option label="周报" value="weekly" />
            <el-option label="月报" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron 表达式">
          <el-input 
            v-model="scheduleForm.cron_expression" 
            placeholder="例如：0 9 * * * (每天 9 点)"
          />
          <div class="form-tip">常用表达式：0 9 * * * (每天 9 点), 0 9 * * 1 (每周一 9 点), 0 9 1 * * (每月 1 号 9 点)</div>
        </el-form-item>
        <el-form-item label="选择模板">
          <el-select v-model="scheduleForm.template_id" placeholder="使用默认模板" clearable style="width: 100%;">
            <el-option
              v-for="tpl in templates"
              :key="tpl.template_id"
              :label="tpl.name"
              :value="tpl.template_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="导出格式">
          <el-select v-model="scheduleForm.export_format" style="width: 100%;">
            <el-option label="PDF" value="pdf" />
            <el-option label="Excel" value="excel" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮件发送">
          <el-switch v-model="scheduleForm.send_email" />
        </el-form-item>
        <el-form-item label="邮件接收者" v-if="scheduleForm.send_email">
          <el-input 
            v-model="scheduleForm.email_recipients_str" 
            placeholder="多个邮箱用逗号分隔"
          />
        </el-form-item>
        <el-form-item label="微信发送">
          <el-switch v-model="scheduleForm.send_wechat" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createScheduleVisible = false">取消</el-button>
        <el-button type="primary" @click="createSchedule">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_BASE = '/api/report'

// 状态
const activeTab = ref('generate')
const loading = ref(false)
const generating = ref(false)
const stats = ref({})
const reportList = ref([])
const templates = ref([])
const schedules = ref([])
const currentReport = ref(null)

// 对话框
const reportDetailVisible = ref(false)
const createTemplateVisible = ref(false)
const createScheduleVisible = ref(false)

// 表单
const generateForm = reactive({
  report_type: 'daily',
  start_date: null,
  end_date: null,
  template_id: null
})

const templateForm = reactive({
  name: '',
  report_type: 'daily',
  sections: []
})

const scheduleForm = reactive({
  report_type: 'daily',
  cron_expression: '',
  template_id: null,
  export_format: 'pdf',
  send_email: false,
  email_recipients_str: '',
  email_recipients: [],
  send_wechat: false
})

const listFilter = reactive({
  type: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 工具函数
const getTypeLabel = (type) => {
  const map = {
    daily: '日报',
    weekly: '周报',
    monthly: '月报'
  }
  return map[type] || type
}

const getTypeColor = (type) => {
  const map = {
    daily: 'primary',
    weekly: 'success',
    monthly: 'warning'
  }
  return map[type] || 'info'
}

const formatValue = (value, unit) => {
  if (typeof value === 'number') {
    if (value > 10000) {
      return (value / 10000).toFixed(2) + '万'
    }
    return value.toFixed(2)
  }
  return value
}

const getTrendClass = (changeRate) => {
  if (changeRate > 0) return 'trend-up'
  if (changeRate < 0) return 'trend-down'
  return 'trend-stable'
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

const loadReports = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      limit: pagination.page_size,
      offset: (pagination.page - 1) * pagination.page_size
    })
    if (listFilter.type) {
      params.append('report_type', listFilter.type)
    }
    
    const res = await fetch(`${API_BASE}/list?${params}`)
    const data = await res.json()
    if (data.success) {
      reportList.value = data.data.reports
      pagination.total = data.data.pagination.total
    }
  } catch (error) {
    ElMessage.error('加载报表列表失败')
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

const loadSchedules = async () => {
  try {
    const res = await fetch(`${API_BASE}/schedules`)
    const data = await res.json()
    if (data.success) {
      schedules.value = data.data.schedules || []
    }
  } catch (error) {
    console.error('加载定时任务失败:', error)
  }
}

// 快速生成
const quickGenerate = async (type) => {
  generating.value = true
  try {
    const res = await fetch(`${API_BASE}/generate/${type}`, {
      method: 'POST'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`${getTypeLabel(type)}生成成功`)
      await loadReports()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error('生成报表失败')
  } finally {
    generating.value = false
  }
}

// 自定义生成
const generateReport = async () => {
  generating.value = true
  try {
    const payload = {
      report_type: generateForm.report_type,
      template_id: generateForm.template_id
    }
    if (generateForm.start_date) {
      payload.start_date = new Date(generateForm.start_date).toISOString()
    }
    if (generateForm.end_date) {
      payload.end_date = new Date(generateForm.end_date).toISOString()
    }
    
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('报表生成成功')
      await loadReports()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error('生成报表失败')
  } finally {
    generating.value = false
  }
}

// 查看报表
const viewReport = async (reportId) => {
  try {
    const res = await fetch(`${API_BASE}/${reportId}`)
    const data = await res.json()
    if (data.success) {
      currentReport.value = data.data
      reportDetailVisible.value = true
    } else {
      ElMessage.error('获取报表详情失败')
    }
  } catch (error) {
    ElMessage.error('获取报表详情失败')
  }
}

// 导出报表
const exportReport = async (reportId, format) => {
  try {
    const res = await fetch(`${API_BASE}/${reportId}/export/${format}`)
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`报表已导出为${format.toUpperCase()}格式`)
    } else {
      ElMessage.error(data.message || '导出失败')
    }
  } catch (error) {
    ElMessage.error('导出报表失败')
  }
}

// 模板管理
const showCreateTemplateDialog = () => {
  templateForm.name = ''
  templateForm.report_type = 'daily'
  templateForm.sections = []
  createTemplateVisible.value = true
}

const addTemplateSection = () => {
  templateForm.sections.push({ title: '', metrics: [] })
}

const removeTemplateSection = (idx) => {
  templateForm.sections.splice(idx, 1)
}

const createTemplate = async () => {
  try {
    const res = await fetch(`${API_BASE}/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: templateForm.name,
        report_type: templateForm.report_type,
        sections: templateForm.sections
      })
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('模板创建成功')
      createTemplateVisible.value = false
      await loadTemplates()
    } else {
      ElMessage.error(data.message || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建模板失败')
  }
}

const deleteTemplate = async (templateId) => {
  try {
    if (!await ElMessageBox.confirm('确定删除此模板？', '提示')) return
    
    const res = await fetch(`${API_BASE}/templates/${templateId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('模板删除成功')
      await loadTemplates()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除模板失败')
  }
}

const useTemplate = (templateId) => {
  generateForm.template_id = templateId
  activeTab.value = 'generate'
  ElMessage.success('已选择该模板')
}

// 定时任务管理
const showCreateScheduleDialog = () => {
  scheduleForm.report_type = 'daily'
  scheduleForm.cron_expression = ''
  scheduleForm.template_id = null
  scheduleForm.export_format = 'pdf'
  scheduleForm.send_email = false
  scheduleForm.email_recipients_str = ''
  scheduleForm.email_recipients = []
  scheduleForm.send_wechat = false
  createScheduleVisible.value = true
}

const createSchedule = async () => {
  try {
    const payload = {
      report_type: scheduleForm.report_type,
      cron_expression: scheduleForm.cron_expression,
      template_id: scheduleForm.template_id,
      export_format: scheduleForm.export_format,
      send_email: scheduleForm.send_email,
      send_wechat: scheduleForm.send_wechat
    }
    if (scheduleForm.send_email && scheduleForm.email_recipients_str) {
      payload.email_recipients = scheduleForm.email_recipients_str.split(',').map(e => e.trim())
    }
    
    const res = await fetch(`${API_BASE}/schedules`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('定时任务创建成功')
      createScheduleVisible.value = false
      await loadSchedules()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建定时任务失败')
  }
}

const toggleSchedule = async (schedule) => {
  try {
    const res = await fetch(`${API_BASE}/schedules/${schedule.schedule_id}/toggle`, {
      method: 'POST'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(data.message)
      await loadSchedules()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const editSchedule = (schedule) => {
  scheduleForm.report_type = schedule.report_type
  scheduleForm.cron_expression = schedule.cron_expression
  scheduleForm.template_id = schedule.template_id
  scheduleForm.export_format = schedule.export_format
  scheduleForm.send_email = schedule.send_email
  scheduleForm.email_recipients_str = (schedule.email_recipients || []).join(', ')
  scheduleForm.email_recipients = schedule.email_recipients || []
  scheduleForm.send_wechat = schedule.send_wechat
  createScheduleVisible.value = true
}

const deleteSchedule = async (scheduleId) => {
  try {
    if (!await ElMessageBox.confirm('确定删除此定时任务？', '提示')) return
    
    const res = await fetch(`${API_BASE}/schedules/${scheduleId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('定时任务删除成功')
      await loadSchedules()
      await fetchStats()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除定时任务失败')
  }
}

// 初始化
onMounted(() => {
  fetchStats()
  loadReports()
  loadTemplates()
  loadSchedules()
})
</script>

<style scoped>
.report-generator-page {
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

.quick-generate-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

.search-box {
  width: 300px;
}

.template-section-item {
  display: flex;
  align-items: center;
  margin-top: 10px;
  gap: 10px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.report-detail {
  padding: 10px;
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.report-header h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
}

.report-header .summary {
  margin-top: 15px;
  color: #606266;
  font-size: 14px;
}

.report-section {
  margin-bottom: 30px;
}

.report-section h4 {
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #409EFF;
  color: #303133;
}

.trend-up {
  color: #67C23A;
  font-weight: bold;
}

.trend-down {
  color: #F56C6C;
  font-weight: bold;
}

.trend-stable {
  color: #909399;
}
</style>
