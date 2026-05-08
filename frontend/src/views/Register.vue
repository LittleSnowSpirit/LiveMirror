<template>
  <div class="auth-page">
    <el-card class="auth-card glass-hover">
      <p class="brand-mark gradient-text">LiveMirror</p>
      <p class="kicker">注册</p>
      <h1>创建新账号</h1>
      <p class="copy">注册后可以直接进入上传和报告流程。</p>

      <form class="auth-form" @submit.prevent="handleRegister">
        <el-input v-model="username" placeholder="用户名" autocomplete="username" />
        <el-input v-model="email" placeholder="邮箱（可选）" autocomplete="email" />
        <el-input v-model="password" type="password" placeholder="密码" autocomplete="new-password" show-password />
        <el-input v-model="confirmPassword" type="password" placeholder="确认密码" autocomplete="new-password" show-password />
        <el-button type="primary" native-type="submit" :loading="loading">注册</el-button>
      </form>

      <div class="links">
        <router-link to="/login">已经有账号，去登录</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '../api';
import { ElMessage } from 'element-plus';

const router = useRouter();
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);

async function handleRegister() {
  if (!username.value.trim() || !password.value.trim()) {
    ElMessage.warning('请输入用户名和密码');
    return;
  }

  if (password.value.length < 6) {
    ElMessage.warning('密码长度至少 6 位');
    return;
  }

  if (password.value !== confirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }

  loading.value = true;

  try {
    await register({
      username: username.value.trim(),
      password: password.value,
      email: email.value.trim() || undefined
    });

    ElMessage.success('注册成功，请登录');
    await router.push('/login');
  } catch (error: any) {
    const message = error?.response?.data?.detail || '注册失败，请稍后重试';
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
