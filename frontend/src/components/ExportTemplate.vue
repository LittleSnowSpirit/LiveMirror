<template>
  <div class="export-template-card">
    <div class="template-header">
      <div class="template-icon">
        <span v-if="template.format === 'excel'">📊</span>
        <span v-else-if="template.format === 'word'">📄</span>
        <span v-else-if="template.format === 'powerpoint'">📽</span>
        <span v-else-if="template.format === 'pdf'">📕</span>
        <span v-else-if="template.format === 'csv'">📋</span>
        <span v-else-if="template.format === 'json'">📝</span>
        <span v-else>⚙</span>
      </div>
      <div class="template-info">
        <h3>{{ template.name }}</h3>
        <p class="template-description">{{ template.description || '暂无描述' }}</p>
      </div>
      <div class="template-status">
        <span :class="['badge', template.enabled ? 'enabled' : 'disabled']">
          {{ template.enabled ? '已启用' : '已禁用' }}
        </span>
      </div>
    </div>

    <div class="template-body">
      <div class="template-meta">
        <div class="meta-item">
          <span class="meta-label">格式</span>
          <span class="meta-value">{{ formatLabel(template.format) }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">创建时间</span>
          <span class="meta-value">{{ formatDateTime(template.created_at) }}</span>
        </div>
      </div>

      <div class="template-config" v-if="showConfig">
        <h4>模板配置</h4>
        <pre>{{ JSON.stringify(template.config, null, 2) }}</pre>
      </div>
    </div>

    <div class="template-actions">
      <button class="btn btn-sm btn-primary" @click="$emit('use', template)">
        🚀 使用此模板
      </button>
      <button class="btn btn-sm btn-secondary" @click="$emit('view', template)">
        👁 查看详情
      </button>
      <button class="btn btn-sm btn-secondary" @click="$emit('edit', template)">
        ✏ 编辑
      </button>
      <button class="btn btn-sm btn-danger" @click="handleDelete">
        🗑 删除
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExportTemplateCard',
  props: {
    template: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showConfig: false
    }
  },
  methods: {
    formatLabel(format) {
      const labels = {
        excel: 'Excel',
        word: 'Word',
        powerpoint: 'PowerPoint',
        pdf: 'PDF',
        csv: 'CSV',
        json: 'JSON',
        custom: '自定义'
      }
      return labels[format] || format
    },

    formatDateTime(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN')
    },

    handleDelete() {
      if (confirm(`确定要删除模板 "${this.template.name}" 吗？`)) {
        this.$emit('delete', this.template.id)
      }
    }
  }
}
</script>

<style scoped>
.export-template-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  background: #fafafa;
  transition: all 0.3s;
}

.export-template-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  margin-bottom: 15px;
}

.template-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
}

.template-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.template-description {
  margin: 0;
  font-size: 13px;
  color: #666;
}

.template-status {
  flex-shrink: 0;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge.enabled {
  background: #52c41a;
  color: #fff;
}

.badge.disabled {
  background: #d9d9d9;
  color: #666;
}

.template-body {
  margin-bottom: 15px;
}

.template-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
}

.meta-value {
  font-size: 13px;
  color: #333;
}

.template-config {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.template-config h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #666;
}

.template-config pre {
  margin: 0;
  font-size: 12px;
  color: #333;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.template-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #d9d9d9;
}

.btn-secondary:hover {
  background: #e6e6e6;
}

.btn-danger {
  background: #ff4d4f;
  color: #fff;
}

.btn-danger:hover {
  background: #ff7875;
}
</style>
