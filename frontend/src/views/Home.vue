<template>
  <div class="home-container">
    <div class="home-box">
      <h1 class="title">欢迎使用 LiveMirror</h1>
      
      <div v-if="currentUser" class="user-info">
        <el-card>
          <template #header>
            <span>用户信息</span>
          </template>
          <div class="info-item">
            <span class="label">用户名:</span>
            <span class="value">{{ currentUser.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">邮箱:</span>
            <span class="value">{{ currentUser.email || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">账户状态:</span>
            <span class="value">
              <el-tag :type="currentUser.is_active ? 'success' : 'danger'">
                {{ currentUser.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </span>
          </div>
        </el-card>
      </div>
      
      <div class="actions">
        <el-button type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCurrentUser, logout } from '@/utils/auth'

const router = useRouter()
const currentUser = ref(null)

onMounted(async () => {
  try {
    currentUser.value = await getCurrentUser()
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
})

const handleLogout = () => {
  logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.home-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
}

.title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 24px;
}

.user-info {
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #666;
  font-weight: bold;
}

.value {
  color: #333;
}

.actions {
  text-align: center;
}
</style>
