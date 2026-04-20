<template>
  <div class="ticket-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>📋 客服工单管理</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        + 新建工单
      </button>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-toolbar">
      <div class="filter-group">
        <label>状态:</label>
        <select v-model="filters.status">
          <option value="">全部</option>
          <option value="new">新建</option>
          <option value="assigned">已分配</option>
          <option value="in_progress">处理中</option>
          <option value="pending">待回复</option>
          <option value="resolved">已解决</option>
          <option value="closed">已关闭</option>
        </select>
      </div>

      <div class="filter-group">
        <label>分类:</label>
        <select v-model="filters.category">
          <option value="">全部</option>
          <option value="technical">技术问题</option>
          <option value="billing">账单问题</option>
          <option value="account">账户问题</option>
          <option value="feature">功能建议</option>
          <option value="bug">Bug 报告</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div class="filter-group">
        <label>优先级:</label>
        <select v-model="filters.priority">
          <option value="">全部</option>
          <option value="low">低</option>
          <option value="medium">中</option>
          <option value="high">高</option>
          <option value="urgent">紧急</option>
        </select>
      </div>

      <button class="btn btn-secondary" @click="loadTickets">刷新</button>
    </div>

    <!-- 工单列表 -->
    <div class="ticket-list">
      <TicketCard
        v-for="ticket in tickets"
        :key="ticket.id"
        :ticket="ticket"
        @view="viewTicket"
        @assign="assignTicket"
        @update-status="updateTicketStatus"
      />

      <div v-if="tickets.length === 0" class="empty-state">
        <p>暂无工单</p>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > limit">
      <button :disabled="offset === 0" @click="changePage(-1)">上一页</button>
      <span>{{ offset + 1 }} - {{ Math.min(offset + limit, total) }} / {{ total }}</span>
      <button :disabled="offset + limit >= total" @click="changePage(1)">下一页</button>
    </div>

    <!-- 新建工单弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>新建工单</h2>
        <form @submit.prevent="createTicket">
          <div class="form-group">
            <label>标题 *</label>
            <input v-model="newTicket.title" type="text" required maxlength="200" />
          </div>

          <div class="form-group">
            <label>描述 *</label>
            <textarea v-model="newTicket.description" rows="4" required maxlength="5000"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>分类 *</label>
              <select v-model="newTicket.category" required>
                <option value="technical">技术问题</option>
                <option value="billing">账单问题</option>
                <option value="account">账户问题</option>
                <option value="feature">功能建议</option>
                <option value="bug">Bug 报告</option>
                <option value="other">其他</option>
              </select>
            </div>

            <div class="form-group">
              <label>优先级</label>
              <select v-model="newTicket.priority">
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
                <option value="urgent">紧急</option>
              </select>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 工单详情弹窗 -->
    <div v-if="selectedTicket" class="modal-overlay" @click.self="selectedTicket = null">
      <div class="modal modal-large">
        <h2>工单详情</h2>
        
        <div class="ticket-detail">
          <div class="ticket-header">
            <h3>{{ selectedTicket.title }}</h3>
            <div class="ticket-meta">
              <span class="badge" :class="selectedTicket.priority">
                {{ priorityLabel(selectedTicket.priority) }}
              </span>
              <span class="badge" :class="selectedTicket.status">
                {{ statusLabel(selectedTicket.status) }}
              </span>
            </div>
          </div>

          <div class="ticket-info">
            <p><strong>ID:</strong> {{ selectedTicket.id }}</p>
            <p><strong>分类:</strong> {{ categoryLabel(selectedTicket.category) }}</p>
            <p><strong>创建时间:</strong> {{ formatDate(selectedTicket.created_at) }}</p>
            <p><strong>创建人:</strong> {{ selectedTicket.creator_id }}</p>
            <p v-if="selectedTicket.assignee_id"><strong>指派人:</strong> {{ selectedTicket.assignee_id }}</p>
          </div>

          <div class="ticket-description">
            <h4>描述</h4>
            <p>{{ selectedTicket.description }}</p>
          </div>

          <!-- 消息历史 -->
          <div class="ticket-messages">
            <h4>消息历史</h4>
            <div class="messages-list">
              <div
                v-for="msg in selectedTicket.messages"
                :key="msg.id"
                class="message"
                :class="{ internal: msg.is_internal }"
              >
                <div class="message-header">
                  <span class="sender">{{ msg.sender_id }}</span>
                  <span class="time">{{ formatTime(msg.created_at) }}</span>
                  <span v-if="msg.is_internal" class="internal-badge">内部</span>
                </div>
                <div class="message-content">{{ msg.content }}</div>
              </div>
            </div>

            <!-- 回复输入 -->
            <div class="message-input">
              <textarea v-model="newMessage" rows="3" placeholder="输入回复内容..."></textarea>
              <div class="message-actions">
                <label>
                  <input type="checkbox" v-model="isInternalMessage" />
                  内部备注（客户不可见）
                </label>
                <button class="btn btn-primary" @click="sendMessage" :disabled="!newMessage.trim()">
                  发送
                </button>
              </div>
            </div>
          </div>

          <!-- 状态操作 -->
          <div class="ticket-actions">
            <h4>操作</h4>
            <div class="action-buttons">
              <button class="btn btn-secondary" @click="changeStatus('in_progress')">开始处理</button>
              <button class="btn btn-secondary" @click="changeStatus('pending')">设为待回复</button>
              <button class="btn btn-success" @click="changeStatus('resolved')">标记为已解决</button>
              <button class="btn btn-secondary" @click="changeStatus('closed')">关闭工单</button>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" @click="selectedTicket = null">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TicketCard from '../components/TicketCard.vue'

