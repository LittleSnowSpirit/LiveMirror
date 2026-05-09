<template>
  <div class="export-panel">
    <h3>导出与分享</h3>
    <div class="export-actions">
      <el-dropdown trigger="click" @command="handleExportPDF">
        <el-button class="press-scale" :disabled="!taskId">
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

      <el-button class="press-scale" :disabled="!taskId" @click="handleExportImage">
        导出图片
      </el-button>

      <el-button class="press-scale" type="primary" :disabled="!taskId" @click="$emit('share')">
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
  border-top: 1px solid var(--app-border);
}

.export-panel h3 {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: var(--space-3);
}

.export-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
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
