<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="brand-mark">LiveMirror</p>
      <p class="brand-sub">创作者工作室</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <el-input v-model="username" placeholder="用户名" autocomplete="username" />
        <el-input v-model="password" type="password" placeholder="密码" autocomplete="current-password" show-password />
        <el-button type="primary" native-type="submit" :loading="loading">登录</el-button>
      </form>

      <div class="links">
        <router-link to="/register">没有账号？去注册</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { login, setAuthTokens } from '../api';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
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
    const requestedRedirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/';
    const redirect = requestedRedirect.startsWith('/') ? requestedRedirect : '/';
    await router.push(redirect);
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
  padding: var(--space-6);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.brand-mark {
  font-size: 18px;
  font-weight: 600;
  color: var(--app-primary);
  text-align: center;
}

.brand-sub {
  font-size: 13px;
  color: var(--app-text-faint);
  text-align: center;
  margin-bottom: var(--space-2);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.auth-form :deep(.el-button--primary) {
  width: 100%;
}

.links {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  flex-wrap: wrap;
  font-size: 13px;
}

.links a {
  color: var(--app-text-soft);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.links a:hover {
  color: var(--app-primary);
}
</style>
