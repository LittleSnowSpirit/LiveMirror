<!--
话术改写对比组件
功能：
- Before/After 对比展示
- 改动点高亮
- 预期效果展示
- 一键复制
-->

<template>
  <div class="speech-rewrite-container">
    <div class="header">
      <h3 class="title">✨ 话术优化建议</h3>
      <button class="btn-copy" @click="copyAfter" v-if="rewrite.after">
        📋 复制优化版
      </button>
    </div>
    
    <!-- 对比区域 -->
    <div class="comparison" v-if="rewrite">
      <!-- Before -->
      <div class="side before">
        <div class="side-header">
          <span class="side-label">优化前</span>
          <span class="side-icon">❌</span>
        </div>
        <div class="side-content">
          <p class="text">{{ rewrite.before }}</p>
        </div>
        <div class="side-tags">
          <span 
            v-for="(issue, index) in issues" 
            :key="index"
            class="tag issue"
          >
            {{ issue.title }}
          </span>
        </div>
      </div>
      
      <!-- 箭头 -->
      <div class="arrow">
        <span>➜</span>
      </div>
      
      <!-- After -->
      <div class="side after">
        <div class="side-header">
          <span class="side-label">优化后</span>
          <span class="side-icon">✅</span>
        </div>
        <div class="side-content">
          <p class="text highlight">{{ rewrite.after }}</p>
        </div>
        <div class="side-tags">
          <span 
            v-for="(change, index) in rewrite.changes" 
            :key="index"
            class="tag change"
          >
            + {{ change }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 预期效果 -->
    <div class="expected-improvement" v-if="rewrite.expected_improvement">
      <h4 class="improvement-title">📈 预期提升</h4>
      <div class="improvement-metrics">
        <div 
          v-for="(value, key) in rewrite.expected_improvement" 
          :key="key"
          class="metric-card"
        >
          <div class="metric-icon">📊</div>
          <div class="metric-content">
            <div class="metric-label">{{ getMetricLabel(key) }}</div>
            <div class="metric-value">{{ value }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <div class="empty-icon">✅</div>
      <p>当前话术已经很好，无需改进</p>
    </div>
    
    <!-- 复制提示 -->
    <div class="copy-toast" v-if="showCopyToast">
      ✓ 已复制到剪贴板
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// ==================== Props ====================

interface Issue {
  type: string;
  severity: string;
  title: string;
  description: string;
}

interface Rewrite {
  before: string;
  after: string;
  changes: string[];
  expected_improvement: Record<string, string>;
}

const props = defineProps<{
  rewrite?: Rewrite | null;
  issues?: Issue[];
}>();

// ==================== State ====================

const showCopyToast = ref(false);

// ==================== Methods ====================

const getMetricLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    'emotion_impact': '情绪影响',
    'engagement_rate': '互动率',
    'conversion_rate': '转化率',
    'overall': '综合提升'
  };
  return labelMap[key] || key;
};

const copyAfter = () => {
  if (!props.rewrite?.after) return;
  
  navigator.clipboard.writeText(props.rewrite.after);
  showCopyToast.value = true;
  
  setTimeout(() => {
    showCopyToast.value = false;
  }, 2000);
};
</script>

<style scoped>
.speech-rewrite-container {
  width: 100%;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.btn-copy {
  padding: 6px 12px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-copy:hover {
  background: #40a9ff;
}

.comparison {
  display: flex;
  gap: 16px;
  align-items: stretch;
  margin-bottom: 20px;
}

.side {
  flex: 1;
  padding: 16px;
  border-radius: 8px;
  border: 2px solid;
}

.side.before {
  background: #fff1f0;
  border-color: #ffccc7;
}

.side.after {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.side-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.side-label {
  font-weight: bold;
  font-size: 14px;
}

.side-label.before {
  color: #ff4d4f;
}

.side-label.after {
  color: #52c41a;
}

.side-icon {
  font-size: 18px;
}

.side-content {
  margin-bottom: 12px;
  min-height: 80px;
}

.text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.text.highlight {
  color: #389e0d;
  font-weight: 500;
}

.side-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag.issue {
  background: #ffccc7;
  color: #d4380d;
}

.tag.change {
  background: #b7eb8f;
  color: #389e0d;
}

.arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #1890ff;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.expected-improvement {
  padding: 16px;
  background: #e6f7ff;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.improvement-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin: 0 0 12px 0;
}

.improvement-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #fff;
  border-radius: 6px;
}

.metric-icon {
  font-size: 20px;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 11px;
  color: #666;
}

.metric-value {
  font-size: 14px;
  font-weight: bold;
  color: #1890ff;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.copy-toast {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 8px 16px;
  background: #52c41a;
  color: #fff;
  border-radius: 4px;
  font-size: 13px;
  animation: fadeInOut 2s;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(-10px); }
  10% { opacity: 1; transform: translateY(0); }
  90% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; }
}
</style>