export default {
  name: 'TicketPage',
  components: {
    TicketCard
  },
  data() {
    return {
      tickets: [],
      total: 0,
      limit: 20,
      offset: 0,
      filters: {
        status: '',
        category: '',
        priority: ''
      },
      stats: [],
      showCreateModal: false,
      selectedTicket: null,
      creating: false,
      newTicket: {
        title: '',
        description: '',
        category: 'technical',
        priority: 'medium'
      },
      newMessage: '',
      isInternalMessage: false
    }
  },
  async mounted() {
    await this.loadStatistics()
    await this.loadTickets()
  },
  methods: {
    async loadTickets() {
      try {
        const params = new URLSearchParams({
          limit: this.limit,
          offset: this.offset
        })
        
        if (this.filters.status) params.append('status', this.filters.status)
        if (this.filters.category) params.append('category', this.filters.category)
        if (this.filters.priority) params.append('priority', this.filters.priority)

        const response = await fetch(`/api/tickets?${params}`)
        const data = await response.json()
        
        this.tickets = data.tickets
        this.total = data.total
      } catch (error) {
        console.error('加载工单失败:', error)
      }
    },

    async loadStatistics() {
      try {
        const response = await fetch('/api/tickets/statistics')
        const data = await response.json()
        
        this.stats = [
          { label: '总工单数', value: data.total },
          { label: '待处理', value: data.by_status.new + data.by_status.assigned },
          { label: '处理中', value: data.by_status.in_progress },
          { label: '已解决', value: data.resolved_count },
          { label: '平均解决时间', value: `${data.avg_resolution_hours}h` }
        ]
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },

    async createTicket() {
      this.creating = true
      try {
        const response = await fetch('/api/tickets', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newTicket)
        })
        
        if (response.ok) {
          this.showCreateModal = false
          this.newTicket = {
            title: '',
            description: '',
            category: 'technical',
            priority: 'medium'
          }
          await this.loadTickets()
          await this.loadStatistics()
        }
      } catch (error) {
        console.error('创建工单失败:', error)
      } finally {
        this.creating = false
      }
    },

    viewTicket(ticket) {
      this.selectedTicket = ticket
    },

    async assignTicket(ticketId, assigneeId) {
      try {
        const response = await fetch(`/api/tickets/${ticketId}/assign`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ assignee_id: assigneeId })
        })
        
        if (response.ok) {
          await this.loadTickets()
        }
      } catch (error) {
        console.error('分配工单失败:', error)
      }
    },

    async updateTicketStatus(ticketId, status) {
      try {
        const response = await fetch(`/api/tickets/${ticketId}/status`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status })
        })
        
        if (response.ok) {
          await this.loadTickets()
          if (this.selectedTicket && this.selectedTicket.id === ticketId) {
            const updated = await response.json()
            this.selectedTicket = updated
          }
        }
      } catch (error) {
        console.error('更新状态失败:', error)
      }
    },

    async changeStatus(status) {
      if (this.selectedTicket) {
        await this.updateTicketStatus(this.selectedTicket.id, status)
      }
    },

    async sendMessage() {
      if (!this.newMessage.trim() || !this.selectedTicket) return
      
      try {
        const response = await fetch(`/api/tickets/${this.selectedTicket.id}/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: this.newMessage,
            is_internal: this.isInternalMessage
          })
        })
        
        if (response.ok) {
          this.newMessage = ''
          this.isInternalMessage = false
          const updated = await response.json()
          this.selectedTicket = updated
        }
      } catch (error) {
        console.error('发送消息失败:', error)
      }
    },

    changePage(delta) {
      this.offset += delta * this.limit
      if (this.offset < 0) this.offset = 0
      this.loadTickets()
    },

    priorityLabel(priority) {
      const labels = {
        low: '低',
        medium: '中',
        high: '高',
        urgent: '紧急'
      }
      return labels[priority] || priority
    },

    statusLabel(status) {
      const labels = {
        new: '新建',
        assigned: '已分配',
        in_progress: '处理中',
        pending: '待回复',
        resolved: '已解决',
        closed: '已关闭'
      }
      return labels[status] || status
    },

    categoryLabel(category) {
      const labels = {
        technical: '技术问题',
        billing: '账单问题',
        account: '账户问题',
        feature: '功能建议',
        bug: 'Bug 报告',
        other: '其他'
      }
      return labels[category] || category
    },

    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString('zh-CN')
    },

    formatTime(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  },
  watch: {
    'filters.status'() {
      this.offset = 0
      this.loadTickets()
    },
    'filters.category'() {
      this.offset = 0
      this.loadTickets()
    },
    'filters.priority'() {
      this.offset = 0
      this.loadTickets()
    }
  }
}
</script>

<style scoped>
.ticket-page {
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

/* 筛选工具栏 */
.filter-toolbar {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
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

/* 工单列表 */
.ticket-list {
  display: grid;
  gap: 15px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
  padding: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
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

.btn-success {
  background: #52c41a;
  color: #fff;
}

.btn-success:hover {
  background: #73d13d;
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
  max-width: 800px;
}

.modal h2 {
  margin: 0 0 20px 0;
}

/* 表单 */
.form-group {
  margin-bottom: 15px;
  flex: 1;
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

.form-row {
  display: flex;
  gap: 15px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 工单详情 */
.ticket-detail {
  margin-bottom: 20px;
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.ticket-meta {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge.urgent { background: #ff4d4f; color: #fff; }
.badge.high { background: #fa8c16; color: #fff; }
.badge.medium { background: #1890ff; color: #fff; }
.badge.low { background: #52c41a; color: #fff; }

.badge.new { background: #1890ff; color: #fff; }
.badge.assigned { background: #722ed1; color: #fff; }
.badge.in_progress { background: #fa8c16; color: #fff; }
.badge.pending { background: #13c2c2; color: #fff; }
.badge.resolved { background: #52c41a; color: #fff; }
.badge.closed { background: #8c8c8c; color: #fff; }

.ticket-info {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.ticket-info p {
  margin: 5px 0;
  font-size: 14px;
}

.ticket-description {
  margin-bottom: 15px;
}

.ticket-description h4 {
  margin: 0 0 10px 0;
}

/* 消息列表 */
.ticket-messages {
  margin-bottom: 15px;
}

.messages-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 15px;
}

.message {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.message.internal {
  background: #fff7e6;
  border-left: 3px solid #fa8c16;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 12px;
}

.sender {
  font-weight: bold;
}

.time {
  color: #999;
}

.internal-badge {
  background: #fa8c16;
  color: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
}

.message-input {
  margin-top: 15px;
}

.message-input textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

.message-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.ticket-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
