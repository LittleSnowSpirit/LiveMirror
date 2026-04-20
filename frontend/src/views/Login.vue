<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <p class="kicker">登录</p>
      <h1>进入 LiveMirror</h1>
      <p class="copy">登录后可以保留任务记录，并继续查看报告和分析。</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <el-input v-model="username" placeholder="用户名" autocomplete="username" />
        <el-input v-model="password" type="password" placeholder="密码" autocomplete="current-password" show-password />
        <el-button type="primary" native-type="submit" :loading="loading">登录</el-button>
      </form>

      <div class="links">
        <router-link to="/register">没有账号，去注册</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { login, setAuthTokens } from '../api';

const router = useRouter();
const username = ref('');
const password = ref('');
const loading = ref(false);

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) {
    ElMessage.warning('请输入用户名和密码');
    return;
  }

  loading.value = true;

  try {
    const formData = new URLSearchParams();
    formData.append('username', username.value.trim());
    formData.append('password', password.value);

    const tokens = await login(formData);
    setAuthTokens(tokens);
    ElMessage.success('登录成功');
    await router.push('/');
  } catch (error: any) {
    const message = error?.response?.data?.detail || '登录失败，请检查用户名和密码';
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  place-items: center;
  min-height: calc(100vh - 69px);
  padding: 24px;
}

.auth-card {
  width: min(460px, 100%);
  border-radius: 8px;
}

.auth-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.kicker {
  font-size: 12px;
  color: var(--app-text-soft);
  text-transform: uppercase;
}

h1 {
  font-size: 24px;
}

.copy {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.links {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 14px;
}

.links a {
  color: var(--app-primary);
  text-decoration: none;
}
</style>
