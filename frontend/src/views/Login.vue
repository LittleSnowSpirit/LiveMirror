<template>
  <div ref="pageRef" class="auth-page">
    <div class="auth-card" data-animate="scale">
      <div data-stagger>
        <p class="brand-mark" data-animate style="transition-delay: 0ms">LiveMirror</p>
        <p class="brand-sub" data-animate style="transition-delay: 80ms">创作者工作室</p>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div data-stagger>
          <div data-animate style="transition-delay: 160ms">
            <el-input v-model="username" placeholder="用户名" autocomplete="username" class="auth-input" />
          </div>
          <div data-animate style="transition-delay: 240ms">
            <el-input v-model="password" type="password" placeholder="密码" autocomplete="current-password" show-password class="auth-input" />
          </div>
          <div data-animate style="transition-delay: 320ms">
            <el-button type="primary" native-type="submit" :loading="loading">登录</el-button>
          </div>
        </div>
      </form>

      <div class="links" data-animate="fade" style="transition-delay: 400ms">
        <router-link to="/register">没有账号？去注册</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { login, setAuthTokens } from '../api';
import { ElMessage } from 'element-plus';
import { useReveal } from '../composables/useReveal';

const router = useRouter();
const route = useRoute();
const username = ref('');
const password = ref('');
const loading = ref(false);
const pageRef = ref<HTMLElement | null>(null);
const { observe } = useReveal();

onMounted(() => {
  pageRef.value?.querySelectorAll('[data-animate]').forEach(el => observe(el as HTMLElement));
});

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

.auth-input :deep(.el-input__wrapper) {
  transition: box-shadow 200ms ease, border-color 200ms ease;
}

.auth-input :deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 2px var(--app-primary-soft);
}
</style>
