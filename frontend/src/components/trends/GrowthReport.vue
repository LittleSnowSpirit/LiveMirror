<!--
成长报告展示组件
功能：
- 展示完整成长报告
- 进步/退步识别
- 总结建议展示
-->

<template>
  <div class="growth-report-container">
    <div class="header">
      <h1 class="title">📊 直播成长报告</h1>
      <div class="period">
        {{ formatDate(report.period_start) }} - {{ formatDate(report.period_end) }}
      </div>
    </div>
    
    <!-- 概览卡片 -->
    <div class="overview-cards">
      <div class="card">
        <div class="card-icon">📺</div>
        <div class="card-content">
          <div class="card-label">直播场次</div>
          <div class="card-value">{{ report.total_sessions }}</div>
        </div>
      </div>
      
      <div class="card" :class="report.overall_trend?.direction">
        <div class="card-icon">{{ getTrendIcon(report.overall_trend?.direction) }}</div>
        <div class="card-content">
          <div class="card-label">整体趋势</div>
          <div class="card-value">{{ getTrendLabel(report.overall_trend?.direction) }}</div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-icon">📈</div>
        <div class="card-content">
          <div class="card-label">变化幅度</div>
          <div class="card-value" :class="getChangeClass(report.overall_trend?.change_rate)">
            {{ formatChange(report.overall_trend?.change_rate) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 总结 -->
    <div class="summary-section">
      <h3 class="section-title">📝 整体总结</h3>
      <p class="summary-text">{{ report.summary }}</p>
    </div>
    
    <!-- 进步最大的方面 -->
    <div class="improvements-section">
      <h3 class="section-title">🎉 进步最大的方面</h3>
      <div class="improvements-list">
        <div 
          v-for="(item, index) in report.top_improvements" 
          :key="index"
          class="improvement-card"
        >
          <div class="rank-badge" :class="`rank-${index + 1}`">
            {{ index + 1 }}
          </div>
          <div class="improvement-content">
            <div class="improvement-name">{{ item.aspect }}</div>
            <div class="improvement-desc">{{ item.description }}</div>
            <div class="improvement-rate">
              提升 {{ formatChange(item.change_rate) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 需要改进的方面 -->
    <div class="areas-section" v-if="report.areas_to_work_on?.length">
      <h3 class="section-title">⚠️ 需要改进的方面</h3>
      <div class="areas-list">
        <div 
          v-for="(area, index) in report.areas_to_work_on" 
          :key="index"
          class="area-card"
          :class="area.severity"
        >
          <div class="area-header">
            <span class="area-icon">⚠️</span>
            <span class="area-name">{{ area.aspect }}</span>
            <span class="area-severity" :class="area.severity">
              {{ getSeverityLabel(area.severity) }}
            </span>
          </div>
          <p class="area-desc">{{ area.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- 建议列表 -->
    <div class="recommendations-section">
      <h3 class="section-title">💡 优化建议</h3>
      <div class="recommendations-list">
        <div 
          v-for="(rec, index) in report.recommendations" 
          :key="index"
          class="recommendation-card"
        >
          <span class="rec-number">{{ index + 1 }}</span>
          <span class="rec-text">{{ rec }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ==================== Props ====================

const props = defineProps<{
  report: {
    period_start: string;
    period_end: string;
    total_sessions: number;
    overall_trend?: {
      direction: string;
      change_rate: number;
      description: string;
    };
    top_improvements?: Array<{
      aspect: string;
      change_rate: number;
      description: string;
    }>;
    areas_to_work_on?: Array<{
      aspect: string;
      severity: string;
      description: string;
    }>;
    summary: string;
    recommendations: string[];
  };
}>();

// ==================== Methods ====================

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', { 
    month: 'short', 
    day: 'numeric' 
  });
};

const getTrendIcon = (direction?: string): string => {
  const icons = {
    'up': '📈',
    'down': '📉',
    'stable': '➡️'
  };
  return icons[direction || 'stable'];
};

const getTrendLabel = (direction?: string): string => {
  const labels = {
    'up': '上升',
    'down': '下降',
    'stable': '平稳'
  };
  return labels[direction || 'stable'];
};

const getChangeClass = (changeRate?: number): string => {
  if (!changeRate) return '';
  if (changeRate > 0) return 'positive';
  if (changeRate < 0) return 'negative';
  return '';
};

const formatChange = (changeRate?: number): string => {
  if (!changeRate) return '0%';
  const percent = (changeRate * 100).toFixed(1);
  if (changeRate > 0) return `+${percent}%`;
  if (changeRate < 0) return `${percent}%`;
  return '0%';
};

const getSeverityLabel = (severity: string): string => {
  const labels = {
    'high': '高',
    'medium': '中',
    'low': '低'
  };
  return labels[severity] || severity;
};
</script>

<style scoped>
.growth-report-container {
  width: 100%;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
}

.period {
  font-size: 14px;
  color: #999;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.card.up {
  border-left-color: #52c41a;
  background: #f6ffed;
}

.card.down {
  border-left-color: #ff4d4f;
  background: #fff1f0;
}

.card.stable {
  border-left-color: #1890ff;
  background: #e6f7ff;
}

.card-icon {
  font-size: 32px;
}

.card-content {
  flex: 1;
}

.card-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.card-value.positive {
  color: #52c41a;
}

.card-value.negative {
  color: #ff4d4f;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.summary-section {
  margin-bottom: 32px;
  padding: 16px;
  background: #e6f7ff;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.summary-text {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.improvements-section {
  margin-bottom: 32px;
}

.improvements-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.improvement-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f6ffed;
  border-radius: 8px;
  border-left: 4px solid #52c41a;
}

.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  color: #fff;
  flex-shrink: 0;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #999);
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #b87333);
}

.improvement-content {
  flex: 1;
}

.improvement-name {
  font-weight: bold;
  font-size: 15px;
  color: #333;
  margin-bottom: 4px;
}

.improvement-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.improvement-rate {
  font-size: 14px;
  color: #52c41a;
  font-weight: bold;
}

.areas-section {
  margin-bottom: 32px;
}

.areas-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.area-card {
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.area-card.high {
  background: #fff1f0;
  border-left-color: #ff4d4f;
}

.area-card.medium {
  background: #fff7e6;
  border-left-color: #fa8c16;
}

.area-card.low {
  background: #e6f7ff;
  border-left-color: #1890ff;
}

.area-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.area-icon {
  font-size: 18px;
}

.area-name {
  font-weight: bold;
  font-size: 15px;
  color: #333;
  flex: 1;
}

.area-severity {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.area-severity.high {
  background: #ffccc7;
  color: #d4380d;
}

.area-severity.medium {
  background: #ffd591;
  color: #d46b08;
}

.area-severity.low {
  background: #bae7ff;
  color: #096dd9;
}

.area-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.6;
}

.recommendations-section {
  margin-bottom: 16px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.rec-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 13px;
  flex-shrink: 0;
}

.rec-text {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}
</style>
