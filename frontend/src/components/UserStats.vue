<template>
  <el-card class="user-stats-card">
    <template #header>
      <div class="card-header">
        <span>使用统计</span>
        <el-icon><data-line /></el-icon>
      </div>
    </template>

    <div class="stats-grid">
      <!-- 分析次数 -->
      <div class="stat-item">
        <div class="stat-icon analysis">
          <el-icon><document-checked /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.analysis_count }}</div>
          <div class="stat-label">分析次数</div>
        </div>
      </div>

      <!-- 总时长 -->
      <div class="stat-item">
        <div class="stat-icon duration">
          <el-icon><timer /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatDuration(stats.total_duration) }}</div>
          <div class="stat-label">总时长</div>
        </div>
      </div>

      <!-- 保存报告数 -->
      <div class="stat-item">
        <div class="stat-icon reports">
          <el-icon><files /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.saved_reports }}</div>
          <div class="stat-label">保存报告</div>
        </div>
      </div>

      <!-- 总弹幕数 -->
      <div class="stat-item">
        <div class="stat-icon danmus">
          <el-icon><chat-dot-round /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stats.total_danmus) }}</div>
          <div class="stat-label">弹幕总数</div>
        </div>
      </div>

      <!-- 批量上传次数 -->
      <div class="stat-item">
        <div class="stat-icon uploads">
          <el-icon><upload-filled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.batch_uploads }}</div>
          <div class="stat-label">上传次数</div>
        </div>
      </div>
    </div>

    <!-- 趋势提示（可选） -->
    <div v-if="showTrends" class="stats-trends">
      <el-alert
        title="数据统计说明"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <ul class="trend-info">
            <li>分析次数：成功完成的弹幕分析任务总数</li>
            <li>总时长：所有分析视频的累计时长</li>
            <li>保存报告：已保存的分析报告数量</li>
            <li>弹幕总数：处理过的弹幕消息总数</li>
            <li>上传次数：批量上传文件的次数</li>
          </ul>
        </template>
      </el-alert>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  DataLine, 
  DocumentChecked, 
  Timer, 
  Files, 
  ChatDotRound, 
  UploadFilled 
} from '@element-plus/icons-vue'

// Props
const props = defineProps<{
  stats: {
    analysis_count: number
    total_duration: number
    saved_reports: number
    total_danmus: number
    batch_uploads: number
  }
  showTrends?: boolean
}>()

// 格式化时长
const formatDuration = (seconds: number): string => {
  if (seconds === 0) return '0 秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${secs}秒`
  } else {
    return `${secs}秒`
  }
}

// 格式化数字（超过 1000 使用 K 单位）
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  } else {
    return num.toString()
  }
}

// 默认值
const showTrends = computed(() => props.showTrends ?? false)
</script>

<style scoped>
.user-stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 10px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.stat-icon.analysis {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.duration {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.reports {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.danmus {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-icon.uploads {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.stats-trends {
  margin-top: 16px;
}

.trend-info {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}

.trend-info li {
  margin-bottom: 4px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-item {
    padding: 12px;
    gap: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
