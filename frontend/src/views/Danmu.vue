<template>
  <div class="danmu-page">
    <!-- Upload & History mode -->
    <el-card v-if="!activeBatchId" class="panel">
      <p class="kicker">弹幕分析</p>
      <h1>弹幕数据分析</h1>
      <p class="copy">上传弹幕文件（CSV/JSON），系统将进行情感分析、关键词提取和密度统计。</p>

      <el-tabs v-model="activeTab" class="mode-tabs">
        <!-- Upload Tab -->
        <el-tab-pane label="上传弹幕" name="upload">
          <div
            class="drop-zone"
            :class="{ dragover: isDragover }"
            @dragover.prevent="isDragover = true"
            @dragleave="isDragover = false"
            @drop.prevent="handleDrop"
          >
            <div class="drop-icon">+</div>
            <p class="drop-text">拖拽文件到此处，或</p>
            <label class="drop-label">
              <span>选择文件</span>
              <input
                ref="fileInput"
                type="file"
                accept=".csv,.json"
                class="file-input-hidden"
                @change="handleFileChange"
              />
            </label>
            <p class="drop-hint">支持 .csv 和 .json 格式</p>
          </div>

          <div v-if="selectedFile" class="selected-file">
            <span class="file-name">{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
            <el-button type="danger" text size="small" @click="clearFile">移除</el-button>
          </div>

          <el-progress
            v-if="uploading"
            :percentage="uploadProgress"
            :stroke-width="10"
            class="upload-progress"
          />

          <el-alert
            v-if="errorMessage"
            :title="errorMessage"
            type="error"
            :closable="false"
            show-icon
          />

          <div v-if="uploadResult" class="result-box">
            <p class="result-title">上传完成</p>
            <div class="result-stats">
              <div class="result-stat">
                <span class="stat-num">{{ uploadResult.total_count }}</span>
                <span class="stat-desc">总条数</span>
              </div>
              <div class="result-stat success">
                <span class="stat-num">{{ uploadResult.success_count }}</span>
                <span class="stat-desc">成功</span>
              </div>
              <div class="result-stat danger">
                <span class="stat-num">{{ uploadResult.failed_count }}</span>
                <span class="stat-desc">失败</span>
              </div>
            </div>
            <div class="actions">
              <el-button type="primary" :loading="analyzing" @click="startAnalysis">
                开始分析
              </el-button>
              <el-button @click="resetUpload">继续上传</el-button>
            </div>
          </div>

          <div class="actions" v-if="!uploadResult">
            <el-button
              type="primary"
              :disabled="!selectedFile || uploading"
              :loading="uploading"
              @click="handleUpload"
            >
              上传弹幕文件
            </el-button>
          </div>
        </el-tab-pane>

        <!-- History Tab -->
        <el-tab-pane label="历史批次" name="history">
          <div v-if="loadingBatches" class="loading-state">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="batches.length === 0" class="empty-state">
            <el-empty description="暂无弹幕批次" />
          </div>

          <el-table
            v-else
            :data="batches"
            stripe
            class="batch-table"
            @row-click="goToDetail"
          >
            <el-table-column prop="filename" label="文件名" min-width="180" show-overflow-tooltip />
            <el-table-column prop="total_count" label="弹幕数" width="100" align="center" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="batchStatusType(row.status)" size="small">
                  {{ batchStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="上传时间" width="180" align="center">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button type="primary" text size="small" @click.stop="goToDetail(row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Detail view -->
    <DanmuDetail
      v-if="activeBatchId"
      :batch-id="activeBatchId"
      @back="activeBatchId = ''"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import {
  uploadDanmuFile,
  getDanmuBatches,
  triggerDanmuAnalysis,
  type DanmuBatch,
} from '../api';
import DanmuDetail from '../components/DanmuDetail.vue';

const route = useRoute();
const router = useRouter();

const activeTab = ref('upload');
const activeBatchId = ref('');

// Upload state
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const isDragover = ref(false);
const uploading = ref(false);
const uploadProgress = ref(0);
const errorMessage = ref('');
const uploadResult = ref<{ batch_id: string; total_count: number; success_count: number; failed_count: number } | null>(null);
const analyzing = ref(false);

// History state
const batches = ref<DanmuBatch[]>([]);
const loadingBatches = ref(false);

// Check route param for direct detail access
onMounted(() => {
  const batchId = route.params.batchId as string;
  if (batchId) {
    activeBatchId.value = batchId;
  }
});

watch(() => route.params.batchId, (id) => {
  if (id) {
    activeBatchId.value = id as string;
  }
});

// Load batches when switching to history tab
watch(activeTab, (tab) => {
  if (tab === 'history') {
    loadBatches();
  }
});

async function loadBatches() {
  loadingBatches.value = true;
  try {
    batches.value = await getDanmuBatches();
  } catch {
    batches.value = [];
  } finally {
    loadingBatches.value = false;
  }
}

function handleDrop(event: DragEvent) {
  isDragover.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    selectFile(file);
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0] || null;
  if (file) {
    selectFile(file);
  }
}

function selectFile(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase();
  if (ext !== 'csv' && ext !== 'json') {
    ElMessage.warning('仅支持 .csv 和 .json 文件');
    return;
  }
  selectedFile.value = file;
  errorMessage.value = '';
  uploadResult.value = null;
}

function clearFile() {
  selectedFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function handleUpload() {
  if (!selectedFile.value) return;

  uploading.value = true;
  uploadProgress.value = 0;
  errorMessage.value = '';

  try {
    const result = await uploadDanmuFile(selectedFile.value, (progress) => {
      uploadProgress.value = progress;
    });
    uploadResult.value = result;
    ElMessage.success('上传成功');
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || '上传失败，请稍后重试';
  } finally {
    uploading.value = false;
  }
}

async function startAnalysis() {
  if (!uploadResult.value) return;

  analyzing.value = true;
  try {
    await triggerDanmuAnalysis(uploadResult.value.batch_id);
    ElMessage.success('分析已启动');
    router.push({ name: 'danmu-detail', params: { batchId: uploadResult.value.batch_id } });
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '启动分析失败');
  } finally {
    analyzing.value = false;
  }
}

function resetUpload() {
  selectedFile.value = null;
  uploadResult.value = null;
  uploadProgress.value = 0;
  errorMessage.value = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function goToDetail(row: DanmuBatch) {
  router.push({ name: 'danmu-detail', params: { batchId: row.batch_id } });
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatTime(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('zh-CN');
}

function batchStatusType(status: string) {
  const map: Record<string, string> = {
    pending: 'info',
    uploaded: 'info',
    analyzing: 'warning',
    completed: 'success',
    failed: 'danger',
  };
  return (map[status] || 'info') as any;
}

function batchStatusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待处理',
    uploaded: '已上传',
    analyzing: '分析中',
    completed: '已完成',
    failed: '失败',
  };
  return map[status] || status;
}
</script>

<style scoped>
.danmu-page {
  padding: var(--space-6) var(--space-6) var(--space-10);
}

.panel {
  width: min(960px, 100%);
  margin: 0 auto;
  border-radius: var(--radius-lg);
  background:
    linear-gradient(135deg, rgba(167, 139, 250, 0.06), transparent 38%),
    var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.kicker {
  font-size: var(--text-xs);
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

h1 {
  font-size: var(--text-4xl);
  font-weight: 820;
  letter-spacing: 0;
}

.copy {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.mode-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--space-2);
}

/* Drop zone */
.drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-10) var(--space-6);
  border: 2px dashed var(--app-border-strong);
  border-radius: var(--radius-lg);
  background: var(--app-bg-deep);
  transition: border-color var(--transition-fast), background var(--transition-fast);
  cursor: pointer;
}

.drop-zone:hover,
.drop-zone.dragover {
  border-color: var(--app-primary);
  background: var(--app-primary-soft);
}

.drop-icon {
  font-size: 48px;
  line-height: 1;
  color: var(--app-text-faint);
  font-weight: 300;
}

.drop-text {
  color: var(--app-text-soft);
}

.drop-label {
  display: inline-flex;
  align-items: center;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--app-primary);
  color: #06110f;
  font-weight: 600;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.drop-label:hover {
  background: var(--app-primary-strong);
}

.file-input-hidden {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.drop-hint {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
}

/* Selected file */
.selected-file {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  background: var(--app-surface-soft);
}

.file-name {
  font-weight: 600;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.upload-progress {
  margin-top: var(--space-2);
}

/* Result box */
.result-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-lg);
  background: var(--app-surface-soft);
}

.result-title {
  font-weight: 600;
  color: var(--app-primary-strong);
}

.result-stats {
  display: flex;
  gap: var(--space-6);
}

.result-stat {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-num {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--app-text);
}

.result-stat.success .stat-num {
  color: var(--app-success);
}

.result-stat.danger .stat-num {
  color: var(--app-danger);
}

.stat-desc {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* History */
.batch-table {
  width: 100%;
}

.batch-table :deep(.el-table__row) {
  cursor: pointer;
}

.loading-state {
  padding: var(--space-5) 0;
}

.empty-state {
  padding: var(--space-10) 0;
}

@media (max-width: 720px) {
  .result-stats {
    gap: var(--space-4);
  }
}
</style>
