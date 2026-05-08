<template>
  <div class="profile-page">
    <el-card class="panel">
      <p class="kicker">个人中心</p>
      <h1>我的账户</h1>

      <div v-if="userStore.loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <template v-else>
        <div class="section">
          <h2>用户信息</h2>
          <dl class="info-grid">
            <div>
              <dt>用户名</dt>
              <dd>{{ user?.username || '-' }}</dd>
            </div>
            <div>
              <dt>邮箱</dt>
              <dd>{{ user?.email || '-' }}</dd>
            </div>
            <div>
              <dt>注册时间</dt>
              <dd>{{ user?.created_at ? formatTime(user.created_at) : '-' }}</dd>
            </div>
          </dl>
        </div>

        <div class="section">
          <h2>本周配额</h2>
          <div v-if="userStore.quota" class="quota-card">
            <div class="quota-ring">
              <span class="quota-number">{{ userStore.quota.used_this_week }}</span>
              <span class="quota-sep">/</span>
              <span class="quota-limit">{{ userStore.quota.weekly_limit }}</span>
              <p class="quota-label">已用次数</p>
            </div>
            <div class="quota-details">
              <p>剩余 <strong>{{ userStore.quota.remaining }}</strong> 次免费分析</p>
              <p>下次重置：{{ formatTime(userStore.quota.reset_at) }}</p>
              <el-progress
                :percentage="quotaPercentage"
                :stroke-width="8"
                :status="quotaPercentage >= 100 ? 'exception' : undefined"
              />
            </div>
          </div>
          <p v-else class="empty-text">暂无配额信息</p>
        </div>

        <div class="section">
          <h2>使用记录</h2>
          <div v-if="userStore.usageRecords.length === 0" class="empty-text">
            <el-empty description="暂无使用记录" />
          </div>
          <div v-else class="usage-list">
            <div v-for="record in userStore.usageRecords" :key="record.id" class="usage-item">
              <div class="usage-info">
                <p class="usage-filename">{{ record.filename }}</p>
                <p class="usage-meta">{{ formatTime(record.created_at) }}</p>
              </div>
              <el-tag :type="record.status === 'completed' ? 'success' : 'info'" size="small">
                {{ record.status === 'completed' ? '已完成' : record.status }}
              </el-tag>
            </div>
          </div>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { getCurrentUser, type UserProfile } from '../api';
import { useUserStore } from '../stores/user';

const userStore = useUserStore();
const user = ref<UserProfile | null>(null);

const quotaPercentage = computed(() => {
  if (!userStore.quota) return 0;
  return Math.min(100, Math.round((userStore.quota.used_this_week / userStore.quota.weekly_limit) * 100));
});

onMounted(async () => {
  try {
    user.value = await getCurrentUser();
  } catch {
    // ignore
  }
  userStore.fetchQuota();
  userStore.fetchUsageRecords();
});

function formatTime(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('zh-CN');
}
</script>

<style scoped>
.profile-page {
  padding: 28px 24px 40px;
}

.panel {
  width: min(800px, 100%);
  margin: 0 auto;
  border-radius: 8px;
  background: var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.kicker {
  font-size: 12px;
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

h1 {
  font-size: 30px;
  font-weight: 700;
}

h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
}

.section {
  padding-bottom: 20px;
  border-bottom: 1px solid var(--app-border);
}

.section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-grid {
  display: grid;
  gap: 10px;
}

.info-grid > div {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 12px;
}

dt {
  color: var(--app-text-soft);
}

dd {
  color: var(--app-text);
}

.quota-card {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 20px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-soft);
}

.quota-ring {
  display: flex;
  align-items: baseline;
  gap: 2px;
  font-family: var(--font-heading);
}

.quota-number {
  font-size: 36px;
  font-weight: 700;
  color: var(--app-primary-strong);
}

.quota-sep {
  font-size: 20px;
  color: var(--app-text-soft);
}

.quota-limit {
  font-size: 20px;
  color: var(--app-text-soft);
}

.quota-label {
  font-size: 12px;
  color: var(--app-text-faint);
  text-align: center;
  margin-top: 4px;
}

.quota-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--app-text-soft);
}

.quota-details strong {
  color: var(--app-text);
}

.empty-text {
  color: var(--app-text-soft);
}

.usage-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.usage-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-soft);
}

.usage-info {
  min-width: 0;
  flex: 1;
}

.usage-filename {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.usage-meta {
  font-size: 13px;
  color: var(--app-text-soft);
  margin-top: 2px;
}

.loading-state {
  padding: 20px 0;
}
</style>
