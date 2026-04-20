<template>
  <div class="campaign-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>📊 营销活动策划</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showCreateModal = true">
          + 新建活动
        </button>
        <button class="btn btn-secondary" @click="showTemplates = !showTemplates">
          📋 活动模板
        </button>
        <button class="btn btn-secondary" @click="showCases = !showCases">
          💡 案例库
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_campaigns }}</div>
        <div class="stat-label">总活动数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.by_status.active || 0 }}</div>
        <div class="stat-label">进行中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">¥{{ (stats.total_budget / 10000).toFixed(1) }}万</div>
        <div class="stat-label">总预算</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.avg_roi.toFixed(1) }}</div>
        <div class="stat-label">平均健康度</div>
      </div>
    </div>

    <!-- 活动列表 -->
    <div class="campaign-list">
      <div class="list-header">
        <h2>我的活动</h2>
        <div class="filter-group">
          <select v-model="filterStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="draft">草稿</option>
            <option value="planning">规划中</option>
            <option value="active">进行中</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
      </div>

      <div class="campaigns-grid">
        <CampaignCard
          v-for="campaign in filteredCampaigns"
          :key="campaign.id"
          :campaign="campaign"
          @view="viewCampaign"
          @edit="editCampaign"
          @delete="deleteCampaign"
          @update-status="updateCampaignStatus"
        />
      </div>

      <div v-if="filteredCampaigns.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无活动</p>
        <button class="btn btn-primary" @click="showCreateModal = true">
          创建第一个活动
        </button>
      </div>
    </div>

    <!-- 活动模板面板 -->
    <div v-if="showTemplates" class="panel-overlay">
      <div class="panel">
        <div class="panel-header">
          <h2>📋 活动策划模板</h2>
          <button class="btn-close" @click="showTemplates = false">×</button>
        </div>
        <div class="panel-content">
          <div v-for="template in templates" :key="template.id" class="template-card">
            <div class="template-header">
              <h3>{{ template.name }}</h3>
              <span class="template-type">{{ getTemplateTypeName(template.campaign_type) }}</span>
            </div>
            <p class="template-desc">{{ template.description }}</p>
            <div class="template-info">
              <div class="info-item">
                <span class="label">建议时长</span>
                <span class="value">{{ template.recommended_duration_days }}天</span>
              </div>
              <div class="info-item">
                <span class="label">预算范围</span>
                <span class="value">
                  ¥{{ (template.typical_budget_range.min / 10000).toFixed(0) }}万 - 
                  ¥{{ (template.typical_budget_range.max / 10000).toFixed(0) }}万
                </span>
              </div>
            </div>
            <div class="template-section">
              <h4>核心指标</h4>
              <div class="tags">
                <span v-for="metric in template.key_metrics" :key="metric" class="tag">
                  {{ metric }}
                </span>
              </div>
            </div>
            <div class="template-section">
              <h4>最佳实践</h4>
              <ul class="checklist">
                <li v-for="practice in template.best_practices" :key="practice">
                  ✓ {{ practice }}
                </li>
              </ul>
            </div>
            <button class="btn btn-primary btn-block" @click="createFromTemplate(template)">
              使用此模板创建
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 案例库面板 -->
    <div v-if="showCases" class="panel-overlay">
      <div class="panel panel-wide">
        <div class="panel-header">
          <h2>💡 优秀活动案例库</h2>
          <button class="btn-close" @click="showCases = false">×</button>
        </div>
        <div class="panel-content">
          <div class="search-bar">
            <input
              v-model="caseSearch"
              type="text"
              placeholder="搜索案例（关键词用逗号分隔）..."
              @keyup.enter="searchCases"
            />
            <button class="btn btn-primary" @click="searchCases">搜索</button>
          </div>
          <div v-for="caseItem in displayedCases" :key="caseItem.id" class="case-card">
            <div class="case-header">
              <h3>{{ caseItem.title }}</h3>
              <span class="case-industry">{{ caseItem.industry }}</span>
            </div>
            <p class="case-desc">{{ caseItem.description }}</p>
            <div class="case-results">
              <div class="result-item" v-for="(value, key) in caseItem.results" :key="key">
                <span class="result-label">{{ key }}</span>
                <span class="result-value">{{ formatResultValue(key, value) }}</span>
              </div>
            </div>
            <div class="case-stats">
              <div class="stat">
                <span class="stat-label">预算</span>
                <span class="stat-value">¥{{ (caseItem.budget / 10000).toFixed(0) }}万</span>
              </div>
              <div class="stat">
                <span class="stat-label">ROI</span>
                <span class="stat-value">{{ caseItem.roi.toFixed(1) }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">时长</span>
                <span class="stat-value">{{ caseItem.duration_days }}天</span>
              </div>
            </div>
            <div class="case-learnings">
              <h4>关键经验</h4>
              <ul>
                <li v-for="learning in caseItem.key_learnings" :key="learning">
                  💡 {{ learning }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建活动模态框 -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal modal-large">
        <div class="modal-header">
          <h2>创建新活动</h2>
          <button class="btn-close" @click="showCreateModal = false">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createCampaign" class="campaign-form">
            <div class="form-group">
              <label>活动名称 *</label>
              <input v-model="newCampaign.name" type="text" required placeholder="输入活动名称" />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>活动类型 *</label>
                <select v-model="newCampaign.campaign_type" required @change="onTypeChange">
                  <option value="promotion">促销活动</option>
                  <option value="product_launch">产品发布</option>
                  <option value="brand_awareness">品牌宣传</option>
                  <option value="user_acquisition">用户获取</option>
                  <option value="retention">用户留存</option>
                  <option value="seasonal">季节性活动</option>
                </select>
              </div>
              <div class="form-group">
                <label>状态</label>
                <select v-model="newCampaign.status">
                  <option value="draft">草稿</option>
                  <option value="planning">规划中</option>
                  <option value="active">进行中</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>活动描述</label>
              <textarea v-model="newCampaign.description" rows="3" placeholder="活动描述..."></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>开始日期 *</label>
                <input v-model="newCampaign.start_date" type="date" required />
              </div>
              <div class="form-group">
                <label>结束日期 *</label>
                <input v-model="newCampaign.end_date" type="date" required />
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="generateTimeline">
                📅 生成时间规划
              </button>
              <button type="button" class="btn btn-secondary" @click="showBudgetEditor = true">
                💰 编辑预算
              </button>
              <button type="button" class="btn btn-secondary" @click="showMetricsEditor = true">
                📈 设置指标
              </button>
            </div>

            <div class="form-group">
              <label>备注</label>
              <textarea v-model="newCampaign.notes" rows="2" placeholder="备注信息..."></textarea>
            </div>

            <div class="form-group">
              <label>标签</label>
              <input v-model="newCampaign.tagsInput" type="text" placeholder="标签，用逗号分隔" />
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" @click="createCampaign">创建活动</button>
        </div>
      </div>
    </div>

    <!-- 预算编辑器 -->
    <div v-if="showBudgetEditor" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>💰 预算编辑</h2>
          <button class="btn-close" @click="showBudgetEditor = false">×</button>
        </div>
        <div class="modal-body">
          <div v-for="(item, index) in newCampaign.budget_items" :key="index" class="budget-item">
            <input v-model="item.category" type="text" placeholder="类别（如：广告投放）" />
            <input v-model.number="item.planned" type="number" placeholder="预算金额" />
            <input v-model="item.description" type="text" placeholder="说明" />
            <button class="btn btn-danger btn-sm" @click="removeBudgetItem(index)">删除</button>
          </div>
          <button class="btn btn-secondary btn-block" @click="addBudgetItem">+ 添加预算项</button>
          
          <div v-if="newCampaign.budget_items.length > 0" class="budget-summary">
            <div class="summary-row">
              <span>总预算：</span>
              <span class="total">¥{{ calculateBudgetTotal.planned.toLocaleString() }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showBudgetEditor = false">完成</button>
        </div>
      </div>
    </div>

    <!-- 指标编辑器 -->
    <div v-if="showMetricsEditor" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>📈 指标设置</h2>
          <button class="btn-close" @click="showMetricsEditor = false">×</button>
        </div>
        <div class="modal-body">
          <div v-for="(metric, index) in newCampaign.metrics" :key="index" class="metric-item">
            <input v-model="metric.name" type="text" placeholder="指标名称" />
            <input v-model.number="metric.target" type="number" placeholder="目标值" />
            <input v-model="metric.unit" type="text" placeholder="单位" />
            <button class="btn btn-danger btn-sm" @click="removeMetric(index)">删除</button>
          </div>
          <button class="btn btn-secondary btn-block" @click="addMetric">+ 添加指标</button>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showMetricsEditor = false">完成</button>
        </div>
      </div>
    </div>

    <!-- 活动详情面板 -->
    <div v-if="selectedCampaign" class="panel-overlay">
      <div class="panel panel-wide">
        <div class="panel-header">
          <h2>{{ selectedCampaign.name }}</h2>
          <button class="btn-close" @click="selectedCampaign = null">×</button>
        </div>
        <div class="panel-content">
          <!-- 活动基本信息 -->
          <div class="detail-section">
            <h3>基本信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">类型</span>
                <span class="value">{{ getCampaignTypeName(selectedCampaign.campaign_type) }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态</span>
                <span class="value status-badge" :class="selectedCampaign.status">
                  {{ getStatusName(selectedCampaign.status) }}
                </span>
              </div>
              <div class="info-item">
                <span class="label">时间</span>
                <span class="value">{{ selectedCampaign.start_date }} 至 {{ selectedCampaign.end_date }}</span>
              </div>
            </div>
            <p class="description">{{ selectedCampaign.description }}</p>
          </div>

          <!-- 时间线 -->
          <div class="detail-section" v-if="selectedCampaign.timeline && selectedCampaign.timeline.length > 0">
            <h3>📅 时间规划</h3>
            <div class="timeline">
              <div v-for="(phase, index) in selectedCampaign.timeline" :key="index" class="timeline-phase" :class="phase.status">
                <div class="phase-header">
                  <h4>{{ phase.name }}</h4>
                  <span class="phase-dates">{{ phase.start_date }} - {{ phase.end_date }}</span>
                </div>
                <ul class="phase-tasks">
                  <li v-for="task in phase.tasks" :key="task">{{ task }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 预算 -->
          <div class="detail-section" v-if="selectedCampaign.budget_items && selectedCampaign.budget_items.length > 0">
            <h3>💰 预算</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>类别</th>
                  <th>预算</th>
                  <th>实际</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in selectedCampaign.budget_items" :key="index">
                  <td>{{ item.category }}</td>
                  <td>¥{{ item.planned.toLocaleString() }}</td>
                  <td>¥{{ (item.actual || 0).toLocaleString() }}</td>
                  <td>{{ item.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 指标追踪 -->
          <div class="detail-section" v-if="selectedCampaign.metrics && selectedCampaign.metrics.length > 0">
            <h3>📈 效果追踪</h3>
            <div class="metrics-grid">
              <div v-for="(metric, index) in selectedCampaign.metrics" :key="index" class="metric-card" :class="metric.trend">
                <div class="metric-name">{{ metric.name }}</div>
                <div class="metric-values">
                  <span class="actual">{{ metric.actual }}</span>
                  <span class="target">目标：{{ metric.target }}</span>
                </div>
                <div class="metric-progress">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: Math.min((metric.actual / metric.target) * 100, 100) + '%' }"></div>
                  </div>
                  <span class="trend-icon">{{ getTrendIcon(metric.trend) }}</span>
                </div>
              </div>
            </div>
            <div class="metrics-actions">
              <button class="btn btn-primary" @click="showUpdateMetrics = true">更新指标数据</button>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="detail-actions">
            <button class="btn btn-secondary" @click="editCampaign(selectedCampaign)">编辑</button>
            <button class="btn btn-primary" @click="generateReviewReport">生成复盘报告</button>
            <select v-model="statusToUpdate" class="status-select">
              <option value="draft">草稿</option>
              <option value="planning">规划中</option>
              <option value="active">进行中</option>
              <option value="completed">已完成</option>
              <option value="cancelled">已取消</option>
            </select>
            <button class="btn btn-secondary" @click="updateCampaignStatus(selectedCampaign.id, statusToUpdate)">更新状态</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 更新指标模态框 -->
    <div v-if="showUpdateMetrics" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>更新指标数据</h2>
          <button class="btn-close" @click="showUpdateMetrics = false">×</button>
        </div>
        <div class="modal-body">
          <div v-for="(metric, index) in selectedCampaign.metrics" :key="index" class="metric-update-item">
            <label>{{ metric.name }}</label>
            <input v-model.number="metricUpdateData[index].actual" type="number" :placeholder="'当前：' + metric.actual" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showUpdateMetrics = false">取消</button>
          <button class="btn btn-primary" @click="submitMetricsUpdate">保存</button>
        </div>
      </div>
    </div>

    <!-- 复盘报告面板 -->
    <div v-if="reviewReport" class="panel-overlay">
      <div class="panel panel-wide">
        <div class="panel-header">
          <h2>📊 活动复盘报告</h2>
          <button class="btn-close" @click="reviewReport = null">×</button>
        </div>
        <div class="panel-content">
          <div class="report-header">
            <h3>{{ reviewReport.campaign_name }}</h3>
            <p>{{ reviewReport.period }}</p>
          </div>
          
          <div class="report-summary">
            <div class="summary-card">
              <div class="summary-value">{{ reviewReport.summary.overall_progress }}%</div>
              <div class="summary-label">整体达成率</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ reviewReport.summary.health_score }}</div>
              <div class="summary-label">健康度评分</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">¥{{ (reviewReport.summary.budget_total / 10000).toFixed(1) }}万</div>
              <div class="summary-label">实际花费</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ reviewReport.summary.estimated_roi.toFixed(1) }}</div>
              <div class="summary-label">ROI</div>
            </div>
          </div>

          <div class="report-section">
            <h3>✅ 亮点</h3>
            <ul>
              <li v-for="highlight in reviewReport.highlights" :key="highlight">✓ {{ highlight }}</li>
            </ul>
          </div>

          <div class="report-section">
            <h3>⚠️ 待改进</h3>
            <ul>
              <li v-for="improvement in reviewReport.improvements" :key="improvement">⚠ {{ improvement }}</li>
            </ul>
          </div>

          <div class="report-section">
            <h3>💡 建议</h3>
            <ul>
              <li v-for="rec in reviewReport.recommendations" :key="rec">💡 {{ rec }}</li>
            </ul>
          </div>

          <div class="report-actions">
            <button class="btn btn-primary" @click="exportReport">导出报告</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignCard from '../components/CampaignCard.vue'

export default {
  name: 'Campaign',
  components: {
    CampaignCard
  },
  data() {
    return {
      campaigns: [],
      templates: [],
      caseStudies: [],
      stats: null,
      filterStatus: '',
      showTemplates: false,
      showCases: false,
      showCreateModal: false,
      showBudgetEditor: false,
      showMetricsEditor: false,
      showUpdateMetrics: false,
      selectedCampaign: null,
      reviewReport: null,
      statusToUpdate: 'draft',
      caseSearch: '',
      newCampaign: {
        name: '',
        description: '',
        campaign_type: 'promotion',
        status: 'draft',
        start_date: '',
        end_date: '',
        budget_items: [],
        timeline: [],
        metrics: [],
        notes: '',
        tags: [],
        tagsInput: ''
      },
      metricUpdateData: []
    }
  },
  computed: {
    filteredCampaigns() {
      if (!this.filterStatus) return this.campaigns
      return this.campaigns.filter(c => c.status === this.filterStatus)
    },
    displayedCases() {
      return this.caseStudies
    },
    calculateBudgetTotal() {
      const total = this.newCampaign.budget_items.reduce((sum, item) => sum + (item.planned || 0), 0)
      return { planned: total }
    }
  },
  mounted() {
    this.loadCampaigns()
    this.loadTemplates()
    this.loadCaseStudies()
    this.loadStats()
  },
  methods: {
    // API 调用
    async loadCampaigns() {
      try {
        const res = await fetch('/api/campaigns')
        const data = await res.json()
        this.campaigns = data
      } catch (error) {
        console.error('加载活动失败:', error)
      }
    },
    async loadTemplates() {
      try {
        const res = await fetch('/api/campaigns/templates')
        const data = await res.json()
        this.templates = data
      } catch (error) {
        console.error('加载模板失败:', error)
      }
    },
    async loadCaseStudies() {
      try {
        const res = await fetch('/api/campaigns/cases')
        const data = await res.json()
        this.caseStudies = data
      } catch (error) {
        console.error('加载案例失败:', error)
      }
    },
    async loadStats() {
      try {
        const res = await fetch('/api/campaigns/stats/overview')
        const data = await res.json()
        this.stats = data
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },
    
    // 创建活动
    createFromTemplate(template) {
      this.newCampaign = {
        name: '',
        description: '',
        campaign_type: template.campaign_type,
        status: 'draft',
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        budget_items: [],
        timeline: [],
        metrics: template.key_metrics.map(m => ({ name: m, target: 0, actual: 0, unit: '' })),
        notes: '',
        tags: [],
        tagsInput: ''
      }
      this.showTemplates = false
      this.showCreateModal = true
    },
    async createCampaign() {
      try {
        const payload = {
          ...this.newCampaign,
          tags: this.newCampaign.tagsInput.split(',').map(t => t.trim()).filter(t => t)
        }
        const res = await fetch('/api/campaigns', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (data.success) {
          this.loadCampaigns()
          this.showCreateModal = false
          this.resetNewCampaign()
        }
      } catch (error) {
        console.error('创建活动失败:', error)
      }
    },
    resetNewCampaign() {
      this.newCampaign = {
        name: '',
        description: '',
        campaign_type: 'promotion',
        status: 'draft',
        start_date: '',
        end_date: '',
        budget_items: [],
        timeline: [],
        metrics: [],
        notes: '',
        tags: [],
        tagsInput: ''
      }
    },
    
    // 预算和指标编辑
    addBudgetItem() {
      this.newCampaign.budget_items.push({ category: '', planned: 0, actual: 0, description: '' })
    },
    removeBudgetItem(index) {
      this.newCampaign.budget_items.splice(index, 1)
    },
    addMetric() {
      this.newCampaign.metrics.push({ name: '', target: 0, actual: 0, unit: '' })
    },
    removeMetric(index) {
      this.newCampaign.metrics.splice(index, 1)
    },
    
    // 时间规划生成
    async generateTimeline() {
      if (!this.newCampaign.start_date || !this.newCampaign.end_date) {
        alert('请先设置开始和结束日期')
        return
      }
      const startDate = new Date(this.newCampaign.start_date)
      const endDate = new Date(this.newCampaign.end_date)
      const durationDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
      
      try {
        const res = await fetch('/api/campaigns/timeline/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            campaign_type: this.newCampaign.campaign_type,
            start_date: this.newCampaign.start_date,
            duration_days: durationDays
          })
        })
        const data = await res.json()
        this.newCampaign.timeline = data
        alert('时间规划已生成')
      } catch (error) {
        console.error('生成时间规划失败:', error)
      }
    },
    
    // 活动操作
    viewCampaign(campaign) {
      this.selectedCampaign = campaign
    },
    editCampaign(campaign) {
      this.newCampaign = { ...campaign, tagsInput: campaign.tags?.join(', ') || '' }
      this.showCreateModal = true
    },
    async deleteCampaign(id) {
      if (!confirm('确定要删除这个活动吗？')) return
      try {
        await fetch(`/api/campaigns/${id}`, { method: 'DELETE' })
        this.loadCampaigns()
      } catch (error) {
        console.error('删除活动失败:', error)
      }
    },
    async updateCampaignStatus(id, status) {
      try {
        await fetch(`/api/campaigns/${id}/status?status=${status}`, { method: 'PATCH' })
        this.loadCampaigns()
        if (this.selectedCampaign) {
          this.selectedCampaign.status = status
        }
      } catch (error) {
        console.error('更新状态失败:', error)
      }
    },
    
    // 指标更新
    async submitMetricsUpdate() {
      if (!this.selectedCampaign) return
      try {
        const metrics = this.selectedCampaign.metrics.map((m, i) => ({
          ...m,
          actual: this.metricUpdateData[i]?.actual || m.actual
        }))
        await fetch(`/api/campaigns/${this.selectedCampaign.id}/metrics`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ metrics })
        })
        this.showUpdateMetrics = false
        this.loadCampaigns()
      } catch (error) {
        console.error('更新指标失败:', error)
      }
    },
    
    // 复盘报告
    async generateReviewReport() {
      if (!this.selectedCampaign) return
      try {
        const res = await fetch(`/api/campaigns/${this.selectedCampaign.id}/review`)
        const data = await res.json()
        this.reviewReport = data
      } catch (error) {
        console.error('生成复盘报告失败:', error)
      }
    },
    exportReport() {
      // 导出报告逻辑
      alert('报告导出功能开发中...')
    },
    
    // 案例搜索
    async searchCases() {
      if (!this.caseSearch) return
      try {
        const res = await fetch(`/api/campaigns/cases/search?keywords=${encodeURIComponent(this.caseSearch)}`)
        const data = await res.json()
        this.caseStudies = data
      } catch (error) {
        console.error('搜索案例失败:', error)
      }
    },
    
    // 工具函数
    getTemplateTypeName(type) {
      const names = {
        product_launch: '产品发布',
        promotion: '促销活动',
        brand_awareness: '品牌宣传',
        user_acquisition: '用户获取',
        retention: '用户留存',
        seasonal: '季节性活动'
      }
      return names[type] || type
    },
    getCampaignTypeName(type) {
      return this.getTemplateTypeName(type)
    },
    getStatusName(status) {
      const names = {
        draft: '草稿',
        planning: '规划中',
        active: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return names[status] || status
    },
    getTrendIcon(trend) {
      const icons = { up: '📈', stable: '➡️', down: '📉' }
      return icons[trend] || '➡️'
    },
    formatResultValue(key, value) {
      if (typeof value === 'number') {
        if (value > 10000) return (value / 10000).toFixed(1) + '万'
        return value.toFixed(0)
      }
      return value
    },
    onTypeChange() {
      // 类型变化时重置指标
      const template = this.templates.find(t => t.campaign_type === this.newCampaign.campaign_type)
      if (template) {
        this.newCampaign.metrics = template.key_metrics.map(m => ({ name: m, target: 0, actual: 0, unit: '' }))
      }
    }
  }
}
</script>

