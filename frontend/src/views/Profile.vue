<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人中心</h2>
      <p class="description">管理您的账户信息和设置</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 主要内容 -->
    <div v-else class="profile-content">
      <el-row :gutter="20">
        <!-- 左侧：用户信息和统计 -->
        <el-col :xs="24" :sm="12" :md="8">
          <!-- 用户信息卡片 -->
          <el-card class="user-info-card">
            <template #header>
              <div class="card-header">
                <span>个人信息</span>
              </div>
            </template>
            
            <div class="user-info">
              <div class="avatar-section">
                <el-avatar :size="100" :src="userProfile.avatar_url || defaultAvatar">
                  <img :src="defaultAvatar" alt="avatar" />
                </el-avatar>
                <el-button 
                  type="primary" 
                  link 
                  size="small"
                  @click="showAvatarDialog = true"
                >
                  修改头像
                </el-button>
              </div>
              
              <div class="user-details">
                <div class="username">
                  <el-icon><user /></el-icon>
                  <span>{{ userProfile.username }}</span>
                </div>
                <div v-if="userProfile.email" class="email">
                  <el-icon><message /></el-icon>
                  <span>{{ userProfile.email }}</span>
                </div>
                <div class="register-date">
                  <el-icon><calendar /></el-icon>
                  <span>注册时间：{{ formatDate(userProfile.created_at) }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 会员信息卡片 -->
          <el-card v-if="membership" class="membership-card" :class="{ 'is-member': membership.is_member }">
            <template #header>
              <div class="card-header">
                <span>会员信息</span>
              </div>
            </template>
            
            <div class="membership-info">
              <el-tag v-if="membership.is_member" :type="getMembershipType(membership.membership_type)" size="large">
                {{ getMembershipLabel(membership.membership_type) }}
              </el-tag>
              <el-tag v-else type="info" size="large">普通会员</el-tag>
              
              <div v-if="membership.is_member && membership.expires_at" class="membership-expiry">
                <el-icon><clock /></el-icon>
                <span>有效期至：{{ formatDate(membership.expires_at) }}</span>
              </div>
              <div v-if="membership.remaining_days !== null && membership.remaining_days !== undefined" class="remaining-days">
                <el-icon><timer /></el-icon>
                <span>剩余 {{ membership.remaining_days }} 天</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：使用统计和设置 -->
        <el-col :xs="24" :sm="12" :md="16">
          <!-- 使用统计 -->
          <UserStats :stats="userStats" />

          <!-- 账号设置 -->
          <Settings 
            @password-change="handlePasswordChange"
            @avatar-change="handleAvatarChange"
            @logout="handleLogout"
          />

          <!-- 操作日志 -->
          <el-card class="activity-logs-card">
            <template #header>
              <div class="card-header">
                <span>最近操作</span>
                <el-button type="primary" link size="small" @click="loadActivityLogs">
                  刷新
                </el-button>
              </div>
            </template>
            
            <el-empty v-if="activityLogs.length === 0" description="暂无操作记录" />
            
            <el-timeline v-else>
              <el-timeline-item
                v-for="log in activityLogs"
                :key="log.id"
                :timestamp="formatDate(log.created_at)"
                placement="top"
                :type="getLogType(log.action)"
              >
                <el-card>
                  <div class="log-item">
                    <el-icon><component :is="getLogIcon(log.action)" /></el-icon>
                    <span>{{ log.description }}</span>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 修改头像对话框 -->
    <el-dialog
      v-model="showAvatarDialog"
      title="修改头像"
      width="400px"
    >
      <el-form :model="avatarForm" label-position="top">
        <el-form-item label="头像 URL">
          <el-input
            v-model="avatarForm.avatar_url"
            placeholder="请输入头像图片 URL"
            :prefix-icon="Picture"
          />
        </el-form-item>
        <el-form-item label="预览">
          <el-avatar :size="100" :src="avatarForm.avatar_url || defaultAvatar">
            <img :src="defaultAvatar" alt="avatar" />
          </el-avatar>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAvatarDialog = false">取消</el-button>
          <el-button type="primary" @click="submitAvatarChange" :loading="submitting">
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Message, Calendar, Clock, Timer, Picture } from '@element-plus/icons-vue'
import UserStats from '@/components/UserStats.vue'
import Settings from '@/components/Settings.vue'
import type { Component } from 'vue'

// API 基础 URL（根据实际配置修改）
const API_BASE_URL = 'http://localhost:8001'

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

// 路由
const router = useRouter()

// 状态
const loading = ref(true)
const submitting = ref(false)
const showAvatarDialog = ref(false)

// 用户数据
const userProfile = reactive({
  id: 0,
  username: '',
  email: '',
  is_active: true,
  created_at: new Date(),
  avatar_url: ''
})

const userStats = reactive({
  analysis_count: 0,
  total_duration: 0,
  saved_reports: 0,
  total_danmus: 0,
  batch_uploads: 0
})

const membership = ref({
  is_member: false,
  membership_type: 'basic',
  expires_at: null as Date | null,
  remaining_days: null as number | null
})

