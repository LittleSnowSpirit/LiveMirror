<template>
  <div ref="pageRef" class="profile-page">
    <el-card class="panel">
      <p class="kicker">个人中心</p>
      <h1>我的账户</h1>

      <div v-if="userStore.loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <template v-else>
        <div class="section avatar-section" data-animate="scale">
          <div class="avatar-wrapper" @click="triggerAvatarUpload">
            <img
              v-if="avatarPreview || userStore.profile?.avatar_url"
              :src="avatarPreview || userStore.profile?.avatar_url"
              alt="头像"
              class="avatar-img"
            />
            <div v-else class="avatar-placeholder">
              {{ userStore.profile?.nickname?.[0] || userStore.profile?.username?.[0] || '?' }}
            </div>
            <div class="avatar-overlay">更换头像</div>
          </div>
          <input
            ref="avatarInput"
            type="file"
            accept="image/*"
            class="hidden-input"
            @change="handleAvatarChange"
          />
        </div>

        <div class="section" data-animate>
          <h2>编辑资料</h2>
          <div class="form-grid">
            <div class="form-field">
              <label>昵称</label>
              <el-input v-model="editForm.nickname" placeholder="输入昵称" />
            </div>
            <div class="form-field">
              <label>简介</label>
              <el-input
                v-model="editForm.bio"
                type="textarea"
                :rows="3"
                placeholder="介绍一下自己"
              />
            </div>
          </div>
          <div class="form-actions">
            <el-button @click="resetForm">取消</el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
          </div>
        </div>

        <div class="section" data-animate>
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

        <div class="section" data-animate>
          <h2>本周配额</h2>
          <div v-if="userStore.quota" class="quota-card">
            <div class="quota-ring">
              <span class="quota-number">{{ quotaUsedDisplay }}</span>
              <span class="quota-sep">/</span>
              <span class="quota-limit">{{ quotaLimitDisplay }}</span>
              <p class="quota-label">已用次数</p>
            </div>
            <div class="quota-details">
              <p>剩余 <strong>{{ userStore.quota.remaining }}</strong> 次免费分析</p>
              <p>下次重置：{{ formatTime(userStore.quota.reset_at) }}</p>
              <el-progress
                :percentage="quotaPercentage"
                :stroke-width="8"
                :status="quotaPercentage >= 100 ? 'exception' : undefined"
                class="quota-progress"
              />
            </div>
          </div>
          <p v-else class="empty-text">暂无配额信息</p>
        </div>

        <div class="section" data-animate>
          <h2>使用记录</h2>
          <div v-if="userStore.usageRecords.length === 0" class="empty-text">
            <el-empty description="暂无使用记录" />
          </div>
          <div v-else class="usage-list" data-stagger>
            <div v-for="record in userStore.usageRecords" :key="record.id" class="usage-item" data-animate="fade">
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
import { useReveal } from '../composables/useReveal';
import { useCountUp } from '../composables/useCountUp';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const pageRef = ref<HTMLElement | null>(null);
const { observe } = useReveal();
const user = ref<UserProfile | null>(null);

const quotaUsedTarget = computed(() => userStore.quota?.used_this_week ?? 0);
const quotaLimitTarget = computed(() => userStore.quota?.weekly_limit ?? 0);
const quotaUsedDisplay = useCountUp(quotaUsedTarget);
const quotaLimitDisplay = useCountUp(quotaLimitTarget);
const avatarInput = ref<HTMLInputElement | null>(null);
const avatarPreview = ref('');
const saving = ref(false);
const editForm = ref({ nickname: '', bio: '' });

const quotaPercentage = computed(() => {
  if (!userStore.quota) return 0;
  return Math.min(100, Math.round((userStore.quota.used_this_week / userStore.quota.weekly_limit) * 100));
});

onMounted(async () => {
  pageRef.value?.querySelectorAll('[data-animate]').forEach(el => observe(el as HTMLElement));

  try {
    user.value = await getCurrentUser();
  } catch {
    // ignore
  }

  try {
    const profile = await userStore.fetchProfile();
    editForm.value.nickname = profile.nickname || '';
    editForm.value.bio = profile.bio || '';
  } catch {
    // ignore
  }

  userStore.fetchQuota();
  userStore.fetchUsageRecords();
});

function triggerAvatarUpload() {
  avatarInput.value?.click();
}

function handleAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    avatarPreview.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);

  userStore.uploadAvatar(file).then(() => {
    ElMessage.success('头像已更新');
  }).catch(() => {
    ElMessage.error('头像上传失败');
    avatarPreview.value = '';
  });

  input.value = '';
}

async function handleSave() {
  saving.value = true;
  try {
    await userStore.updateProfile({
      nickname: editForm.value.nickname,
      bio: editForm.value.bio,
    });
    ElMessage.success('资料已保存');
  } catch {
    ElMessage.error('保存失败');
  } finally {
    saving.value = false;
  }
}

function resetForm() {
  editForm.value.nickname = userStore.profile?.nickname || '';
  editForm.value.bio = userStore.profile?.bio || '';
}

function formatTime(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('zh-CN');
}
</script>

<style scoped>
.profile-page {
  padding: var(--space-6) var(--space-6) var(--space-10);
}

.panel {
  width: min(800px, 100%);
  margin: 0 auto;
  border-radius: 6px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.kicker {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

h1 {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--app-text);
}

h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  margin-bottom: var(--space-3);
  color: var(--app-text);
}

.section {
  padding-bottom: var(--space-5);
  border-bottom: 1px solid var(--app-border);
}

.section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.avatar-section {
  display: flex;
  justify-content: center;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  cursor: pointer;
  transition: opacity 150ms ease, transform 200ms var(--ease-out-expo, cubic-bezier(0.16, 1, 0.3, 1));
}

.avatar-wrapper:hover {
  opacity: 0.85;
  transform: scale(1.02);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--app-surface-soft);
  color: var(--app-text-soft);
  font-size: 32px;
  font-weight: 600;
  border-radius: 50%;
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 11px;
  text-align: center;
  opacity: 0;
  transition: opacity 150ms ease;
  border-radius: 0 0 50% 50%;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.hidden-input {
  display: none;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-field label {
  display: block;
  font-size: var(--text-sm);
  color: var(--app-text-soft);
  margin-bottom: var(--space-1);
}

.form-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
  margin-top: var(--space-2);
}

.info-grid {
  display: grid;
  gap: var(--space-2);
}

.info-grid > div {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: var(--space-3);
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
  gap: var(--space-6);
  padding: var(--space-5);
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface);
}

.quota-ring {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.quota-number {
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--app-text);
}

.quota-sep {
  font-size: var(--text-xl);
  color: var(--app-text-soft);
}

.quota-limit {
  font-size: var(--text-xl);
  color: var(--app-text-soft);
}

.quota-label {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  text-align: center;
  margin-top: 4px;
}

.quota-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
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
  gap: 0;
}

.usage-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--app-border);
  transition: background 150ms ease;
}

.usage-item:last-child {
  border-bottom: none;
}

.usage-item:hover {
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
  font-size: var(--text-xs);
  color: var(--app-text-soft);
  margin-top: 2px;
}

.loading-state {
  padding: var(--space-5) 0;
}

.quota-progress :deep(.el-progress-bar__inner) {
  animation: progressBar 800ms var(--ease-out-expo, cubic-bezier(0.16, 1, 0.3, 1)) forwards;
}

@keyframes progressBar {
  from { width: 0; }
}

@media (max-width: 720px) {
  .quota-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
