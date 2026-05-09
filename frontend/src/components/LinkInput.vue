<template>
  <div class="link-input-wrapper">
    <!-- URL Input Row -->
    <div class="url-input-row">
      <div class="input-container">
        <el-input
          v-model="url"
          placeholder="粘贴直播回放链接..."
          size="large"
          clearable
          :disabled="resolving || analyzing"
          @input="onUrlInput"
          @keyup.enter="handlePreview"
        >
          <template #prefix>
            <span class="input-icon">🔗</span>
          </template>
        </el-input>
        <el-button
          class="paste-btn"
          size="large"
          :disabled="resolving || analyzing"
          @click="pasteFromClipboard"
        >
          粘贴
        </el-button>
      </div>
      <el-button
        v-if="!previewData"
        type="primary"
        size="large"
        :disabled="!isValidUrl || resolving"
        :loading="resolving"
        @click="handlePreview"
      >
        解析链接
      </el-button>
    </div>

    <!-- Platform Tag -->
    <Transition name="slide-from-left">
      <div v-if="detectedPlatform" class="platform-tag-row">
        <span
          class="platform-tag"
          :class="detectedPlatform"
        >
          {{ platformLabel }}
        </span>
      </div>
    </Transition>

    <!-- Error Message -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="true"
      show-icon
      @close="errorMessage = ''"
    />

    <!-- Preview Card -->
    <Transition name="scale-in">
      <div v-if="previewData && !previewData.error" class="preview-card">
      <div class="preview-thumb">
        <img
          v-if="previewData.thumbnail_url"
          :src="previewData.thumbnail_url"
          :alt="previewData.title"
          loading="lazy"
          @error="onThumbError"
        />
        <div v-else class="thumb-placeholder">🎬</div>
      </div>
      <div class="preview-info">
        <p class="preview-title">{{ previewData.title || '未知标题' }}</p>
        <p class="preview-meta">
          <span v-if="previewData.uploader">{{ previewData.uploader }}</span>
          <span v-if="previewData.uploader && formattedDuration"> · </span>
          <span v-if="formattedDuration">{{ formattedDuration }}</span>
        </p>
        <el-button
          type="primary"
          size="large"
          :loading="analyzing"
          :disabled="analyzing"
          @click="handleAnalyze"
        >
          开始分析
        </el-button>
      </div>
    </div>
    </Transition>

    <!-- Analyzing Progress -->
    <div v-if="analyzing" class="progress-panel">
      <div class="progress-steps">
        <div
          v-for="(step, index) in steps"
          :key="step.label"
          class="progress-step"
          :class="{
            active: index === currentStepIndex,
            done: index < currentStepIndex,
          }"
        >
          <span class="step-indicator">{{ index < currentStepIndex ? '✓' : index + 1 }}</span>
          <span class="step-label">{{ step.label }}</span>
        </div>
      </div>
      <el-progress
        :percentage="analysisProgress"
        :stroke-width="8"
        :status="analysisProgress >= 100 ? 'success' : undefined"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { getLinkInfo, analyzeLink, getTaskStatus, setStoredTaskId } from '../api';
import type { LinkInfo } from '../api';

const emit = defineEmits<{
  (e: 'started', taskId: string): void;
  (e: 'completed', taskId: string): void;
  (e: 'error', message: string): void;
}>();

const router = useRouter();

const url = ref('');
const resolving = ref(false);
const analyzing = ref(false);
const previewData = ref<LinkInfo | null>(null);
const errorMessage = ref('');
const thumbBroken = ref(false);
const analysisProgress = ref(0);
const currentStepIndex = ref(0);
let pollTimer: ReturnType<typeof setInterval> | null = null;

const steps = [
  { label: '下载中' },
  { label: '转写中' },
  { label: '分析中' },
  { label: '完成' },
];

const URL_RE = /^https?:\/\/.+/i;

const isValidUrl = computed(() => URL_RE.test(url.value.trim()));

const detectedPlatform = computed(() => {
  const u = url.value.trim().toLowerCase();
  if (!u) return '';
  if (u.includes('douyin.com') || u.includes('iesdouyin.com')) return 'douyin';
  if (u.includes('bilibili.com') || u.includes('b23.tv')) return 'bilibili';
  return '';
});

const platformLabel = computed(() => {
  if (detectedPlatform.value === 'douyin') return '抖音';
  if (detectedPlatform.value === 'bilibili') return 'B站';
  return '';
});

const formattedDuration = computed(() => {
  if (!previewData.value?.duration) return '';
  const s = Math.round(previewData.value.duration);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return m > 0 ? `${m}分${sec}秒` : `${sec}秒`;
});

function onUrlInput() {
  previewData.value = null;
  errorMessage.value = '';
  thumbBroken.value = false;
  stopPolling();
}

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) {
      url.value = text.trim();
      onUrlInput();
    }
  } catch {
    ElMessage.warning('无法读取剪贴板，请手动粘贴');
  }
}

async function handlePreview() {
  if (!isValidUrl.value) {
    errorMessage.value = '请输入有效的链接地址';
    return;
  }
  resolving.value = true;
  errorMessage.value = '';
  previewData.value = null;

  try {
    const info = await getLinkInfo(url.value.trim());
    if (info.error) {
      errorMessage.value = info.error;
    } else {
      previewData.value = info;
      thumbBroken.value = false;
    }
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || '链接解析失败，请检查链接是否正确';
  } finally {
    resolving.value = false;
  }
}

