<template>
  <div class="auth-page">
    <el-card class="auth-card">
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
import { ElMessage } from 'element-plus';
import { register } from '../api';

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
