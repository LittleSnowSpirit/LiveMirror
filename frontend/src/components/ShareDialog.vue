<template>
  <el-dialog
    :model-value="visible"
    title="分享报告"
    width="480px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
  >
    <div v-if="!createdShare" class="share-create">
      <p class="share-hint">生成分享链接，他人可通过链接和提取码查看报告。</p>

      <div class="form-row">
        <label>有效期</label>
        <el-select v-model="expiresInDays" class="expire-select">
          <el-option :value="1" label="1 天" />
          <el-option :value="7" label="7 天" />
          <el-option :value="30" label="30 天" />
          <el-option :value="0" label="永久" />
        </el-select>
      </div>

      <el-button type="primary" :loading="creating" @click="handleCreate">
        生成分享链接
      </el-button>
    </div>

    <div v-else class="share-result">
      <div class="result-field">
        <label>分享链接</label>
        <div class="copy-row">
          <el-input :model-value="shareUrl" readonly />
          <el-button @click="copyText(shareUrl)">复制</el-button>
        </div>
      </div>

      <div class="result-field">
        <label>提取码</label>
        <div class="copy-row">
          <el-input :model-value="createdShare.access_code" readonly class="access-code-input" />
          <el-button @click="copyText(createdShare.access_code)">复制</el-button>
        </div>
      </div>

      <div class="qr-section">
        <canvas ref="qrCanvas" />
      </div>

      <el-button text @click="createdShare = null">创建新的分享链接</el-button>
    </div>

    <el-divider v-if="existingShares.length > 0" />

    <div v-if="existingShares.length > 0" class="share-list">
      <h4>已有的分享链接</h4>
      <div v-for="share in existingShares" :key="share.token" class="share-item">
        <div class="share-item-info">
          <span class="share-token">{{ share.token.slice(0, 8) }}...</span>
          <span class="share-meta">
            {{ share.view_count }} 次查看
            <template v-if="share.expires_at">
              | {{ formatDate(share.expires_at) }} 过期
            </template>
          </span>
        </div>
        <el-button type="danger" text size="small" @click="handleDelete(share.token)">
          删除
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import QRCode from 'qrcode';
import { useShareStore } from '../stores/share';
import type { ShareLink } from '../api';

const props = defineProps<{
  visible: boolean;
  taskId: string;
}>();

defineEmits<{
  'update:visible': [value: boolean];
}>();

const shareStore = useShareStore();
const expiresInDays = ref(7);
const creating = ref(false);
const createdShare = ref<ShareLink | null>(null);
const existingShares = ref<ShareLink[]>([]);
const qrCanvas = ref<HTMLCanvasElement | null>(null);

const shareUrl = ref('');

onMounted(() => {
  if (props.visible) {
    loadExistingShares();
  }
});

watch(() => props.visible, (val) => {
  if (val) {
    createdShare.value = null;
    loadExistingShares();
  }
});

async function loadExistingShares() {
  try {
    await shareStore.fetchShares();
    existingShares.value = shareStore.shares.filter((s) => s.task_id === props.taskId);
  } catch {
    existingShares.value = [];
  }
}

async function handleCreate() {
  creating.value = true;
  try {
    const share = await shareStore.createShare(
      props.taskId,
      undefined,
      expiresInDays.value || undefined,
    );
    createdShare.value = share;
    shareUrl.value = `${window.location.origin}/share/${share.token}`;
    await nextTick();
    renderQR();
  } catch {
    ElMessage.error('创建分享链接失败');
  } finally {
    creating.value = false;
  }
}

function renderQR() {
  if (!qrCanvas.value || !shareUrl.value) return;
  QRCode.toCanvas(qrCanvas.value, shareUrl.value, {
    width: 160,
    margin: 2,
    color: {
      dark: '#f0f0f0',
      light: '#141414',
    },
  });
}

async function handleDelete(token: string) {
  try {
    await shareStore.removeShare(token);
    existingShares.value = existingShares.value.filter((s) => s.token !== token);
    ElMessage.success('已删除');
  } catch {
    ElMessage.error('删除失败');
  }
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('已复制');
  } catch {
    ElMessage.error('复制失败');
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN');
}
</script>

<style scoped>
.share-create {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-hint {
  color: var(--app-text-soft);
  font-size: 14px;
  line-height: 1.6;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-row label {
  color: var(--app-text-soft);
  font-size: 14px;
  white-space: nowrap;
}

.expire-select {
  flex: 1;
}

/* Gradient primary button */
.share-create :deep(.el-button--primary) {
  background: var(--app-gradient-primary);
  border: none;
  color: #06110f;
  font-weight: 600;
  transition: box-shadow var(--transition-fast);
}

.share-create :deep(.el-button--primary:hover) {
  box-shadow: var(--app-glow-strong);
}

.share-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-field label {
  display: block;
  font-size: 13px;
  color: var(--app-text-soft);
  margin-bottom: 6px;
}

.copy-row {
  display: flex;
  gap: 8px;
}

.copy-row .el-input {
  flex: 1;
}

.copy-row :deep(.el-input__wrapper) {
  background: var(--app-glass-bg) !important;
  border: 1px solid var(--app-glass-border) !important;
  box-shadow: none !important;
}

/* Copy button — gradient treatment */
.copy-row :deep(.el-button) {
  background: var(--app-glass-bg);
  border: 1px solid var(--app-glass-border);
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}

.copy-row :deep(.el-button:hover) {
  border-color: rgba(167, 139, 250, 0.3);
  box-shadow: var(--app-glow);
}

.access-code-input {
  max-width: 120px;
}

/* QR section with glow border */
.qr-section {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.qr-section canvas {
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.15), 0 0 40px rgba(167, 139, 250, 0.08);
  border: 1px solid var(--app-glass-border);
  padding: 8px;
  background: var(--app-glass-bg);
}

/* Share list — glass items with hover glow */
.share-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.share-list h4 {
  font-size: 14px;
  font-weight: 600;
  background: var(--app-gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}

.share-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border: 1px solid var(--app-glass-border);
  border-radius: 6px;
  background: var(--app-glass-bg);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
}

.share-item:hover {
  box-shadow: var(--app-glow);
  transform: translateY(-1px);
}

.share-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.share-token {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--app-text);
}

.share-meta {
  font-size: 12px;
  color: var(--app-text-soft);
}

@media (max-width: 720px) {
  .form-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .expire-select {
    width: 100%;
  }
}
</style>