const activityLogs = ref<any[]>([])

// 头像表单
const avatarForm = reactive({
  avatar_url: ''
})

// 获取 Token
const getToken = (): string | null => {
  return localStorage.getItem('access_token')
}

// 加载用户资料
const loadUserProfile = async () => {
  try {
    const token = getToken()
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    const response = await fetch(`${API_BASE_URL}/user/profile`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
      return
    }

    if (!response.ok) {
      throw new Error('加载用户资料失败')
    }

    const data = await response.json()
    
    // 填充用户信息
    Object.assign(userProfile, data.profile)
    Object.assign(userStats, data.stats)
    
    if (data.membership) {
      Object.assign(membership.value, data.membership)
    }
    
    if (data.recent_logs && data.recent_logs.length > 0) {
      activityLogs.value = data.recent_logs
    }
  } catch (error) {
    console.error('加载用户资料失败:', error)
    ElMessage.error('加载用户资料失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 加载操作日志
const loadActivityLogs = async () => {
  try {
    const token = getToken()
    if (!token) return

    const response = await fetch(`${API_BASE_URL}/user/activity-logs?limit=20`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      const data = await response.json()
      activityLogs.value = data
    }
  } catch (error) {
    console.error('加载操作日志失败:', error)
  }
}

// 修改头像
const submitAvatarChange = async () => {
  if (!avatarForm.avatar_url) {
    ElMessage.warning('请输入头像 URL')
    return
  }

  submitting.value = true
  
  try {
    const token = getToken()
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    const response = await fetch(`${API_BASE_URL}/user/change-avatar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        avatar_url: avatarForm.avatar_url
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '修改头像失败')
    }

    const data = await response.json()
    userProfile.avatar_url = data.avatar_url
    
    ElMessage.success('头像修改成功')
    showAvatarDialog.value = false
  } catch (error: any) {
    console.error('修改头像失败:', error)
    ElMessage.error(error.message || '修改头像失败')
  } finally {
    submitting.value = false
  }
}

// 处理密码修改
const handlePasswordChange = async (oldPassword: string, newPassword: string) => {
  try {
    const token = getToken()
    if (!token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return false
    }

    const response = await fetch(`${API_BASE_URL}/user/change-password`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '修改密码失败')
    }

    ElMessage.success('密码修改成功，请重新登录')
    
    // 延迟跳转登录页
    setTimeout(() => {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    }, 1500)
    
    return true
  } catch (error: any) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.message || '修改密码失败')
    return false
  }
}

// 处理头像修改（从 Settings 组件）
const handleAvatarChange = () => {
  showAvatarDialog.value = true
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = getToken()
    if (token) {
      // 调用登出接口（可选）
      await fetch(`${API_BASE_URL}/user/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }).catch(() => {}) // 忽略错误
    }

    // 清除本地 Token
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 用户取消
  }
}

// 工具函数
const formatDate = (dateString: string | Date): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getMembershipType = (type?: string): 'success' | 'warning' | 'danger' | 'info' => {
  switch (type) {
    case 'vip': return 'danger'
    case 'premium': return 'warning'
    default: return 'success'
  }
}

const getMembershipLabel = (type?: string): string => {
  switch (type) {
    case 'vip': return 'VIP 会员'
    case 'premium': return '高级会员'
    default: return '会员'
  }
}

const getLogType = (action: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  switch (action) {
    case 'login': return 'success'
    case 'upload': return 'primary'
    case 'analysis': return 'warning'
    case 'password_change': return 'danger'
    case 'avatar_change': return 'info'
    default: return 'info'
  }
}

const getLogIcon = (action: string): Component => {
  switch (action) {
    case 'login': return User
    case 'upload': return Picture
    case 'analysis': return Timer
    case 'password_change': return Message
    case 'avatar_change': return Picture
    default: return User
  }
}

// 生命周期
onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.description {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.loading-container {
  padding: 20px;
}

.profile-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

/* 用户信息卡片 */
.user-info-card {
  margin-bottom: 20px;
}

.user-info {
  text-align: center;
  padding: 10px 0;
}

.avatar-section {
  margin-bottom: 20px;
}

.avatar-section .el-button {
  margin-top: 12px;
}

.user-details {
  text-align: left;
  padding: 0 10px;
}

.user-details > div {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--el-text-color-regular);
}

.username {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.email {
  font-size: 14px;
}

.register-date {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* 会员信息卡片 */
.membership-card {
  margin-bottom: 20px;
}

.membership-card.is-member {
  border-color: var(--el-color-warning-light-5);
  background: linear-gradient(135deg, var(--el-color-warning-light-9) 0%, var(--el-bg-color) 100%);
}

.membership-info {
  text-align: center;
  padding: 10px 0;
}

.membership-info .el-tag {
  margin-bottom: 16px;
}

.membership-expiry,
.remaining-days {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

/* 操作日志 */
.activity-logs-card {
  margin-top: 20px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 对话框 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-page {
    padding: 10px;
  }
  
  .page-header h2 {
    font-size: 20px;
  }
}
</style>
