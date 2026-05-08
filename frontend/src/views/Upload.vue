<template>
  <div class="upload-page">
    <h1 class="page-title">上传分析</h1>
    <p class="page-desc">选择上传文件或粘贴直播回放链接，系统会返回任务 ID，用于后续查看报告。</p>

    <el-card class="upload-card">
      <el-tabs v-model="activeTab" class="upload-tabs">
        <!-- File Upload Tab -->
        <el-tab-pane label="上传文件" name="upload">
          <div class="drop-zone" @click="fileInput?.click()">
            <input ref="fileInput" class="file-input-hidden" type="file" accept="audio/*,video/*" @change="handleFileChange" />
            <div class="drop-content">
              <span class="drop-icon">📎</span>
              <p class="drop-text">拖放文件到此处或点击选择</p>
              <p class="drop-hint">{{ fileName || '支持常见音视频格式' }}</p>
            </div>
          </div>

          <div class="actions">
            <el-button type="primary" :disabled="!selectedFile || uploading" :loading="uploading" @click="handleUpload">
              上传并创建任务
            </el-button>
            <el-button @click="router.push('/report')">去报告页</el-button>
          </div>

          <div v-if="uploading || uploadProgress > 0" class="progress-area">
            <el-progress :percentage="uploadProgress" :stroke-width="10" />
          </div>

          <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />

          <div v-if="result" class="result-box">
            <p class="result-title">上传完成</p>
            <dl>
              <div>
                <dt>任务 ID</dt>
                <dd>{{ result.task_id }}</dd>
              </div>
              <div>
                <dt>文件名</dt>
                <dd>{{ result.filename }}</dd>
              </div>
              <div>
                <dt>状态</dt>
                <dd>{{ result.status }}</dd>
              </div>
            </dl>
            <div class="actions">
              <el-button type="primary" @click="openReport">查看报告</el-button>
              <el-button @click="resetForm">继续上传</el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- Link Analysis Tab -->
        <el-tab-pane label="粘贴链接" name="link">
          <LinkInput />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { uploadFile, setStoredTaskId } from '../api';
import { ElMessage } from 'element-plus';
import LinkInput from '../components/LinkInput.vue';

const router = useRouter();
const activeTab = ref('upload');
const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const fileName = ref('');
const uploading = ref(false);
const uploadProgress = ref(0);
const errorMessage = ref('');
const result = ref<{ task_id: string; filename: string; status: string } | null>(null);

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0] || null;
  selectedFile.value = file;
  fileName.value = file?.name || '';
  errorMessage.value = '';
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请选择一个文件');
    return;
  }

  uploading.value = true;
  uploadProgress.value = 0;
  errorMessage.value = '';

  try {
    const response = await uploadFile(selectedFile.value, (progress) => {
      uploadProgress.value = progress;
    });

    setStoredTaskId(response.task_id);
    localStorage.setItem('livemirror:last-task-name', response.filename);
    window.dispatchEvent(new CustomEvent('livemirror:task-updated', { detail: response.task_id }));

    result.value = {
      task_id: response.task_id,
      filename: response.filename,
      status: response.status
    };

    ElMessage.success('上传成功');
  } catch (error: any) {
    const message = error?.response?.data?.detail || '上传失败，请稍后重试';
    errorMessage.value = message;
    ElMessage.error(message);
  } finally {
    uploading.value = false;
  }
}

function openReport() {
  if (!result.value) {
    return;
  }

  router.push({ name: 'report', params: { taskId: result.value.task_id } });
}

function resetForm() {
  selectedFile.value = null;
  fileName.value = '';
  result.value = null;
  uploadProgress.value = 0;
  errorMessage.value = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}
</script>

<style scoped>
.upload-page {
  width: min(840px, 100%);
  margin: 0 auto;
  padding: var(--space-6) var(--space-6) var(--space-10);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.page-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--app-text);
}

.page-desc {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
  margin-bottom: var(--space-2);
}

.upload-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.upload-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--space-2);
}

.drop-zone {
  border: 2px dashed var(--app-border);
  border-radius: var(--radius-lg);
  padding: var(--space-12) var(--space-6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color var(--transition-normal);
  background: var(--app-bg-deep);
}

.drop-zone:hover {
  border-color: var(--app-primary);
}

.file-input-hidden {
  display: none;
}

.drop-content {
  text-align: center;
}

.drop-icon {
  font-size: 28px;
  display: block;
  margin-bottom: var(--space-2);
}

.drop-text {
  font-size: var(--text-sm);
  color: var(--app-text);
  font-weight: 500;
}

.drop-hint {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  margin-top: var(--space-1);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.progress-area {
  padding: var(--space-2) 0;
}

.result-box {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  background: var(--app-surface);
}

.result-title {
  font-weight: 600;
  color: var(--app-text);
}

dl {
  display: grid;
  gap: var(--space-2);
}

dl > div {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: var(--space-3);
}

dt {
  color: var(--app-text-soft);
}

dd {
  color: var(--app-text);
  word-break: break-all;
}
</style>