async function handleAnalyze() {
  if (!url.value.trim()) return;
  analyzing.value = true;
  errorMessage.value = '';
  analysisProgress.value = 0;
  currentStepIndex.value = 0;

  try {
    const { task_id } = await analyzeLink(url.value.trim());
    setStoredTaskId(task_id);
    localStorage.setItem('livemirror:last-task-name', previewData.value?.title || '链接分析');
    window.dispatchEvent(new CustomEvent('livemirror:task-updated', { detail: task_id }));
    emit('started', task_id);
    startPolling(task_id);
  } catch (err: any) {
    analyzing.value = false;
    const msg = err?.response?.data?.detail || '分析任务创建失败';
    errorMessage.value = msg;
    emit('error', msg);
  }
}

function startPolling(taskId: string) {
  stopPolling();
  pollTimer = setInterval(async () => {
    try {
      const res = await getTaskStatus(taskId);
      const task = res.task;
      analysisProgress.value = task.progress ?? 0;

      const stepMap: Record<string, number> = {
        pending: 0,
        downloading: 0,
        transcribing: 1,
        processing: 2,
        analyzing: 2,
        completed: 3,
      };
      currentStepIndex.value = stepMap[task.status] ?? 0;

      if (task.status === 'completed') {
        stopPolling();
        analyzing.value = false;
        analysisProgress.value = 100;
        currentStepIndex.value = 3;
        ElMessage.success('分析完成，正在跳转报告页...');
        emit('completed', taskId);
        setTimeout(() => {
          router.push({ name: 'report', params: { taskId } });
        }, 1200);
      } else if (task.status === 'failed') {
        stopPolling();
        analyzing.value = false;
        const msg = task.error_message || '分析失败';
        errorMessage.value = msg;
        emit('error', msg);
      }
    } catch {
      // ignore polling errors, will retry
    }
  }, 2000);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function onThumbError(e: Event) {
  (e.target as HTMLImageElement).style.display = 'none';
  thumbBroken.value = true;
}

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<style scoped>
.link-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.url-input-row {
  display: flex;
  gap: 10px;
  align-items: stretch;
}

.input-container {
  display: flex;
  flex: 1;
  gap: 8px;
}

.input-container .el-input {
  flex: 1;
}

.input-container :deep(.el-input__wrapper) {
  box-shadow: none !important;
}

.input-icon {
  font-size: 16px;
}

.paste-btn {
  flex-shrink: 0;
}

.platform-tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  border: none;
}

.platform-tag.douyin {
  background: rgba(254, 44, 85, 0.12);
  color: #fe2c55;
}

.platform-tag.bilibili {
  background: rgba(0, 161, 214, 0.12);
  color: #00a1d6;
}

.preview-card {
  display: flex;
  gap: 16px;
  padding: 14px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface);
}

.preview-thumb {
  flex-shrink: 0;
  width: 160px;
  height: 90px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--app-surface-soft);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  font-size: 32px;
  opacity: 0.4;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.preview-meta {
  font-size: 14px;
  color: var(--app-text-soft);
}

.preview-info .el-button {
  align-self: flex-start;
  margin-top: 4px;
}

.progress-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface);
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
  opacity: 0.35;
  transition: opacity 150ms ease;
}

.progress-step.active,
.progress-step.done {
  opacity: 1;
}

.step-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--app-surface-soft);
  color: var(--app-text-soft);
  font-size: 14px;
  font-weight: 700;
}

@keyframes stepBounce {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.progress-step.active .step-indicator {
  background: var(--app-primary);
  color: #fff;
  animation: stepBounce 400ms var(--ease-out-back, cubic-bezier(0.34, 1.56, 0.64, 1));
}

.progress-step.done .step-indicator {
  background: var(--app-success);
  color: #fff;
}

.step-label {
  font-size: 12px;
  color: var(--app-text-soft);
}

.progress-step.active .step-label {
  color: var(--app-text);
  font-weight: 600;
}

/* Responsive */
@media (max-width: 720px) {
  .url-input-row {
    flex-direction: column;
  }

  .input-container {
    flex-direction: column;
  }

  .paste-btn {
    align-self: flex-end;
  }

  .preview-card {
    flex-direction: column;
  }

  .preview-thumb {
    width: 100%;
    height: 180px;
  }

  .progress-steps {
    flex-wrap: wrap;
  }

  .progress-step {
    min-width: 60px;
  }
}

/* Transitions */
.scale-in-enter-active {
  transition: opacity 300ms var(--ease-out-expo, cubic-bezier(0.16, 1, 0.3, 1)), transform 300ms var(--ease-out-expo, cubic-bezier(0.16, 1, 0.3, 1));
}

.scale-in-enter-from {
  opacity: 0;
  transform: scale(0.96);
}

.slide-from-left-enter-active {
  transition: opacity 250ms ease, transform 250ms ease;
}

.slide-from-left-enter-from {
  opacity: 0;
  transform: translateX(-12px);
}
</style>
