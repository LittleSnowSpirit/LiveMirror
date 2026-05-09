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

    <Transition name="share-result" appear>
      <div v-if="createdShare" class="share-result">
        <div class="result-field">
          <label>分享链接</label>
          <div class="copy-row">
            <el-input :model-value="shareUrl" readonly />
            <el-button class="press-scale" @click="copyText(shareUrl)">复制</el-button>
          </div>
        </div>

        <div class="result-field">
          <label>提取码</label>
          <div class="copy-row">
            <el-input :model-value="createdShare.access_code" readonly class="access-code-input" />
            <el-button class="press-scale" @click="copyText(createdShare.access_code)">复制</el-button>
          </div>
        </div>

        <div class="qr-section">
          <Transition name="qr-scale" appear>
            <canvas v-if="createdShare" ref="qrCanvas" />
          </Transition>
        </div>

        <el-button class="press-scale" text @click="createdShare = null">创建新的分享链接</el-button>
      </div>
    </Transition>

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

.share-create :deep(.el-button--primary) {
  font-weight: 600;
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
  box-shadow: none !important;
}

.access-code-input {
  max-width: 120px;
}

.qr-section {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.qr-section canvas {
  border-radius: 6px;
  border: 1px solid var(--app-border);
  padding: 8px;
  background: var(--app-surface);
}

.share-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.share-list h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 4px;
}

.share-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface);
  transition: background 150ms ease;
}

.share-item:hover {
  background: var(--app-surface-soft);
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

/* Share result transition: fade-in + slide-up */
.share-result-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.share-result-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.share-result-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
.share-result-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* QR code scale-in transition */
.qr-scale-enter-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.qr-scale-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.qr-scale-enter-from {
  opacity: 0;
  transform: scale(0.8);
}
.qr-scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
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
