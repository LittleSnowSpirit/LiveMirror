<!--
调试版本登录页面 - 用于排查跳转问题
-->
<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">LiveMirror 登录 (调试版)</h1>
      
      <div class="debug-info">
        <h3>调试信息：</h3>
        <p>当前路由：{{ currentRoute }}</p>
        <p>Router 实例：{{ router ? '✅' : '❌' }}</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="rules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="links">
          <router-link to="/register">没有账号？立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/utils/auth'

const router = useRouter()
const route = useRoute()
const loginFormRef = ref(null)
const loading = ref(false)

const currentRoute = computed(() => route.path)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3-50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  console.log('=== 开始登录流程 ===')
  console.log('loginFormRef:', loginFormRef.value)
  console.log('router:', router)
  console.log('当前路由:', route.path)
  
  if (!loginFormRef.value) {
    console.error('❌ loginFormRef is null')
    ElMessage.error('表单引用错误')
    return
  }
  
  loading.value = true
  
  try {
    console.log('1. 验证表单...')
    const valid = await loginFormRef.value.validate()
    console.log('表单验证结果:', valid)
    
    if (!valid) {
      console.error('❌ 表单验证失败')
      return
    }
    
    console.log('2. 准备登录数据...')
    const formData = new URLSearchParams()
    formData.append('username', loginForm.username)
    formData.append('password', loginForm.password)
    console.log('登录数据:', { username: loginForm.username, password: '***' })
    
    console.log('3. 发送登录请求...')
    const response = await login(formData)
    console.log('✅ 登录成功，响应:', response)
    
    console.log('4. 保存 Token...')
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    localStorage.setItem('token_type', response.token_type)
    console.log('Token 已保存')
    
    ElMessage.success('登录成功')
    
    console.log('5. 准备跳转到首页...')
    console.log('router.replace 方法:', typeof router.replace)
    
    // 使用 replace 跳转
    const result = await router.replace('/')
    console.log('✅ 跳转完成，结果:', result)
    console.log('当前路由:', route.path)
    
  } catch (error) {
    console.error('❌ 登录失败:', error)
    console.error('错误详情:', error.response?.data)
    
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  } finally {
    loading.value = false
    console.log('=== 登录流程结束 ===')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
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

.debug-info {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #666;
}

.debug-info h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.debug-info p {
  margin: 5px 0;
  font-family: monospace;
}

.login-form {
  width: 100%;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
}

.links {
  text-align: center;
  margin-top: 15px;
}

.links a {
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
}

.links a:hover {
  text-decoration: underline;
}
</style>
