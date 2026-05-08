<template>
  <div class="auth-page">
    <div class="auth-card">
      <p class="brand-mark">LiveMirror</p>
      <p class="brand-sub">创作者工作室</p>

      <form class="auth-form" @submit.prevent="handleRegister">
        <el-input v-model="username" placeholder="用户名" autocomplete="username" />
        <el-input v-model="email" placeholder="邮箱（可选）" autocomplete="email" />
        <el-input v-model="password" type="password" placeholder="密码" autocomplete="new-password" show-password />
        <el-input v-model="confirmPassword" type="password" placeholder="确认密码" autocomplete="new-password" show-password />
        <el-button type="primary" native-type="submit" :loading="loading">注册</el-button>
      </form>

      <div class="links">
        <router-link to="/login">已经有账号？去登录</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </div>
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
