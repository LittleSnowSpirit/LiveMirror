<template>
  <div class="campaign-card" :class="statusClass">
    <div class="card-header">
      <div class="card-title">
        <h3>{{ campaign.name }}</h3>
        <span class="status-badge" :class="campaign.status">
          {{ getStatusName(campaign.status) }}
        </span>
      </div>
      <div class="card-actions">
        <button class="action-btn" @click="$emit('view', campaign)" title="查看">
          👁️
        </button>
        <button class="action-btn" @click="$emit('edit', campaign)" title="编辑">
          ✏️
        </button>
        <button class="action-btn delete" @click="$emit('delete', campaign.id)" title="删除">
          🗑️
        </button>
      </div>
    </div>

    <div class="card-body">
      <p class="description">{{ campaign.description || '暂无描述' }}</p>

      <div class="info-row">
        <span class="info-label">类型</span>
        <span class="info-value">{{ getCampaignTypeName(campaign.campaign_type) }}</span>
      </div>

      <div class="info-row">
        <span class="info-label">时间</span>
        <span class="info-value">{{ campaign.start_date }} 至 {{ campaign.end_date }}</span>
      </div>

      <!-- 进度条 -->
      <div class="progress-section" v-if="showProgress">
        <div class="progress-label">
          <span>整体进度</span>
          <span class="progress-percent">{{ progress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- 预算概览 -->
      <div class="budget-overview" v-if="campaign.budget_items && campaign.budget_items.length > 0">
        <div class="budget-item-mini">
          <span class="budget-label">预算</span>
          <span class="budget-value">¥{{ formatBudget(calculateBudget.planned) }}</span>
        </div>
        <div class="budget-item-mini">
          <span class="budget-label">已用</span>
          <span class="budget-value">¥{{ formatBudget(calculateBudget.actual) }}</span>
        </div>
      </div>

      <!-- 核心指标 -->
      <div class="metrics-preview" v-if="campaign.metrics && campaign.metrics.length > 0">
        <div class="metric-tag" v-for="metric in campaign.metrics.slice(0, 3)" :key="metric.name" :class="metric.trend">
          <span class="metric-name">{{ metric.name }}</span>
          <span class="metric-value">{{ metric.actual }}/{{ metric.target }}</span>
        </div>
        <div v-if="campaign.metrics.length > 3" class="more-metrics">
          +{{ campaign.metrics.length - 3 }}
        </div>
      </div>

      <!-- 标签 -->
      <div class="tags" v-if="campaign.tags && campaign.tags.length > 0">
        <span v-for="tag in campaign.tags" :key="tag" class="tag">
          {{ tag }}
        </span>
      </div>
    </div>

    <div class="card-footer">
      <div class="footer-actions">
        <select v-model="selectedStatus" class="status-select" @change="updateStatus">
          <option value="draft">草稿</option>
          <option value="planning">规划中</option>
          <option value="active">进行中</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
        <button class="btn btn-outline" @click="$emit('view', campaign)">
          查看详情
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CampaignCard',
  props: {
    campaign: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      selectedStatus: this.campaign.status
    }
  },
  computed: {
    statusClass() {
      return `status-${this.campaign.status}`
    },
    showProgress() {
      return this.campaign.metrics && this.campaign.metrics.length > 0
    },
    progress() {
      if (!this.campaign.metrics || this.campaign.metrics.length === 0) return 0
      const total = this.campaign.metrics.reduce((sum, m) => {
        if (m.target === 0) return sum
        return sum + Math.min((m.actual / m.target) * 100, 100)
      }, 0)
      return Math.round(total / this.campaign.metrics.length)
    },
    calculateBudget() {
      const planned = this.campaign.budget_items?.reduce((sum, item) => sum + (item.planned || 0), 0) || 0
      const actual = this.campaign.budget_items?.reduce((sum, item) => sum + (item.actual || 0), 0) || 0
      return { planned, actual }
    }
  },
  watch: {
    campaign: {
      immediate: true,
      handler(newVal) {
        this.selectedStatus = newVal.status
      }
    }
  },
  methods: {
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
    getCampaignTypeName(type) {
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
    formatBudget(amount) {
      if (amount >= 10000) {
        return (amount / 10000).toFixed(1) + '万'
      }
      return amount.toFixed(0)
    },
    updateStatus() {
      this.$emit('update-status', this.campaign.id, this.selectedStatus)
    }
  }
}
</script>

<style scoped>
.campaign-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: all 0.2s;
  border: 2px solid transparent;
}

.campaign-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.campaign-card.status-draft {
  border-color: #e5e7eb;
}

.campaign-card.status-planning {
  border-color: #93c5fd;
}

.campaign-card.status-active {
  border-color: #fcd34d;
}

.campaign-card.status-completed {
  border-color: #6ee7b7;
}

.campaign-card.status-cancelled {
  border-color: #fca5a5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 16px 0;
}

.card-title {
  flex: 1;
}

.card-title h3 {
  font-size: 18px;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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

.card-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 16px;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.card-body {
  padding: 16px;
}

.description {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.info-label {
  color: #9ca3af;
}

.info-value {
  color: #374151;
  font-weight: 500;
}

/* 进度条 */
.progress-section {
  margin: 16px 0;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 6px;
}

.progress-percent {
  font-weight: 600;
  color: #4f46e5;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  transition: width 0.3s;
}

/* 预算概览 */
.budget-overview {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 12px;
}

.budget-item-mini {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.budget-label {
  font-size: 12px;
  color: #9ca3af;
}

.budget-value {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

/* 指标预览 */
.metrics-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.metric-tag {
  display: flex;
  flex-direction: column;
  padding: 8px 10px;
  background: #f9fafb;
  border-radius: 6px;
  min-width: 80px;
}

.metric-tag.up {
  background: #f0fdf4;
  border-left: 2px solid #059669;
}

.metric-tag.stable {
  background: #f9fafb;
  border-left: 2px solid #d1d5db;
}

.metric-tag.down {
  background: #fef2f2;
  border-left: 2px solid #ef4444;
}

.metric-name {
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
}

.more-metrics {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 10px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 12px;
  color: #6b7280;
}

/* 标签 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
}

/* 卡片底部 */
.card-footer {
  padding: 12px 16px;
  border-top: 1px solid #f3f4f6;
}

.footer-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.status-select {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  background: white;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-outline:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}
</style>
