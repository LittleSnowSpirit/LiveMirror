<template>
  <div class="ticket-card" :class="priorityClass">
    <div class="card-header">
      <div class="ticket-title">
        <h3>{{ ticket.title }}</h3>
        <div class="ticket-id">#{{ shortId }}</div>
      </div>
      <div class="ticket-badges">
        <span class="badge priority" :class="ticket.priority">
          {{ priorityLabel }}
        </span>
        <span class="badge status" :class="ticket.status">
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <div class="card-body">
      <div class="ticket-description">
        {{ truncatedDescription }}
      </div>

      <div class="ticket-meta">
        <div class="meta-item">
          <span class="meta-label">分类</span>
          <span class="meta-value">{{ categoryLabel }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">创建时间</span>
          <span class="meta-value">{{ createdDate }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">消息</span>
          <span class="meta-value">{{ ticket.messages.length }}</span>
        </div>
        <div class="meta-item" v-if="ticket.assignee_id">
          <span class="meta-label">指派人</span>
          <span class="meta-value">{{ ticket.assignee_id }}</span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <div class="footer-actions">
        <button class="btn btn-view" @click="$emit('view', ticket)">
          👁 查看
        </button>
        
        <div class="quick-actions" v-if="showQuickActions">
          <select v-model="selectedAssignee" @change="handleAssign">
            <option value="">分配给...</option>
            <option value="agent_001">客服 A</option>
            <option value="agent_002">客服 B</option>
            <option value="agent_003">客服 C</option>
          </select>
          
          <select v-model="selectedStatus" @change="handleStatusChange">
            <option value="">变更状态...</option>
            <option value="assigned">已分配</option>
            <option value="in_progress">处理中</option>
            <option value="pending">待回复</option>
            <option value="resolved">已解决</option>
            <option value="closed">已关闭</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TicketCard',
  props: {
    ticket: {
      type: Object,
      required: true
    },
    showQuickActions: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      selectedAssignee: '',
      selectedStatus: ''
    }
  },
  computed: {
    shortId() {
      return this.ticket.id.split('-')[0]
    },
    priorityClass() {
      return `priority-${this.ticket.priority}`
    },
    priorityLabel() {
      const labels = {
        low: '低',
        medium: '中',
        high: '高',
        urgent: '紧急'
      }
      return labels[this.ticket.priority] || this.ticket.priority
    },
    statusLabel() {
      const labels = {
        new: '新建',
        assigned: '已分配',
        in_progress: '处理中',
        pending: '待回复',
        resolved: '已解决',
        closed: '已关闭'
      }
      return labels[this.ticket.status] || this.ticket.status
    },
    categoryLabel() {
      const labels = {
        technical: '技术问题',
        billing: '账单问题',
        account: '账户问题',
        feature: '功能建议',
        bug: 'Bug 报告',
        other: '其他'
      }
      return labels[this.ticket.category] || this.ticket.category
    },
    truncatedDescription() {
      const desc = this.ticket.description
      return desc.length > 100 ? desc.substring(0, 100) + '...' : desc
    },
    createdDate() {
      return new Date(this.ticket.created_at).toLocaleDateString('zh-CN')
    }
  },
  methods: {
    handleAssign(event) {
      if (this.selectedAssignee) {
        this.$emit('assign', this.ticket.id, this.selectedAssignee)
        this.selectedAssignee = ''
      }
    },
    handleStatusChange(event) {
      if (this.selectedStatus) {
        this.$emit('update-status', this.ticket.id, this.selectedStatus)
        this.selectedStatus = ''
      }
    }
  }
}
</script>

<style scoped>
.ticket-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: all 0.3s;
  border-left: 4px solid #1890ff;
}

.ticket-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

/* 优先级边框颜色 */
.ticket-card.priority-urgent {
  border-left-color: #ff4d4f;
}

.ticket-card.priority-high {
  border-left-color: #fa8c16;
}

.ticket-card.priority-medium {
  border-left-color: #1890ff;
}

.ticket-card.priority-low {
  border-left-color: #52c41a;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.ticket-title {
  flex: 1;
}

.ticket-title h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.ticket-id {
  font-size: 12px;
  color: #999;
}

.ticket-badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* 优先级徽章 */
.badge.priority.urgent {
  background: #ff4d4f;
  color: #fff;
}

.badge.priority.high {
  background: #fa8c16;
  color: #fff;
}

.badge.priority.medium {
  background: #1890ff;
  color: #fff;
}

.badge.priority.low {
  background: #52c41a;
  color: #fff;
}

/* 状态徽章 */
.badge.status.new {
  background: #1890ff;
  color: #fff;
}

.badge.status.assigned {
  background: #722ed1;
  color: #fff;
}

.badge.status.in_progress {
  background: #fa8c16;
  color: #fff;
}

.badge.status.pending {
  background: #13c2c2;
  color: #fff;
}

.badge.status.resolved {
  background: #52c41a;
  color: #fff;
}

.badge.status.closed {
  background: #8c8c8c;
  color: #fff;
}

.card-body {
  padding: 16px;
}

.ticket-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
}

.ticket-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
}

.meta-value {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.card-footer {
  padding: 12px 16px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-view {
  padding: 6px 12px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view:hover {
  background: #40a9ff;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.quick-actions select {
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  background: #fff;
  cursor: pointer;
}

.quick-actions select:hover {
  border-color: #1890ff;
}
</style>
