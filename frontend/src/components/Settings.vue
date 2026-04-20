<template>
  <el-card class="settings-card">
    <template #header>
      <div class="card-header">
        <span>账号设置</span>
        <el-icon><setting /></el-icon>
      </div>
    </template>

    <el-form label-position="top" size="default">
      <!-- 修改密码 -->
      <el-form-item label="修改密码">
        <div class="password-form">
          <el-form-item>
            <el-input
              v-model="passwordForm.old_password"
              type="password"
              placeholder="请输入当前密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleChangePassword"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              placeholder="请输入新密码（6-50 位）"
              :prefix-icon="Key"
              show-password
              :minlength="6"
              :maxlength="50"
              @keyup.enter="handleChangePassword"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="passwordForm.confirm_password"
              type="password"
              placeholder="请确认新密码"
              :prefix-icon="Key"
              show-password
              :minlength="6"
              :maxlength="50"
              @keyup.enter="handleChangePassword"
            />
          </el-form-item>
          
          <el-button
            type="primary"
            :loading="changingPassword"
            @click="handleChangePassword"
          >
            <el-icon><check /></el-icon>
            修改密码
          </el-button>
        </div>
      </el-form-item>

      <el-divider />

      <!-- 修改头像 -->
      <el-form-item label="修改头像">
        <div class="avatar-form">
          <el-button type="primary" plain @click="handleAvatarChange">
            <el-icon><picture /></el-icon>
            更换头像
          </el-button>
          <span class="form-tip">支持图片 URL 或本地上传</span>
        </div>
      </el-form-item>

      <el-divider />

      <!-- 退出登录 -->
      <el-form-item label="账户操作">
        <div class="logout-section">
          <el-button
            type="danger"
            plain
            @click="handleLogout"
          >
            <el-icon><switch-button /></el-icon>
            退出登录
          </el-button>
          <span class="form-tip">退出后将返回登录页面</span>
        </div>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Setting, 
  Lock, 
  Key, 
  Check, 
  Picture, 
  SwitchButton 
} from '@element-plus/icons-vue'

// Emits
const emit = defineEmits<{
  (e: 'password-change', oldPassword: string, newPassword: string): Promise<boolean>
  (e: 'avatar-change'): void
  (e: 'logout'): void
}>()

// 状态
const changingPassword = ref(false)

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 修改密码
const handleChangePassword = async () => {
  // 验证表单
  if (!passwordForm.old_password) {
    ElMessage.warning('请输入当前密码')
    return
  }
  
  if (!passwordForm.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  
  if (passwordForm.new_password.length < 6 || passwordForm.new_password.length > 50) {
    ElMessage.warning('新密码长度必须在 6-50 位之间')
    return
  }
  
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.old_password === passwordForm.new_password) {
    ElMessage.warning('新密码不能与当前密码相同')
    return
  }
  
  changingPassword.value = true
  
  try {
    const success = await emit('password-change', passwordForm.old_password, passwordForm.new_password)
    
    if (success) {
      // 清空表单
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    changingPassword.value = false
  }
}

// 修改头像
const handleAvatarChange = () => {
  emit('avatar-change')
}

// 退出登录
const handleLogout = () => {
  emit('logout')
}
</script>

<style scoped>
.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 400px;
}

.password-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.avatar-form {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-tip {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.logout-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .password-form {
    max-width: 100%;
  }
  
  .avatar-form,
  .logout-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
