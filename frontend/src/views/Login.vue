<template>
  <div class="auth-page">
    <el-card class="auth-card glass-hover">
      <p class="brand-mark gradient-text">LiveMirror</p>
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
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.auth-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 600px 400px at 20% 30%, rgba(167, 139, 250, 0.12), transparent),
    radial-gradient(ellipse 500px 350px at 80% 60%, rgba(240, 171, 252, 0.1), transparent),
    radial-gradient(ellipse 400px 300px at 50% 80%, rgba(139, 92, 246, 0.08), transparent);
  animation: gradientShift 12s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 0;
}

@keyframes gradientShift {
  0% {
    background:
      radial-gradient(ellipse 600px 400px at 20% 30%, rgba(167, 139, 250, 0.12), transparent),
      radial-gradient(ellipse 500px 350px at 80% 60%, rgba(240, 171, 252, 0.1), transparent),
      radial-gradient(ellipse 400px 300px at 50% 80%, rgba(139, 92, 246, 0.08), transparent);
  }
  50% {
    background:
      radial-gradient(ellipse 550px 380px at 70% 20%, rgba(167, 139, 250, 0.14), transparent),
      radial-gradient(ellipse 480px 320px at 30% 70%, rgba(240, 171, 252, 0.12), transparent),
      radial-gradient(ellipse 420px 280px at 60% 40%, rgba(139, 92, 246, 0.1), transparent);
  }
  100% {
    background:
      radial-gradient(ellipse 580px 420px at 40% 50%, rgba(167, 139, 250, 0.1), transparent),
      radial-gradient(ellipse 520px 360px at 60% 30%, rgba(240, 171, 252, 0.08), transparent),
      radial-gradient(ellipse 450px 320px at 25% 65%, rgba(139, 92, 246, 0.12), transparent);
  }
}

.auth-card {
  width: min(460px, 100%);
  border-radius: var(--radius-lg);
  position: relative;
  z-index: 1;
  background: var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  border: 1px solid var(--app-glass-border);
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
}

.auth-card:hover {
  border-color: rgba(167, 139, 250, 0.2);
  box-shadow: var(--app-glow);
}

.auth-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.brand-mark {
  font-size: var(--text-2xl);
  font-weight: 800;
  letter-spacing: 0.5px;
  text-align: center;
  margin-bottom: var(--space-1);
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

.auth-form :deep(.el-button--primary) {
  position: relative;
  overflow: hidden;
}

.auth-form :deep(.el-button--primary)::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    120deg,
    transparent 0%,
    rgba(255, 255, 255, 0.15) 50%,
    transparent 100%
  );
  transform: translateX(-100%);
  transition: none;
}

.auth-form :deep(.el-button--primary:hover)::after {
  transform: translateX(100%);
  transition: transform 0.6s ease;
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
  transition: color var(--transition-fast);
}

.links a:hover {
  color: var(--app-primary-strong);
}
</style>
