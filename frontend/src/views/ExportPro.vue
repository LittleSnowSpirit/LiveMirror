<template>
  <div class="export-pro-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>📤 专业数据导出</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showQuickExport = true">
          ⚡ 快速导出
        </button>
        <button class="btn btn-secondary" @click="loadStatistics">
          📊 统计
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="statistics">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_templates }}</div>
        <div class="stat-label">导出模板</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_jobs }}</div>
        <div class="stat-label">导出任务</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_export_runs }}</div>
        <div class="stat-label">总导出次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.scheduled_jobs }}</div>
        <div class="stat-label">定时任务</div>
      </div>
    </div>

    <!-- 选项卡 -->
    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'templates' }]"
        @click="activeTab = 'templates'"
      >
        📋 导出模板
      </button>
      <button
        :class="['tab', { active: activeTab === 'jobs' }]"
        @click="activeTab = 'jobs'"
      >
        ⏰ 定时任务
      </button>
      <button
        :class="['tab', { active: activeTab === 'history' }]"
        @click="activeTab = 'history'"
      >
        📜 导出历史
      </button>
    </div>

    <!-- 导出模板列表 -->
    <div v-if="activeTab === 'templates'" class="tab-content">
      <div class="toolbar">
        <div class="filter-group">
          <label>格式:</label>
          <select v-model="templateFilter.format">
            <option value="">全部</option>
            <option value="excel">Excel</option>
            <option value="word">Word</option>
            <option value="powerpoint">PowerPoint</option>
            <option value="pdf">PDF</option>
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
            <option value="custom">自定义</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="showCreateTemplateModal = true">
          + 新建模板
        </button>
      </div>

      <div class="template-list">
        <ExportTemplate
          v-for="template in filteredTemplates"
          :key="template.id"
          :template="template"
          @view="viewTemplate"
          @edit="editTemplate"
          @delete="deleteTemplate"
          @use="useTemplate"
        />
        
        <div v-if="filteredTemplates.length === 0" class="empty-state">
          <p>暂无导出模板</p>
          <button class="btn btn-primary" @click="showCreateTemplateModal = true">
            创建第一个模板
          </button>
        </div>
      </div>
    </div>

    <!-- 定时任务列表 -->
    <div v-if="activeTab === 'jobs'" class="tab-content">
      <div class="toolbar">
        <div class="filter-group">
          <label>格式:</label>
          <select v-model="jobFilter.format">
            <option value="">全部</option>
            <option value="excel">Excel</option>
            <option value="word">Word</option>
            <option value="powerpoint">PowerPoint</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="showCreateJobModal = true">
          + 新建任务
        </button>
        <button class="btn btn-secondary" @click="checkScheduledJobs">
          🔄 检查定时任务
        </button>
      </div>

      <div class="job-list">
        <div v-for="job in filteredJobs" :key="job.id" class="job-card">
          <div class="job-header">
            <h3>{{ job.name }}</h3>
            <div class="job-status">
              <span :class="['badge', job.enabled ? 'enabled' : 'disabled']">
                {{ job.enabled ? '已启用' : '已禁用' }}
              </span>
            </div>
          </div>
          
          <div class="job-info">
            <p><strong>格式:</strong> {{ formatLabel(job.format) }}</p>
            <p><strong>数据源:</strong> {{ job.data_source }}</p>
            <p v-if="job.schedule"><strong>定时:</strong> {{ job.schedule }}</p>
            <p><strong>运行次数:</strong> {{ job.run_count }}</p>
            <p v-if="job.last_run"><strong>上次运行:</strong> {{ formatDateTime(job.last_run) }}</p>
          </div>
          
          <div class="job-actions">
            <button class="btn btn-sm btn-primary" @click="runJobNow(job)">
              ▶ 立即运行
            </button>
            <button class="btn btn-sm btn-secondary" @click="editJob(job)">
              ✏ 编辑
            </button>
            <button class="btn btn-sm btn-danger" @click="deleteJob(job.id)">
              🗑 删除
            </button>
          </div>
        </div>
        
        <div v-if="filteredJobs.length === 0" class="empty-state">
          <p>暂无导出任务</p>
          <button class="btn btn-primary" @click="showCreateJobModal = true">
            创建第一个任务
          </button>
        </div>
      </div>
    </div>

    <!-- 导出历史 -->
    <div v-if="activeTab === 'history'" class="tab-content">
      <div class="history-list">
        <div v-for="item in exportHistory" :key="item.id" class="history-item">
          <div class="history-icon">
            <span v-if="item.format === 'excel'">📊</span>
            <span v-else-if="item.format === 'word'">📄</span>
            <span v-else-if="item.format === 'powerpoint'">📽</span>
            <span v-else-if="item.format === 'pdf'">📕</span>
            <span v-else>📁</span>
          </div>
          <div class="history-info">
            <div class="history-name">{{ item.name }}</div>
            <div class="history-meta">
              <span>{{ formatLabel(item.format) }}</span>
              <span>•</span>
              <span>{{ formatDateTime(item.created_at) }}</span>
            </div>
          </div>
          <div class="history-actions">
            <button class="btn btn-sm btn-secondary" @click="downloadFile(item)">
              ⬇ 下载
            </button>
          </div>
        </div>
        
        <div v-if="exportHistory.length === 0" class="empty-state">
          <p>暂无导出历史</p>
        </div>
      </div>
    </div>

    <!-- 快速导出弹窗 -->
    <div v-if="showQuickExport" class="modal-overlay" @click.self="showQuickExport = false">
      <div class="modal">
        <h2>⚡ 快速导出</h2>
        <form @submit.prevent="quickExport">
          <div class="form-group">
            <label>导出格式 *</label>
            <select v-model="quickExportData.format" required>
              <option value="excel">Excel（带图表）</option>
              <option value="word">Word 报告</option>
              <option value="powerpoint">PowerPoint 演示</option>
              <option value="pdf">PDF 文档</option>
              <option value="csv">CSV 数据</option>
              <option value="json">JSON 数据</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>选择模板（可选）</label>
            <select v-model="quickExportData.template_id">
              <option value="">不使用模板</option>
              <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
                {{ tpl.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>数据</label>
            <textarea
              v-model="quickExportData.data_json"
              rows="6"
              placeholder='输入 JSON 格式数据，例如：[{"name": "测试", "value": 100}]'
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showQuickExport = false">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="exporting">
              {{ exporting ? '导出中...' : '导出' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 创建/编辑模板弹窗 -->
    <div v-if="showCreateTemplateModal || showEditTemplateModal" class="modal-overlay" @click.self="closeTemplateModal">
      <div class="modal modal-large">
        <h2>{{ showEditTemplateModal ? '✏ 编辑模板' : '➕ 创建模板' }}</h2>
        <form @submit.prevent="saveTemplate">
          <div class="form-row">
            <div class="form-group">
              <label>模板名称 *</label>
              <input v-model="templateForm.name" type="text" required maxlength="100" />
            </div>
            
            <div class="form-group">
              <label>导出格式 *</label>
              <select v-model="templateForm.format" :disabled="showEditTemplateModal" required>
                <option value="excel">Excel</option>
                <option value="word">Word</option>
                <option value="powerpoint">PowerPoint</option>
                <option value="pdf">PDF</option>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
                <option value="custom">自定义</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>模板描述</label>
            <input v-model="templateForm.description" type="text" maxlength="500" />
          </div>
          
          <div class="form-group">
            <label>模板配置（JSON）</label>
            <textarea
              v-model="templateForm.config_json"
              rows="8"
              placeholder='输入 JSON 格式配置'
              required
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeTemplateModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="savingTemplate">
              {{ savingTemplate ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 创建/编辑任务弹窗 -->
    <div v-if="showCreateJobModal || showEditJobModal" class="modal-overlay" @click.self="closeJobModal">
      <div class="modal">
        <h2>{{ showEditJobModal ? '✏ 编辑任务' : '➕ 创建任务' }}</h2>
        <form @submit.prevent="saveJob">
          <div class="form-group">
            <label>任务名称 *</label>
            <input v-model="jobForm.name" type="text" required maxlength="100" />
          </div>
          
          <div class="form-group">
            <label>导出格式 *</label>
            <select v-model="jobForm.format" :disabled="showEditJobModal" required>
              <option value="excel">Excel</option>
              <option value="word">Word</option>
              <option value="powerpoint">PowerPoint</option>
              <option value="pdf">PDF</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>数据源 *</label>
            <input v-model="jobForm.data_source" type="text" required placeholder="例如：ticket_data" />
          </div>
          
          <div class="form-group">
            <label>使用模板（可选）</label>
            <select v-model="jobForm.template_id">
              <option value="">不使用模板</option>
              <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
                {{ tpl.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>定时调度（Cron 表达式，可选）</label>
            <input v-model="jobForm.schedule" type="text" placeholder="例如：0 0 * * * （每天午夜）" />
            <small class="help-text">留空表示手动执行</small>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeJobModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="savingJob">
              {{ savingJob ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import ExportTemplate from '../components/ExportTemplate.vue'

export default {
  name: 'ExportProPage',
  components: {
    ExportTemplate
  },
  data() {
    return {
      activeTab: 'templates',
      statistics: null,
      templates: [],
      jobs: [],
      exportHistory: [],
      templateFilter: {
        format: ''
      },
      jobFilter: {
        format: ''
      },
      showQuickExport: false,
      showCreateTemplateModal: false,
      showEditTemplateModal: false,
      showCreateJobModal: false,
      showEditJobModal: false,
      exporting: false,
      savingTemplate: false,
      savingJob: false,
      quickExportData: {
        format: 'excel',
        template_id: '',
        data_json: ''
      },
      templateForm: {
        id: '',
        name: '',
        format: 'excel',
        description: '',
        config_json: '{}'
      },
      jobForm: {
        id: '',
        name: '',
        format: 'excel',
        data_source: '',
        template_id: '',
        schedule: ''
      }
    }
  },
  computed: {
    filteredTemplates() {
      let result = this.templates
      if (this.templateFilter.format) {
        result = result.filter(t => t.format === this.templateFilter.format)
      }
      return result
    },
    filteredJobs() {
      let result = this.jobs
      if (this.jobFilter.format) {
        result = result.filter(j => j.format === this.jobFilter.format)
      }
      return result
    }
  },
  async mounted() {
    await this.loadStatistics()
    await this.loadTemplates()
    await this.loadJobs()
  },
  methods: {
    async loadStatistics() {
      try {
        const response = await fetch('/api/export/statistics')
        const data = await response.json()
        this.statistics = data
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },

    async loadTemplates() {
      try {
        const response = await fetch('/api/export/templates')
        const data = await response.json()
        this.templates = data
      } catch (error) {
        console.error('加载模板失败:', error)
      }
    },

    async loadJobs() {
      try {
        const response = await fetch('/api/export/jobs')
        const data = await response.json()
        this.jobs = data
      } catch (error) {
        console.error('加载任务失败:', error)
      }
    },

    async quickExport() {
      this.exporting = true
      try {
        let data
        try {
          data = JSON.parse(this.quickExportData.data_json)
        } catch (e) {
          alert('数据必须是有效的 JSON 格式')
          return
        }

        const response = await fetch('/api/export/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            format: this.quickExportData.format,
            data: data,
            template_id: this.quickExportData.template_id || undefined
          })
        })

        if (response.ok) {
          const result = await response.json()
          alert(`导出成功！\n${result.message}\n文件：${result.output_path}`)
          this.showQuickExport = false
          this.quickExportData = {
            format: 'excel',
            template_id: '',
            data_json: ''
          }
          this.exportHistory.unshift({
            id: Date.now(),
            name: `快速导出 - ${this.formatLabel(this.quickExportData.format)}`,
            format: this.quickExportData.format,
            created_at: new Date().toISOString(),
            path: result.output_path
          })
          await this.loadStatistics()
        }
      } catch (error) {
        console.error('快速导出失败:', error)
        alert('导出失败：' + error.message)
      } finally {
        this.exporting = false
      }
    },

    async saveTemplate() {
      this.savingTemplate = true
      try {
        let config
        try {
          config = JSON.parse(this.templateForm.config_json)
        } catch (e) {
          alert('配置必须是有效的 JSON 格式')
          return
        }

        const url = this.showEditTemplateModal
          ? `/api/export/templates/${this.templateForm.id}`
          : '/api/export/templates'
        
        const method = this.showEditTemplateModal ? 'PUT' : 'POST'

        const response = await fetch(url, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.templateForm.name,
            format: this.templateForm.format,
            config: config,
            description: this.templateForm.description
          })
        })

        if (response.ok) {
          await this.loadTemplates()
          this.closeTemplateModal()
          alert('模板保存成功')
        }
      } catch (error) {
        console.error('保存模板失败:', error)
        alert('保存失败：' + error.message)
      } finally {
        this.savingTemplate = false
      }
    },

    async saveJob() {
      this.savingJob = true
      try {
        const url = this.showEditJobModal
          ? `/api/export/jobs/${this.jobForm.id}`
          : '/api/export/jobs'
        
        const method = this.showEditJobModal ? 'PUT' : 'POST'

        const response = await fetch(url, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.jobForm.name,
            format: this.jobForm.format,
            data_source: this.jobForm.data_source,
            template_id: this.jobForm.template_id || undefined,
            schedule: this.jobForm.schedule || undefined
          })
        })

        if (response.ok) {
          await this.loadJobs()
          this.closeJobModal()
          alert('任务保存成功')
        }
      } catch (error) {
        console.error('保存任务失败:', error)
        alert('保存失败：' + error.message)
      } finally {
        this.savingJob = false
      }
    },

    viewTemplate(template) {
      alert(`模板详情:\n名称：${template.name}\n格式：${this.formatLabel(template.format)}\n描述：${template.description}\n\n配置:\n${JSON.stringify(template.config, null, 2)}`)
    },

    editTemplate(template) {
      this.templateForm = {
        id: template.id,
        name: template.name,
        format: template.format,
        description: template.description,
        config_json: JSON.stringify(template.config, null, 2)
      }
      this.showEditTemplateModal = true
    },

    async deleteTemplate(templateId) {
      if (!confirm('确定要删除这个模板吗？')) return
      
      try {
        const response = await fetch(`/api/export/templates/${templateId}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          await this.loadTemplates()
          alert('模板已删除')
        }
      } catch (error) {
        console.error('删除模板失败:', error)
      }
    },

    useTemplate(template) {
      this.quickExportData.template_id = template.id
      this.quickExportData.format = template.format
      this.showQuickExport = true
    },

    editJob(job) {
      this.jobForm = {
        id: job.id,
        name: job.name,
        format: job.format,
        data_source: job.data_source,
        template_id: job.template_id || '',
        schedule: job.schedule || ''
      }
      this.showEditJobModal = true
    },

    async runJobNow(job) {
      if (!confirm(`确定要立即运行任务 "${job.name}" 吗？`)) return
      
      try {
        // 模拟运行，实际需要传入数据
        const response = await fetch(`/api/export/jobs/${job.id}/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify([{ name: '示例数据', value: 100 }])
        })
        
        if (response.ok) {
          const result = await response.json()
          alert(`任务运行成功！\n${result.message}\n文件：${result.output_path}`)
          await this.loadJobs()
          await this.loadStatistics()
        }
      } catch (error) {
        console.error('运行任务失败:', error)
        alert('运行失败：' + error.message)
      }
    },

    async deleteJob(jobId) {
      if (!confirm('确定要删除这个任务吗？')) return
      
      try {
        const response = await fetch(`/api/export/jobs/${jobId}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          await this.loadJobs()
          alert('任务已删除')
        }
      } catch (error) {
        console.error('删除任务失败:', error)
      }
    },

    async checkScheduledJobs() {
      try {
        const response = await fetch('/api/export/scheduled-jobs/check', {
          method: 'POST'
        })
        
        if (response.ok) {
          const result = await response.json()
          alert(`检查完成，共 ${result.checked} 个定时任务`)
          await this.loadJobs()
        }
      } catch (error) {
        console.error('检查定时任务失败:', error)
      }
    },

    downloadFile(item) {
      // 模拟下载
      alert(`下载文件：${item.path}`)
    },

    closeTemplateModal() {
      this.showCreateTemplateModal = false
      this.showEditTemplateModal = false
      this.templateForm = {
        id: '',
        name: '',
        format: 'excel',
        description: '',
        config_json: '{}'
      }
    },

    closeJobModal() {
      this.showCreateJobModal = false
      this.showEditJobModal = false
      this.jobForm = {
        id: '',
        name: '',
        format: 'excel',
        data_source: '',
        template_id: '',
        schedule: ''
      }
    },

    formatLabel(format) {
      const labels = {
        excel: 'Excel',
        word: 'Word',
        powerpoint: 'PowerPoint',
        pdf: 'PDF',
        csv: 'CSV',
        json: 'JSON',
        custom: '自定义'
      }
      return labels[format] || format
    },

    formatDateTime(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.export-pro-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
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
  gap: 10px;
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1890ff;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

/* 选项卡 */
.tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e8e8e8;
}

.tab {
  padding: 10px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.3s;
}

.tab:hover {
  background: #f5f5f5;
}

.tab.active {
  border-bottom-color: #1890ff;
  color: #1890ff;
  font-weight: bold;
}

.tab-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #666;
}

.filter-group select {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

/* 模板列表 */
.template-list {
  display: grid;
  gap: 15px;
}

/* 任务列表 */
.job-list {
  display: grid;
  gap: 15px;
}

.job-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  background: #fafafa;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.job-header h3 {
  margin: 0;
  font-size: 16px;
}

.job-status {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge.enabled {
  background: #52c41a;
  color: #fff;
}

.badge.disabled {
  background: #d9d9d9;
  color: #666;
}

.job-info {
  margin-bottom: 15px;
}

.job-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.job-actions {
  display: flex;
  gap: 10px;
}

/* 导出历史 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background: #fafafa;
}

.history-icon {
  font-size: 24px;
}

.history-info {
  flex: 1;
}

.history-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.history-meta {
  font-size: 12px;
  color: #999;
}

.history-meta span {
  margin: 0 4px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

/* 按钮 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #d9d9d9;
}

.btn-secondary:hover {
  background: #e6e6e6;
}

.btn-danger {
  background: #ff4d4f;
  color: #fff;
}

.btn-danger:hover {
  background: #ff7875;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 700px;
}

.modal h2 {
  margin: 0 0 20px 0;
}

/* 表单 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
  font-family: monospace;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.help-text {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #999;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
