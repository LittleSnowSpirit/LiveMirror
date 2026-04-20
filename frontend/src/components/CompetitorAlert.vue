<template>
  <div class="competitor-alert">
    <!-- 告警弹窗通知 -->
    <el-notification
      v-for="alert in visibleAlerts"
      :key="alert.id"
      :title="alert.title"
      :message="alert.message"
      :type="alert.type"
      :duration="alert.duration"
      position="top-right"
      @close="handleClose(alert.id)"
    />

    <!-- 告警悬浮窗 -->
    <div class="alert-float" v-if="showFloatAlert && currentFloatAlert">
      <div class="float-header">
        <span class="float-title">🔔 实时告警</span>
        <el-button size="small" text @click="closeFloatAlert">✕</el-button>
      </div>
      <div class="float-content">
        <div class="float-alert-item" :class="currentFloatAlert.type">
          <div class="alert-icon">
            {{ getAlertIcon(currentFloatAlert.alertType) }}
          </div>
          <div class="alert-info">
            <div class="alert-competitor">{{ currentFloatAlert.competitorName }}</div>
            <div class="alert-message">{{ currentFloatAlert.message }}</div>
            <div class="alert-time">{{ formatTime(currentFloatAlert.time) }}</div>
          </div>
        </div>
      </div>
      <div class="float-footer">
        <el-button size="small" @click="viewAllAlerts">查看全部</el-button>
      </div>
    </div>

    <!-- 告警设置面板 -->
    <el-drawer
      v-model="settingsVisible"
      title="🔔 告警通知设置"
      size="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="通知开关">
          <el-switch v-model="notificationEnabled" @change="saveSettings" />
        </el-form-item>

        <el-form-item label="声音提醒">
          <el-switch v-model="soundEnabled" @change="saveSettings" />
        </el-form-item>

        <el-form-item label="弹窗提醒">
          <el-switch v-model="popupEnabled" @change="saveSettings" />
        </el-form-item>

        <el-form-item label="悬浮窗">
          <el-switch v-model="floatEnabled" @change="saveSettings" />
        </el-form-item>

        <el-divider>邮件通知</el-divider>

        <el-form-item label="启用邮件">
          <el-switch v-model="emailEnabled" @change="saveSettings" />
        </el-form-item>

        <el-form-item label="SMTP 服务器">
          <el-input 
            v-model="emailConfig.smtp_server" 
            placeholder="smtp.example.com"
            :disabled="!emailEnabled"
          />
        </el-form-item>

        <el-form-item label="SMTP 端口">
          <el-input-number 
            v-model="emailConfig.smtp_port" 
            :min="1" 
            :max="65535"
            :disabled="!emailEnabled"
          />
        </el-form-item>

        <el-form-item label="发件人">
          <el-input 
            v-model="emailConfig.username" 
            placeholder="your@email.com"
            :disabled="!emailEnabled"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input 
            v-model="emailConfig.password" 
            type="password"
            placeholder="授权码或密码"
            :disabled="!emailEnabled"
          />
        </el-form-item>

        <el-form-item label="收件人">
          <el-select 
            v-model="emailConfig.recipients" 
            multiple 
            allow-create
            filterable
            :disabled="!emailEnabled"
          >
            <el-option label="运营负责人" value="ops@example.com" />
            <el-option label="主播负责人" value="streamer@example.com" />
            <el-option label="老板" value="boss@example.com" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button @click="testEmailNotification" :loading="testing" :disabled="!emailEnabled">
            发送邮件测试
          </el-button>
        </el-form-item>

        <el-divider>微信通知</el-divider>

        <el-form-item label="启用微信">
          <el-switch v-model="wechatEnabled" @change="saveSettings" />
        </el-form-item>

        <el-form-item label="企业 ID">
          <el-input 
            v-model="wechatConfig.corp_id" 
            placeholder="企业微信 CorpID"
            :disabled="!wechatEnabled"
          />
        </el-form-item>

        <el-form-item label="应用 ID">
          <el-input 
            v-model="wechatConfig.agent_id" 
            placeholder="应用 AgentID"
            :disabled="!wechatEnabled"
          />
        </el-form-item>

        <el-form-item label="Secret">
          <el-input 
            v-model="wechatConfig.secret" 
            type="password"
            placeholder="应用 Secret"
            :disabled="!wechatEnabled"
          />
        </el-form-item>

        <el-form-item label="接收用户">
          <el-select 
            v-model="wechatConfig.user_ids" 
            multiple 
            allow-create
            filterable
            :disabled="!wechatEnabled"
          >
            <el-option label="运营" value="ops" />
            <el-option label="主播" value="streamer" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button @click="testWechatNotification" :loading="testing" :disabled="!wechatEnabled">
            发送微信测试
          </el-button>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="settingsVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveSettings">保存配置</el-button>
      </template>
    </el-drawer>

    <!-- 告警历史记录 -->
    <el-dialog
      v-model="historyVisible"
      title="📋 告警历史记录"
      width="900px"
    >
      <el-form :inline="true">
        <el-form-item label="竞品">
          <el-select v-model="historyFilter.competitor_id" placeholder="全部" clearable>
            <el-option 
              v-for="c in competitors" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="historyFilter.alert_type" placeholder="全部" clearable>
            <el-option label="流量突增" value="viewer_spike" />
            <el-option label="话术抄袭" value="script_plagiarism" />
            <el-option label="成交额阈值" value="gmv_threshold" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker
            v-model="historyFilter.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadHistory"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHistory">查询</el-button>
          <el-button @click="exportHistory">导出</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="alertHistory" style="width: 100%" max-height="500">
        <el-table-column prop="rule_name" label="规则名称" />
        <el-table-column prop="competitor_name" label="竞品" width="120" />
        <el-table-column prop="alert_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertTagType(row.alert_type)" size="small">
              {{ getAlertTypeName(row.alert_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="告警内容" min-width="200" />
        <el-table-column prop="current_value" label="当前值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="80" />
        <el-table-column prop="triggered_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.triggered_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="notified" label="通知" width="80">
          <template #default="{ row }">
            <el-tag :type="row.notified ? 'success' : 'warning'" size="small">
              {{ row.notified ? '已通知' : '未通知' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" style="margin-top: 20px; text-align: right;">
        <el-pagination
          v-model:current-page="historyPage"
          v-model:page-size="historyPageSize"
          :total="historyTotal"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const API_BASE = '/api/monitor'

// 状态
const visibleAlerts = ref([])
const showFloatAlert = ref(false)
const currentFloatAlert = ref(null)
const settingsVisible = ref(false)
const historyVisible = ref(false)
const testing = ref(false)

// 配置
const notificationEnabled = ref(true)
const soundEnabled = ref(true)
const popupEnabled = ref(true)
const floatEnabled = ref(false)

const emailEnabled = ref(false)
const emailConfig = reactive({
  smtp_server: '',
  smtp_port: 587,
  username: '',
  password: '',
  recipients: []
})

const wechatEnabled = ref(false)
const wechatConfig = reactive({
  corp_id: '',
  agent_id: '',
  secret: '',
  user_ids: []
})

// 历史
const competitors = ref([])
const alertHistory = ref([])
const historyFilter = reactive({
  competitor_id: '',
  alert_type: '',
  date_range: []
})
const historyPage = ref(1)
const historyPageSize = ref(20)
const historyTotal = ref(0)

// WebSocket 连接
let ws = null

// 生命周期
onMounted(() => {
  loadSettings()
  loadCompetitors()
  connectWebSocket()
})

onUnmounted(() => {
  disconnectWebSocket()
})

// 方法
function connectWebSocket() {
  // 实际项目中应该使用 WebSocket 实时推送
  // 这里用轮询模拟
  startPolling()
}

function disconnectWebSocket() {
  stopPolling()
}

let pollTimer = null

function startPolling() {
  pollTimer = setInterval(async () => {
    await checkNewAlerts()
  }, 5000) // 5 秒轮询一次
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function checkNewAlerts() {
  try {
    const res = await fetch(`${API_BASE}/alerts?limit=1`)
    if (res.ok) {
      const data = await res.json()
      if (data.length > 0) {
        const latestAlert = data[0]
        // 检查是否是新告警
        const lastAlertId = localStorage.getItem('lastAlertId')
        if (lastAlertId !== latestAlert.id) {
          localStorage.setItem('lastAlertId', latestAlert.id)
          showNewAlert(latestAlert)
        }
      }
    }
  } catch (e) {
    console.error('轮询告警失败:', e)
  }
}

function showNewAlert(alert) {
  if (!notificationEnabled.value) return

  // 弹窗通知
  if (popupEnabled.value) {
    visibleAlerts.value.push({
      id: alert.id + '_' + Date.now(),
      title: `⚠️ ${alert.rule_name}`,
      message: `${alert.competitor_name}: ${alert.message}`,
      type: getAlertNotificationType(alert.alert_type),
      duration: 8000
    })

    // 自动移除
    setTimeout(() => {
      const index = visibleAlerts.value.findIndex(a => a.id === alert.id + '_' + Date.now())
      if (index > -1) {
        visibleAlerts.value.splice(index, 1)
      }
    }, 8000)
  }

  // 悬浮窗
  if (floatEnabled.value) {
    currentFloatAlert.value = {
      id: alert.id,
      competitorName: alert.competitor_name,
      message: alert.message,
      alertType: alert.alert_type,
      time: alert.triggered_at,
      type: getAlertNotificationType(alert.alert_type)
    }
    showFloatAlert.value = true

    // 5 秒后自动关闭
    setTimeout(() => {
      showFloatAlert.value = false
    }, 5000)
  }

  // 声音提醒
  if (soundEnabled.value) {
    playAlertSound()
  }
}

function playAlertSound() {
  // 播放提示音
  const audio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=')
  audio.play().catch(e => console.log('播放声音失败:', e))
}

function handleClose(id) {
  const index = visibleAlerts.value.findIndex(a => a.id === id)
  if (index > -1) {
    visibleAlerts.value.splice(index, 1)
  }
}

function closeFloatAlert() {
  showFloatAlert.value = false
}

function viewAllAlerts() {
  showFloatAlert.value = false
  historyVisible.value = true
  loadHistory()
}

async function loadSettings() {
  try {
    const res = await fetch(`${API_BASE}/notification-config`)
    if (res.ok) {
      const config = await res.json()
      
      emailEnabled.value = config.email?.enabled || false
      if (config.email) {
        emailConfig.smtp_server = config.email.smtp_server || ''
        emailConfig.smtp_port = config.email.smtp_port || 587
        emailConfig.username = config.email.username || ''
        emailConfig.recipients = config.email.recipients || []
      }

      wechatEnabled.value = config.wechat?.enabled || false
      if (config.wechat) {
        wechatConfig.corp_id = config.wechat.corp_id || ''
        wechatConfig.agent_id = config.wechat.agent_id || ''
        wechatConfig.user_ids = config.wechat.user_ids || []
      }

      // 加载本地设置
      const localSettings = JSON.parse(localStorage.getItem('alertSettings') || '{}')
      notificationEnabled.value = localSettings.notificationEnabled ?? true
      soundEnabled.value = localSettings.soundEnabled ?? true
      popupEnabled.value = localSettings.popupEnabled ?? true
      floatEnabled.value = localSettings.floatEnabled ?? false
    }
  } catch (e) {
    console.error('加载配置失败:', e)
  }
}

async function saveSettings() {
  const settings = {
    notificationEnabled: notificationEnabled.value,
    soundEnabled: soundEnabled.value,
    popupEnabled: popupEnabled.value,
    floatEnabled: floatEnabled.value
  }
  localStorage.setItem('alertSettings', JSON.stringify(settings))

  // 保存服务器配置
  try {
    await fetch(`${API_BASE}/notification-config/email`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        enabled: emailEnabled.value,
        smtp_server: emailConfig.smtp_server,
        smtp_port: emailConfig.smtp_port,
        username: emailConfig.username,
        password: emailConfig.password,
        recipients: emailConfig.recipients
      })
    })

    await fetch(`${API_BASE}/notification-config/wechat`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        enabled: wechatEnabled.value,
        corp_id: wechatConfig.corp_id,
        agent_id: wechatConfig.agent_id,
        secret: wechatConfig.secret,
        user_ids: wechatConfig.user_ids
      })
    })

    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function testEmailNotification() {
  testing.value = true
  try {
    const res = await fetch(`${API_BASE}/notification/test/email`, { method: 'POST' })
    if (res.ok) {
      ElMessage.success('测试邮件已发送')
    } else {
      ElMessage.error('发送失败')
    }
  } finally {
    testing.value = false
  }
}

async function testWechatNotification() {
  testing.value = true
  try {
    const res = await fetch(`${API_BASE}/notification/test/wechat`, { method: 'POST' })
    if (res.ok) {
      ElMessage.success('测试消息已发送')
    } else {
      ElMessage.error('发送失败')
    }
  } finally {
    testing.value = false
  }
}

async function loadCompetitors() {
  try {
    const res = await fetch(`${API_BASE}/competitors`)
    if (res.ok) {
      competitors.value = await res.json()
    }
  } catch (e) {
    console.error('加载竞品列表失败:', e)
  }
}

async function loadHistory() {
  try {
    const params = new URLSearchParams({
      limit: historyPageSize.value,
      offset: (historyPage.value - 1) * historyPageSize.value
    })

    if (historyFilter.competitor_id) {
      params.append('competitor_id', historyFilter.competitor_id)
    }
    if (historyFilter.alert_type) {
      params.append('alert_type', historyFilter.alert_type)
    }
    if (historyFilter.date_range && historyFilter.date_range.length === 2) {
      params.append('start_time', historyFilter.date_range[0].toISOString())
      params.append('end_time', historyFilter.date_range[1].toISOString())
    }

    const res = await fetch(`${API_BASE}/alerts?${params}`)
    if (res.ok) {
      alertHistory.value = await res.json()
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}

function exportHistory() {
  // 导出 CSV
  const headers = ['规则名称', '竞品', '类型', '告警内容', '当前值', '阈值', '时间', '通知状态']
  const rows = alertHistory.value.map(a => [
    a.rule_name,
    a.competitor_name,
    getAlertTypeName(a.alert_type),
    a.message,
    a.current_value,
    a.threshold,
    a.triggered_at,
    a.notified ? '已通知' : '未通知'
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `告警记录_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('导出成功')
}

// 工具函数
function getAlertIcon(type) {
  const icons = {
    viewer_spike: '📈',
    script_plagiarism: '📋',
    gmv_threshold: '💰'
  }
  return icons[type] || '⚠️'
}

function getAlertNotificationType(type) {
  const types = {
    viewer_spike: 'warning',
    script_plagiarism: 'error',
    gmv_threshold: 'success'
  }
  return types[type] || 'info'
}

function getAlertTagType(type) {
  const types = {
    viewer_spike: 'warning',
    script_plagiarism: 'danger',
    gmv_threshold: 'success'
  }
  return types[type] || ''
}

function getAlertTypeName(type) {
  const names = {
    viewer_spike: '流量突增',
    script_plagiarism: '话术抄袭',
    gmv_threshold: '成交额阈值'
  }
  return names[type] || type
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}

// 暴露方法给父组件
defineExpose({
  openSettings: () => { settingsVisible.value = true },
  openHistory: () => { historyVisible.value = true }
})
</script>

<style scoped>
.alert-float {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.float-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.float-title {
  font-weight: bold;
  font-size: 14px;
}

.float-content {
  padding: 15px;
}

.float-alert-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f5f7fa;
}

.float-alert-item.warning {
  border-left: 4px solid #E6A23C;
}

.float-alert-item.error {
  border-left: 4px solid #F56C6C;
}

.float-alert-item.success {
  border-left: 4px solid #67C23A;
}

.alert-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.alert-info {
  flex: 1;
  min-width: 0;
}

.alert-competitor {
  font-weight: bold;
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-time {
  font-size: 12px;
  color: #909399;
}

.float-footer {
  padding: 10px 15px;
  border-top: 1px solid #ebeef5;
  text-align: right;
}

.pagination-container {
  margin-top: 20px;
}
</style>
