<template>
  <div class="upload-page">
    <el-card class="panel">
      <p class="kicker">上传</p>
      <h1>创建分析任务</h1>
      <p class="copy">请选择音视频文件，系统会返回任务 ID，用于后续查看报告。</p>

      <div class="picker">
        <input ref="fileInput" class="file-input" type="file" accept="audio/*,video/*" @change="handleFileChange" />
        <div class="file-meta">
          <p class="file-name">{{ fileName || '还没有选择文件' }}</p>
          <p class="file-hint">支持常见音视频格式。</p>
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" :disabled="!selectedFile || uploading" :loading="uploading" @click="handleUpload">
          上传并创建任务
        </el-button>
        <el-button @click="router.push('/report')">去报告页</el-button>
      </div>

      <el-progress v-if="uploading || uploadProgress > 0" :percentage="uploadProgress" :stroke-width="10" />

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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { uploadFile, setStoredTaskId } from '../api';

const router = useRouter();
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
  padding: 28px 24px 40px;
}

.panel {
  width: min(840px, 100%);
  margin: 0 auto;
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(45, 212, 191, 0.08), transparent 38%),
    var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.kicker {
  font-size: 12px;
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

h1 {
  font-size: 32px;
  font-weight: 820;
  letter-spacing: 0;
}

.copy,
.file-hint {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.picker {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  border: 1px dashed var(--app-border-strong);
  border-radius: 8px;
  background: var(--app-bg-deep);
}

.file-input {
  max-width: 280px;
  color: var(--app-text-soft);
}

.file-name {
  font-weight: 600;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.result-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-soft);
}

.result-title {
  font-weight: 600;
  color: var(--app-primary-strong);
}

dl {
  display: grid;
  gap: 10px;
}

dl > div {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 12px;
}

dt {
  color: var(--app-text-soft);
}

dd {
  color: var(--app-text);
  word-break: break-all;
}

@media (max-width: 640px) {
  .picker {
    flex-direction: column;
    align-items: stretch;
  }

  .file-input {
    max-width: 100%;
  }
}
</style>
