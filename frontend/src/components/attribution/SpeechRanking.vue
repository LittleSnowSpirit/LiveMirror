<!--
话术影响力排行榜组件
功能：
- Top N 话术卡片展示
- 按综合评分排序
- 颜色编码话术类型
- 点击展开查看详情和建议
-->

<template>
  <div class="speech-ranking-container">
    <div class="header">
      <h3 class="title">📊 话术影响力排行榜</h3>
      <div class="filters">
        <select v-model="sortBy" class="filter-select">
          <option value="overall">综合评分</option>
          <option value="emotion">情绪影响</option>
          <option value="engagement">互动影响</option>
        </select>
      </div>
    </div>
    
    <div class="ranking-list">
      <div 
        v-for="(speech, index) in sortedSpeeches" 
        :key="speech.speech_id"
        class="speech-card"
        :class="{ 'expanded': expandedId === speech.speech_id }"
        @click="toggleExpand(speech.speech_id)"
      >
        <!-- 排名徽章 -->
        <div class="rank-badge" :class="getRankClass(index)">
          {{ index + 1 }}
        </div>
        
        <!-- 主要内容 -->
        <div class="speech-content">
          <div class="speech-header">
            <span class="speech-type" :class="getTypeClass(speech.speech_type)">
              {{ getTypeName(speech.speech_type) }}
            </span>
            <span class="confidence-tag" v-if="speech.confidence >= 0.8">
              高置信
            </span>
          </div>
          
          <p class="speech-text">{{ speech.speech_content }}</p>
          
          <div class="speech-meta">
            <span class="time-range">
              {{ formatTime(speech.start_time) }} - {{ formatTime(speech.end_time) }}
            </span>
            <span class="score" :class="getScoreClass(speech.overall_score)">
              {{ speech.overall_score }}分
            </span>
          </div>
          
          <!-- 进度条 -->
          <div class="score-bar">
            <div 
              class="score-fill" 
              :class="getScoreClass(speech.overall_score)"
              :style="{ width: speech.overall_score + '%' }"
            ></div>
          </div>
          
          <!-- 详细指标 -->
          <div class="metrics" v-if="expandedId === speech.speech_id">
            <div class="metric-item">
              <span class="metric-label">情绪影响</span>
              <div class="metric-bar">
                <div 
                  class="metric-fill emotion"
                  :style="{ width: speech.emotion_impact * 100 + '%' }"
                ></div>
              </div>
              <span class="metric-value">{{ (speech.emotion_impact * 100).toFixed(0) }}%</span>
            </div>
            
            <div class="metric-item">
              <span class="metric-label">互动影响</span>
              <div class="metric-bar">
                <div 
                  class="metric-fill engagement"
                  :style="{ width: speech.engagement_impact * 100 + '%' }"
                ></div>
              </div>
              <span class="metric-value">{{ (speech.engagement_impact * 100).toFixed(0) }}%</span>
            </div>
            
            <!-- 问题诊断 -->
            <div class="issues-section" v-if="speech.issues?.length">
              <h4>⚠️ 问题诊断</h4>
              <ul class="issues-list">
                <li v-for="(issue, i) in speech.issues" :key="i">
                  {{ issue }}
                </li>
              </ul>
            </div>
            
            <!-- 优化建议 -->
            <div class="suggestions-section" v-if="speech.suggestions?.length">
              <h4>💡 优化建议</h4>
              <ul class="suggestions-list">
                <li v-for="(suggestion, i) in speech.suggestions" :key="i">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
            
            <!-- 操作按钮 -->
            <div class="actions">
              <button class="btn btn-primary" @click.stop="copySpeech(speech.speech_content)">
                📋 复制话术
              </button>
              <button class="btn btn-secondary" @click.stop="viewDetail(speech)">
                🔍 查看详情
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!sortedSpeeches.length">
      <div class="empty-icon">📝</div>
      <p>暂无话术数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// ==================== Types ====================

interface SpeechData {
  speech_id: string;
  speech_type: string;
  speech_content: string;
  start_time: number;
  end_time: number;
  overall_score: number;
  emotion_impact: number;
  engagement_impact: number;
  confidence: number;
  issues?: string[];
  suggestions?: string[];
}

// ==================== Props & Emits ====================

const props = defineProps<{
  speeches: SpeechData[];
  topN?: number;
}>();

const emit = defineEmits<{
  (e: 'speech-click', speech: SpeechData): void;
  (e: 'copy', content: string): void;
}>();

// ==================== State ====================

const expandedId = ref<string | null>(null);
const sortBy = ref<'overall' | 'emotion' | 'engagement'>('overall');

// ==================== Computed ====================