<style scoped>
.campaign-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #1a1a1a;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #4f46e5;
  color: white;
}

.btn-primary:hover {
  background: #4338ca;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

.btn-block {
  width: 100%;
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #4f46e5;
}

.stat-label {
  color: #6b7280;
  margin-top: 5px;
}

/* 活动列表 */
.campaign-list {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h2 {
  font-size: 20px;
  color: #1a1a1a;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.campaigns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

/* 面板 */
.panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: flex-end;
  z-index: 1000;
}

.panel {
  background: white;
  width: 600px;
  max-height: 100vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
}

.panel-wide {
  width: 900px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h2 {
  font-size: 20px;
  color: #1a1a1a;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.panel-content {
  padding: 20px;
}

/* 模板卡片 */
.template-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.template-header h3 {
  font-size: 18px;
  color: #1a1a1a;
}

.template-type {
  background: #e0e7ff;
  color: #4f46e5;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.template-desc {
  color: #6b7280;
  margin-bottom: 15px;
}

.template-info {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item .label {
  font-size: 12px;
  color: #9ca3af;
}

.info-item .value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

.template-section {
  margin-bottom: 15px;
}

.template-section h4 {
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #f3f4f6;
  color: #374151;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.checklist {
  list-style: none;
  padding: 0;
  margin: 0;
}

.checklist li {
  color: #6b7280;
  font-size: 13px;
  padding: 4px 0;
}

/* 案例卡片 */
.case-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.case-header h3 {
  font-size: 18px;
  color: #1a1a1a;
}

.case-industry {
  background: #d1fae5;
  color: #059669;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.case-desc {
  color: #6b7280;
  margin-bottom: 15px;
}

.case-results {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.result-item {
  background: #f9fafb;
  padding: 10px;
  border-radius: 6px;
}

.result-label {
  font-size: 12px;
  color: #9ca3af;
  display: block;
}

.result-value {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 600;
}

.case-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  padding: 15px 0;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}

.case-stats .stat {
  text-align: center;
}

.case-stats .stat-label {
  font-size: 12px;
  color: #9ca3af;
  display: block;
}

.case-stats .stat-value {
  font-size: 18px;
  color: #4f46e5;
  font-weight: 600;
}

.case-learnings h4 {
  font-size: 14px;
  color: #374151;
  margin-bottom: 10px;
}

.case-learnings ul {
  padding-left: 20px;
}

.case-learnings li {
  color: #6b7280;
  font-size: 13px;
  padding: 4px 0;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar input {
  flex: 1;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

/* 模态框 */
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
  background: white;
  border-radius: 12px;
  width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 20px;
  color: #1a1a1a;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

/* 表单 */
.campaign-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-actions {
  display: flex;
  gap: 10px;
}

/* 预算和指标编辑 */
.budget-item,
.metric-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.metric-update-item {
  margin-bottom: 15px;
}

.metric-update-item label {
  display: block;
  margin-bottom: 5px;
  color: #374151;
}

.metric-update-item input {
  width: 100%;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.budget-summary {
  margin-top: 20px;
  padding: 15px;
  background: #f9fafb;
  border-radius: 6px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
}

.summary-row .total {
  font-weight: bold;
  color: #4f46e5;
}

/* 活动详情 */
.detail-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h3 {
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.description {
  color: #6b7280;
  line-height: 1.6;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.draft {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.planning {
  background: #dbeafe;
  color: #2563eb;
}

.status-badge.active {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.completed {
  background: #d1fae5;
  color: #059669;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #dc2626;
}

/* 时间线 */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.timeline-phase {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #d1d5db;
}

.timeline-phase.completed {
  border-left-color: #059669;
}

.timeline-phase.in_progress {
  border-left-color: #d97706;
}

.timeline-phase.pending {
  border-left-color: #d1d5db;
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.phase-header h4 {
  font-size: 15px;
  color: #1a1a1a;
}

.phase-dates {
  font-size: 12px;
  color: #9ca3af;
}

.phase-tasks {
  list-style: disc;
  padding-left: 20px;
  color: #6b7280;
  font-size: 13px;
}

.phase-tasks li {
  padding: 3px 0;
}

/* 数据表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
}

.data-table td {
  color: #1a1a1a;
  font-size: 14px;
}

/* 指标卡片 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.metric-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 15px;
}

.metric-card.up {
  border-color: #059669;
  background: #f0fdf4;
}

.metric-card.stable {
  border-color: #d1d5db;
}

.metric-card.down {
  border-color: #ef4444;
  background: #fef2f2;
}

.metric-name {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.metric-values {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}

.metric-values .actual {
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a;
}

.metric-values .target {
  font-size: 12px;
  color: #9ca3af;
}

.metric-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4f46e5;
  transition: width 0.3s;
}

.trend-icon {
  font-size: 16px;
}

.metrics-actions {
  margin-top: 15px;
}

.detail-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.status-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

/* 复盘报告 */
.report-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border-radius: 12px;
  color: white;
}

.report-header h3 {
  font-size: 24px;
  margin-bottom: 5px;
}

.report-header p {
  opacity: 0.9;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.summary-card {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #4f46e5;
}

.summary-label {
  color: #6b7280;
  margin-top: 5px;
  font-size: 13px;
}

.report-section {
  margin-bottom: 25px;
}

.report-section h3 {
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 15px;
}

.report-section ul {
  list-style: none;
  padding: 0;
}

.report-section li {
  padding: 8px 0;
  color: #6b7280;
  font-size: 14px;
}

.report-actions {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}
</style>
