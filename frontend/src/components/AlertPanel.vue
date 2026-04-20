<template>
  <div class="alert-panel">
    <!-- 提醒铃铛图标 -->
    <div class="alert-bell" @click="togglePanel">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }}</span>
    </div>
    
    <!-- 提醒面板 -->
    <div v-show="panelOpen" class="panel-content">
      <!-- 面板头部 -->
      <div class="panel-header">
        <h3>📢 智能提醒</h3>
        <div class="header-actions">
          <button @click="markAllAsRead" class="btn-mark-read" title="全部已读">
            ✓ 全部已读
          </button>
          <button @click="togglePanel" class="btn-close">✕</button>
        </div>
      </div>
      
      <!-- 统计概览 -->
      <div class="stats-overview" v-if="stats">
        <div class="stat-card">
          <span class="stat-value">{{ stats.total_alerts }}</span>
          <span class="stat-label">总提醒</span>
        </div>
        <div class="stat-card warning">
          <span class="stat-value">{{ stats.unread_count }}</span>
          <span class="stat-label">未读</span>
        </div>
        <div class="stat-card">
          <span class="stat-value critical">{{ stats.by_level?.critical || 0 }}</span>
          <span class="stat-label">严重</span>
        </div>
        <div class="stat-card">
          <span class="stat-value warning">{{ stats.by_level?.warning || 0 }}</span>
          <span class="stat-label">警告</span>
        </div>
      </div>
      
      <!-- 提醒列表 -->
      <div class="alert-list">
        <div
          v-for="alert in alerts"
          :key="alert.alert_id"
          :class="['alert-item', alert.level, { read: alert.read }]"
          @click="markAsRead(alert.alert_id)"
        >
          <!-- 提醒级别标识 -->
          <div class="alert-level-indicator" :class="alert.level"></div>
          
          <!-- 提醒内容 -->
          <div class="alert-content">
            <div class="alert-header">
              <span class="alert-title">{{ alert.title }}</span>
              <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
            </div>
            
            <div class="alert-message">{{ alert.message }}</div>
            
            <div class="alert-meta">
              <span class="alert-type">{{ getAlertTypeLabel(alert.alert_type) }}</span>
              <span class="alert-rule">{{ alert.rule_name }}</span>
            </div>
            
            <!-- 详细数据（如果有） -->
            <div v-if="alert.data && Object.keys(alert.data).length > 0" class="alert-data">
              <div class="data-row" v-for="(value, key) in alert.data" :key="key">
                <span class="data-key">{{ formatDataKey(key) }}:</span>
                <span class="data-value">{{ formatDataValue(value) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 未读标识 -->
          <div v-if="!alert.read" class="unread-dot"></div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="alerts.length === 0 && !loading" class="empty-state">
          <span class="empty-icon">✨</span>
          <span class="empty-text">暂无提醒</span>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <span>加载中...</span>
        </div>
      </div>
      
      <!-- 加载更多 -->
      <div v-if="alerts.length > 0 && hasMore" class="load-more">
        <button @click="loadMore" :disabled="loadingMore">
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
      
      <!-- 面板底部 -->
      <div class="panel-footer">
        <button @click="showRulesConfig" class="btn-config">
          ⚙️ 规则配置
        </button>
        <button @click="refreshAlerts" class="btn-refresh" :disabled="loading">
          🔄 刷新
        </button>
      </div>
    </div>
    
    <!-- 规则配置弹窗 -->
    <div v-if="showConfigModal" class="modal-overlay" @click="closeConfigModal">
      <div class="config-modal" @click.stop>
        <div class="modal-header">
          <h3>⚙️ 提醒规则配置</h3>
          <button @click="closeConfigModal" class="btn-close">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="rules-list">
            <div
              v-for="rule in rules"
              :key="rule.rule_id"
              class="rule-item"
            >
              <div class="rule-header">
                <span class="rule-name">{{ rule.rule_name }}</span>
                <label class="toggle-switch">
                  <input
                    type="checkbox"
                    :checked="rule.enabled"
                    @change="toggleRule(rule.rule_id, $event)"
                  >
                  <span class="toggle-slider"></span>
                </label>
              </div>
              
              <div class="rule-description">{{ rule.description }}</div>
              
              <div class="rule-thresholds" v-if="rule.thresholds">
                <div
                  v-for="(value, key) in rule.thresholds"
                  :key="key"
                  class="threshold-item"
                >
                  <span class="threshold-key">{{ formatThresholdKey(key) }}:</span>
                  <span class="threshold-value">{{ formatThresholdValue(value) }}</span>
                </div>
              </div>
              
              <div class="rule-channels">
                <span
                  v-for="channel in rule.channels"
                  :key="channel"
                  class="channel-tag"
                >
                  {{ getChannelLabel(channel) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeConfigModal" class="btn-primary">完成</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8001/api/alerts'

export default {
  name: 'AlertPanel',
  
  setup() {
    // 状态
    const panelOpen = ref(false)
    const loading = ref(false)
    const loadingMore = ref(false)
    const showConfigModal = ref(false)
    
    const alerts = ref([])
    const stats = ref(null)
    const rules = ref([])
    const unreadCount = ref(0)
    
    const limit = ref(20)
    const hasMore = ref(true)
    
    // 获取认证头
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      return token ? { 'Authorization': `Bearer ${token}` } : {}
    }
    
    // 加载提醒
    const loadAlerts = async (unreadOnly = false) => {
      loading.value = true
      try {
        const response = await axios.get(`${API_BASE}/history`, {
          params: {
            limit: limit.value,
            unread_only: unreadOnly,
          },
          headers: getAuthHeaders(),
        })
        
        if (response.data.success) {
          alerts.value = response.data.data
          hasMore.value = response.data.total >= limit.value
        }
      } catch (error) {
        console.error('加载提醒失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 加载更多
    const loadMore = async () => {
      if (loadingMore.value || !hasMore.value) return
      
      loadingMore.value = true
      try {
        const currentLength = alerts.value.length
        const response = await axios.get(`${API_BASE}/history`, {
          params: {
            limit: limit.value + 20,
          },
          headers: getAuthHeaders(),
        })
        
        if (response.data.success) {
          alerts.value = response.data.data
          hasMore.value = response.data.total > currentLength + 20
        }
      } catch (error) {
        console.error('加载更多失败:', error)
      } finally {
        loadingMore.value = false
      }
    }
    
    // 加载统计
    const loadStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/stats`, {
          headers: getAuthHeaders(),
        })
        
        if (response.data.success) {
          stats.value = response.data.data
          unreadCount.value = response.data.data.unread_count
        }
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    }
    
    // 加载规则
    const loadRules = async () => {
      try {
        const response = await axios.get(`${API_BASE}/rules`, {
          headers: getAuthHeaders(),
        })
        
        if (response.data.success) {
          rules.value = response.data.data
        }
      } catch (error) {
        console.error('加载规则失败:', error)
      }
    }
    
    // 标记为已读
    const markAsRead = async (alertId) => {
      try {
        await axios.post(`${API_BASE}/read/${alertId}`, {}, {
          headers: getAuthHeaders(),
        })
        
        // 更新本地状态
        const alert = alerts.value.find(a => a.alert_id === alertId)
        if (alert) {
          alert.read = true
        }
        
        // 重新加载统计
        loadStats()
      } catch (error) {
        console.error('标记已读失败:', error)
      }
    }
    
    // 全部标记为已读
    const markAllAsRead = async () => {
      try {
        await axios.post(`${API_BASE}/read/all`, {}, {
          headers: getAuthHeaders(),
        })
        
        // 更新本地状态
        alerts.value.forEach(alert => {
          alert.read = true
        })
        
        unreadCount.value = 0
        loadStats()
      } catch (error) {
        console.error('全部标记失败:', error)
      }
    }
    
    // 刷新提醒
    const refreshAlerts = () => {
      loadAlerts()
      loadStats()
    }
    
    // 切换面板
    const togglePanel = () => {
      panelOpen.value = !panelOpen.value
      if (panelOpen.value) {
        loadAlerts()
        loadStats()
      }
    }
    
    // 显示规则配置
    const showRulesConfig = () => {
      loadRules()
      showConfigModal.value = true
    }
    
    // 关闭规则配置
    const closeConfigModal = () => {
      showConfigModal.value = false
    }
    
    // 切换规则启用状态
    const toggleRule = async (ruleId, event) => {
      const enabled = event.target.checked
      const endpoint = enabled ? 'enable' : 'disable'
      
      try {
        await axios.post(`${API_BASE}/rules/${ruleId}/${endpoint}`, {}, {
          headers: getAuthHeaders(),
        })
        
        // 更新本地状态
        const rule = rules.value.find(r => r.rule_id === ruleId)
        if (rule) {
          rule.enabled = enabled
        }
      } catch (error) {
        console.error('更新规则失败:', error)
        event.target.checked = !enabled // 回滚
      }
    }
    
    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // 1 分钟内
        return '刚刚'
      } else if (diff < 3600000) { // 1 小时内
        return `${Math.floor(diff / 60000)}分钟前`
      } else if (diff < 86400000) { // 24 小时内
        return `${Math.floor(diff / 3600000)}小时前`
      } else {
        return date.toLocaleString('zh-CN', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      }
    }
    
    // 获取提醒类型标签
    const getAlertTypeLabel = (type) => {
      const labels = {
        'sentiment_low': '情绪预警',
        'speech_risk': '话术风险',
        'audience_loss': '观众流失',
        'controversy': '争议预警',
        'heat_drop': '热度下降',
        'key_moment': '关键时刻',
      }
      return labels[type] || type
    }
    
    // 获取渠道标签
    const getChannelLabel = (channel) => {
      const labels = {
        'in_app': '站内信',
        'email': '邮件',
        'wechat': '微信',
      }
      return labels[channel] || channel
    }
    
    // 格式化数据键
    const formatDataKey = (key) => {
      const labels = {
        'negative_count': '负面数量',
        'total_count': '总数',
        'negative_ratio': '负面比例',
        'window_seconds': '时间窗口',
        'controversy_count': '争议数量',
        'controversy_ratio': '争议比例',
        'initial_count': '初始观众',
        'current_count': '当前观众',
        'drop_count': '流失数量',
        'drop_ratio': '流失比例',
        'baseline_rate': '基线速率',
        'current_rate': '当前速率',
        'heat_multiplier': '热度倍数',
        'climax_count': '高潮弹幕',
        'detected_words': '检测词',
        'detected_phrases': '检测短语',
      }
      return labels[key] || key
    }
    
    // 格式化数据值
    const formatDataValue = (value) => {
      if (typeof value === 'number') {
        if (value > 1 || value < -1) {
          return Math.round(value)
        } else {
          return (value * 100).toFixed(1) + '%'
        }
      }
      if (Array.isArray(value)) {
        return value.join(', ')
      }
      return value
    }
    
    // 格式化阈值键
    const formatThresholdKey = (key) => {
      const labels = {
        'negative_ratio_threshold': '负面比例阈值',
        'window_seconds': '时间窗口',
        'min_danmu_count': '最小弹幕数',
        'controversy_ratio_threshold': '争议比例阈值',
        'drop_ratio_threshold': '下降比例阈值',
        'min_viewers': '最小观众数',
        'heat_multiplier': '热度倍数',
        'sensitive_words': '敏感词',
        'critical_words': '严重违规词',
        'risk_phrases': '风险短语',
      }
      return labels[key] || key
    }
    
    // 格式化阈值值
    const formatThresholdValue = (value) => {
      if (Array.isArray(value)) {
        return value.slice(0, 5).join(', ') + (value.length > 5 ? '...' : '')
      }
      if (typeof value === 'number' && (value < 1 && value > -1)) {
        return (value * 100).toFixed(0) + '%'
      }
      return value
    }
    
    // 定时刷新（每 30 秒）
    let refreshInterval = null
    onMounted(() => {
      refreshInterval = setInterval(() => {
        if (panelOpen.value) {
          loadStats()
        }
      }, 30000)
    })
    
    // 清理定时器
    watch(panelOpen, (open) => {
      if (!open && refreshInterval) {
        clearInterval(refreshInterval)
        refreshInterval = null
      }
    })
    
    return {
      // 状态
      panelOpen,
      loading,
      loadingMore,
      showConfigModal,
      alerts,
      stats,
      rules,
      unreadCount,
      hasMore,
      
      // 方法
      togglePanel,
      loadAlerts,
      loadMore,
      loadStats,
      loadRules,
      markAsRead,
      markAllAsRead,
      refreshAlerts,
      showRulesConfig,
      closeConfigModal,
      toggleRule,
      
      // 格式化
      formatTime,
      getAlertTypeLabel,
      getChannelLabel,
      formatDataKey,
      formatDataValue,
      formatThresholdKey,
      formatThresholdValue,
    }
  },
}
</script>

<style scoped>
.alert-panel {
  position: relative;
}

/* 铃铛图标 */
.alert-bell {
  position: relative;
  cursor: pointer;
  font-size: 24px;
  padding: 8px;
  transition: transform 0.2s;
}

.alert-bell:hover {
  transform: scale(1.1);
}

.unread-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #ff4757;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

/* 面板内容 */
.panel-content {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  max-height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 面板头部 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-mark-read {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.btn-mark-read:hover {
  background: rgba(255, 255, 255, 0.3);
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.stat-card {
  background: white;
  padding: 8px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card.warning .stat-value {
  color: #ffa502;
}

.stat-card.critical .stat-value {
  color: #ff4757;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #666;
  margin-top: 2px;
}

/* 提醒列表 */
.alert-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.alert-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #ccc;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.alert-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.alert-item.read {
  opacity: 0.7;
  background: #f8f9fa;
}

.alert-item.critical {
  border-left-color: #ff4757;
}

.alert-item.warning {
  border-left-color: #ffa502;
}

.alert-item.info {
  border-left-color: #667eea;
}

.alert-level-indicator {
  width: 4px;
  border-radius: 2px;
  flex-shrink: 0;
}

.alert-level-indicator.critical {
  background: #ff4757;
}

.alert-level-indicator.warning {
  background: #ffa502;
}

.alert-level-indicator.info {
  background: #667eea;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.alert-title {
  font-weight: bold;
  font-size: 14px;
  color: #333;
}

.alert-time {
  font-size: 11px;
  color: #999;
}

.alert-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  line-height: 1.4;
}

.alert-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #999;
}

.alert-type,
.alert-rule {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 详细数据 */
.alert-data {
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.data-row:last-child {
  margin-bottom: 0;
}

.data-key {
  color: #666;
  font-weight: 500;
}

.data-value {
  color: #333;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 8px;
}

.empty-text {
  font-size: 14px;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 20px;
  color: #999;
}

/* 加载更多 */
.load-more {
  padding: 12px;
  text-align: center;
  border-top: 1px solid #e0e0e0;
}

.load-more button {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.load-more button:hover:not(:disabled) {
  background: #5568d3;
}

.load-more button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 面板底部 */
.panel-footer {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.btn-config,
.btn-refresh {
  flex: 1;
  background: white;
  border: 1px solid #ddd;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-config:hover,
.btn-refresh:hover:not(:disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 配置弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.config-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-header .btn-close {
  color: #666;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.rule-name {
  font-weight: bold;
  font-size: 14px;
}

/* 切换开关 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #667eea;
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.rule-description {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.rule-thresholds {
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 12px;
}

.threshold-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.threshold-item:last-child {
  margin-bottom: 0;
}

.threshold-key {
  color: #666;
}

.threshold-value {
  color: #333;
  font-weight: 500;
}

.rule-channels {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.channel-tag {
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #666;
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  text-align: right;
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #5568d3;
}
</style>