const sortedSpeeches = computed(() => {
  let speeches = [...props.speeches];
  
  // 排序
  speeches.sort((a, b) => {
    if (sortBy.value === 'overall') {
      return b.overall_score - a.overall_score;
    } else if (sortBy.value === 'emotion') {
      return b.emotion_impact - a.emotion_impact;
    } else {
      return b.engagement_impact - a.engagement_impact;
    }
  });
  
  // 限制数量
  return speeches.slice(0, props.topN);
});

// ==================== Methods ====================

const getRankClass = (index: number): string => {
  if (index === 0) return 'rank-gold';
  if (index === 1) return 'rank-silver';
  if (index === 2) return 'rank-bronze';
  return 'rank-normal';
};

const getTypeName = (type: string): string => {
  const typeMap: Record<string, string> = {
    'opening': '开场白',
    'product_intro': '产品介绍',
    'price_promotion': '价格优惠',
    'limited_offer': '限时限量',
    'interaction': '互动问答',
    'demo': '使用演示',
    'testimonial': '买家秀',
    'closing': '促单成交',
    'qa': '答疑',
    'retention': '留人话术'
  };
  return typeMap[type] || type;
};

const getTypeClass = (type: string): string => {
  const classMap: Record<string, string> = {
    'opening': 'type-opening',
    'product_intro': 'type-product',
    'price_promotion': 'type-price',
    'limited_offer': 'type-limited',
    'interaction': 'type-interaction',
    'closing': 'type-closing'
  };
  return classMap[type] || '';
};

const getScoreClass = (score: number): string => {
  if (score >= 80) return 'score-excellent';
  if (score >= 60) return 'score-good';
  if (score >= 40) return 'score-average';
  return 'score-poor';
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const toggleExpand = (speechId: string) => {
  expandedId.value = expandedId.value === speechId ? null : speechId;
};

const copySpeech = (content: string) => {
  navigator.clipboard.writeText(content);
  emit('copy', content);
};

const viewDetail = (speech: SpeechData) => {
  emit('speech-click', speech);
};
</script>

<style scoped>
.speech-ranking-container {
  width: 100%;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

.filter-select {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.speech-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.speech-card:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24,144,255,0.15);
}

.speech-card.expanded {
  border-color: #1890ff;
  background: #f0f5ff;
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
  flex-shrink: 0;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  color: #fff;
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0, #999);
  color: #fff;
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32, #b87333);
  color: #fff;
}

.rank-normal {
  background: #f0f0f0;
  color: #666;
}

.speech-content {
  flex: 1;
  min-width: 0;
}

.speech-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.speech-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.type-opening {
  background: #e6f7ff;
  color: #1890ff;
}

.type-product {
  background: #f6ffed;
  color: #52c41a;
}

.type-price {
  background: #fff7e6;
  color: #fa8c16;
}

.type-limited {
  background: #fff1f0;
  color: #f5222d;
}

.type-interaction {
  background: #f9f0ff;
  color: #722ed1;
}

.type-closing {
  background: #ffe6f6;
  color: #eb2f96;
}

.confidence-tag {
  padding: 2px 6px;
  background: #52c41a;
  color: #fff;
  border-radius: 3px;
  font-size: 11px;
}

.speech-text {
  font-size: 14px;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.speech-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.time-range {
  font-family: monospace;
}

.score {
  font-weight: bold;
  font-size: 16px;
}

.score-excellent {
  color: #52c41a;
}

.score-good {
  color: #1890ff;
}

.score-average {
  color: #fa8c16;
}

.score-poor {
  color: #ff4d4f;
}

.score-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  margin-top: 8px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.score-fill.score-excellent {
  background: #52c41a;
}

.score-fill.score-good {
  background: #1890ff;
}

.score-fill.score-average {
  background: #fa8c16;
}

.score-fill.score-poor {
  background: #ff4d4f;
}

.metrics {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #d9d9d9;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.metric-label {
  width: 80px;
  font-size: 13px;
  color: #666;
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill.emotion {
  height: 100%;
  background: linear-gradient(90deg, #1890ff, #52c41a);
}

.metric-fill.engagement {
  height: 100%;
  background: linear-gradient(90deg, #722ed1, #eb2f96);
}

.metric-value {
  width: 40px;
  text-align: right;
  font-size: 13px;
  font-weight: bold;
  color: #333;
}

.issues-section,
.suggestions-section {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
}

.issues-section {
  background: #fff7e6;
  border-left: 3px solid #fa8c16;
}

.suggestions-section {
  background: #f6ffed;
  border-left: 3px solid #52c41a;
}

.issues-section h4,
.suggestions-section h4 {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: #333;
}

.issues-list,
.suggestions-list {
  margin: 0;
  padding-left: 16px;
}

.issues-list li,
.suggestions-list li {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover {
  background: #d9d9d9;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 8px;
}
</style>
