<template>
  <div class="export-panel">
    <h3>导出与分享</h3>
    <div class="export-actions">
      <el-dropdown trigger="click" @command="handleExportPDF">
        <el-button :disabled="!taskId">
          导出 PDF
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="default">默认模板</el-dropdown-item>
            <el-dropdown-item command="compact">简洁模板</el-dropdown-item>
            <el-dropdown-item command="detailed">详细模板</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-button :disabled="!taskId" @click="handleExportImage">
        导出图片
      </el-button>

      <el-button type="primary" :disabled="!taskId" @click="$emit('share')">
        分享
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { exportPDF, exportImage } from '../api';
import { ElMessage } from 'element-plus';

const props = defineProps<{
  taskId: string;
}>();

defineEmits<{
  share: [];
}>();

async function handleExportPDF(template: string) {
  try {
    await exportPDF(props.taskId, template === 'default' ? undefined : template);
    ElMessage.success('PDF 导出成功');
  } catch {
    ElMessage.error('PDF 导出失败');
  }
}

async function handleExportImage() {
  try {
    await exportImage(props.taskId);
    ElMessage.success('图片导出成功');
  } catch {
    ElMessage.error('图片导出失败');
  }
}
</script>

<style scoped>
.export-panel {
  padding: var(--space-4);
  border-top: 1px solid var(--app-glass-border);
}

.export-panel h3 {
  font-size: var(--text-sm);
  font-weight: 600;
  background: var(--app-gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: var(--space-3);
}

/* Glass buttons with hover glow */
.export-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.export-actions :deep(.el-button) {
  background: var(--app-glass-bg);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--app-glass-border);
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
}

.export-actions :deep(.el-button:hover) {
  border-color: rgba(167, 139, 250, 0.3);
  box-shadow: var(--app-glow);
  transform: translateY(-1px);
}

/* Primary share button — gradient */
.export-actions :deep(.el-button--primary) {
  background: var(--app-gradient-primary);
  border: none;
  color: #06110f;
  font-weight: 600;
}

.export-actions :deep(.el-button--primary:hover) {
  box-shadow: var(--app-glow-strong);
}

/* Dropdown trigger — gradient border on hover */
.export-actions :deep(.el-dropdown .el-button:hover) {
  border-image: var(--app-gradient-border) 1;
}

@media (max-width: 720px) {
  .export-actions {
    flex-direction: column;
  }

  .export-actions .el-button {
    width: 100%;
  }
}
</style>
