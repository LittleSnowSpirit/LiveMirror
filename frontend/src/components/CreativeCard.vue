<template>
  <el-card shadow="hover" class="creative-card">
    <!-- 素材预览 -->
    <div class="creative-preview">
      <div class="preview-placeholder" v-if="!creative.file_path">
        <el-icon :size="48"><Picture /></el-icon>
        <span>暂无预览</span>
      </div>
      <img
        v-else-if="creative.creative_type === 'image'"
        :src="creative.file_path"
        :alt="creative.name"
        class="preview-image"
      />
      <div v-else-if="creative.creative_type === 'video'" class="preview-video">
        <el-icon :size="48"><VideoCamera /></el-icon>
        <span>视频素材</span>
      </div>
      <div v-else class="preview-placeholder">
        <el-icon :size="48"><PictureFilled /></el-icon>
        <span>{{ getTypeLabel(creative.creative_type) }}</span>
      </div>
      
      <!-- 评分徽章 -->
      <div class="score-badge" :class="getScoreClass(creative.score)">
        {{ creative.score }}
      </div>
      
      <!-- 状态标签 -->
      <div class="status-tag" :class="creative.status">
        {{ getStatusLabel(creative.status) }}
      </div>
    </div>

    <!-- 素材信息 -->
    <div class="creative-info">
      <h3 class="creative-name" :title="creative.name">{{ creative.name }}</h3>
      
      <div class="creative-meta">
        <el-tag size="small" type="info">{{ getTypeLabel(creative.creative_type) }}</el-tag>
        <span class="meta-text">{{ formatDate(creative.created_at) }}</span>
      </div>

      <!-- 标签 -->
      <div class="creative-tags" v-if="creative.tags?.length">
        <el-tag
          v-for="tag in creative.tags.slice(0, 3)"
          :key="tag"
          size="small"
          class="mr-1"
        >
          {{ tag }}
        </el-tag>
        <el-tag v-if="creative.tags.length > 3" size="small">
          +{{ creative.tags.length - 3 }}
        </el-tag>
      </div>
    </div>

    <!-- 效果指标摘要 -->
    <div class="metrics-summary">
      <div class="metric-item">
        <div class="metric-label">展示</div>
        <div class="metric-value">{{ formatNumber(creative.metrics.impressions) }}</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">点击</div>
        <div class="metric-value">{{ formatNumber(creative.metrics.clicks) }}</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">CTR</div>
        <div class="metric-value" :class="getMetricClass(creative.metrics.ctr, 'ctr')">
          {{ (creative.metrics.ctr * 100).toFixed(2) }}%
        </div>
      </div>
      <div class="metric-item">
        <div class="metric-label">ROAS</div>
        <div class="metric-value" :class="getMetricClass(creative.metrics.roas, 'roas')">
          {{ creative.metrics.roas.toFixed(1) }}
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="creative-actions">
      <el-button size="small" @click="$emit('analyze', creative)">
        <el-icon><DataAnalysis /></el-icon>
        分析
      </el-button>
      <el-button size="small" @click="$emit('abtest', creative)">
        <el-icon><Connection /></el-icon>
        A/B 测试
      </el-button>
      <el-dropdown trigger="click" @command="handleCommand">
        <el-button size="small">
          <el-icon><More /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="activate" v-if="creative.status === 'draft'">
              激活
            </el-dropdown-item>
            <el-dropdown-item command="pause" v-if="creative.status === 'active'">
              暂停
            </el-dropdown-item>
            <el-dropdown-item command="resume" v-if="creative.status === 'paused'">
              恢复
            </el-dropdown-item>
            <el-dropdown-item command="archive" v-if="creative.status !== 'archived'">
              归档
            </el-dropdown-item>
            <el-dropdown-item command="delete" divided>
              <span class="text-danger">删除</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- A/B 测试标识 -->
    <div v-if="creative.ab_test_id" class="ab-test-badge">
      <el-tag size="small" type="warning">
        <el-icon><TrendCharts /></el-icon>
        A/B 测试中
      </el-tag>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import {
  Picture,
  PictureFilled,
  VideoCamera,
  DataAnalysis,
  Connection,
  More,
  TrendCharts
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  creative: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['analyze', 'abtest', 'status-change', 'delete'])

// 方法
function getTypeLabel(type) {
  const map = {
    image: '图片',
    video: '视频',
    carousel: '轮播'
  }
  return map[type] || type
}

function getStatusLabel(status) {
  const map = {
    draft: '草稿',
    active: '投放中',
    paused: '已暂停',
    archived: '已归档'
  }
  return map[status] || status
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'average'
  return 'poor'
}

function getMetricClass(value, type) {
  if (type === 'ctr') {
    if (value >= 0.02) return 'metric-good'
    if (value >= 0.01) return 'metric-average'
    return 'metric-bad'
  }
  if (type === 'roas') {
    if (value >= 3) return 'metric-good'
    if (value >= 2) return 'metric-average'
    return 'metric-bad'
  }
  return ''
}

function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K'
  }
  return num.toString()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

function handleCommand(command) {
  if (command === 'delete') {
    emit('delete', props.creative)
  } else if (['activate', 'pause', 'resume', 'archive'].includes(command)) {
    const statusMap = {
      activate: 'active',
      pause: 'paused',
      resume: 'active',
      archive: 'archived'
    }
    emit('status-change', props.creative, statusMap[command])
  }
}
</script>

<style scoped>
.creative-card {
  position: relative;
  transition: all 0.3s;
}

.creative-card:hover {
  transform: translateY(-2px);
}

.creative-preview {
  position: relative;
  height: 200px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #909399;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-video {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #909399;
}

.score-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.score-badge.excellent {
  background: linear-gradient(135deg, #67c23a, #529b2e);
}

.score-badge.good {
  background: linear-gradient(135deg, #409eff, #337ecc);
}

.score-badge.average {
  background: linear-gradient(135deg, #e6a23c, #d4882b);
}

.score-badge.poor {
  background: linear-gradient(135deg, #f56c6c, #dd4d4d);
}

.status-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.status-tag.draft {
  background: #909399;
}

.status-tag.active {
  background: #67c23a;
}

.status-tag.paused {
  background: #e6a23c;
}

.status-tag.archived {
  background: #606266;
}

.creative-info {
  padding: 15px 0 10px;
}

.creative-name {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.creative-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.meta-text {
  font-size: 12px;
  color: #909399;
}

.creative-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.mr-1 {
  margin-right: 4px;
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 15px;
}

.metric-item {
  text-align: center;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.metric-good {
  color: #67c23a;
}

.metric-average {
  color: #e6a23c;
}

.metric-bad {
  color: #f56c6c;
}

.creative-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.ab-test-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
}

.text-danger {
  color: #f56c6c;
}
</style>
