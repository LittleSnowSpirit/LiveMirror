<template>
  <div class="title-score">
    <!-- 总分展示 -->
    <div class="score-main">
      <div class="score-circle" :class="scoreClass">
        <svg viewBox="0 0 36 36" class="circular-chart">
          <path
            class="circle-bg"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            class="circle"
            :stroke-dasharray="`${score?.total || 0}, 100`"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <text x="18" y="20.35" class="score-number">
            {{ score?.total || 0 }}
          </text>
        </svg>
      </div>
      <div class="score-info">
        <div class="score-rating" :class="ratingClass">
          {{ score?.rating || 'N/A' }}
        </div>
        <div class="score-prediction">
          预测 CTR: <span class="ctr-value">{{ score?.predicted_ctr?.toFixed(2) || 0 }}%</span>
        </div>
      </div>
    </div>

    <!-- 评分因子详情 -->
    <div class="score-factors" v-if="score?.factors">
      <h4 class="factors-title">评分详情</h4>
      <div class="factor-item" v-for="(value, key) in score.factors" :key="key">
        <div class="factor-label">
          {{ getFactorLabel(key) }}
        </div>
        <div class="factor-bar">
          <div 
            class="factor-fill" 
            :class="getFactorClass(value)"
            :style="{ width: `${value}%` }"
          ></div>
        </div>
        <div class="factor-value">{{ value }}</div>
      </div>
    </div>

    <!-- 优化建议 -->
    <div class="score-suggestions" v-if="suggestions && suggestions.recommendations?.length">
      <h4 class="suggestions-title">💡 优化建议</h4>
      <div 
        class="suggestion-item" 
        v-for="(suggestion, index) in suggestions.recommendations" 
        :key="index"
        :class="suggestion.priority"
      >
        <span class="suggestion-icon">
          {{ suggestion.priority === 'high' ? '🔴' : suggestion.priority === 'medium' ? '🟡' : '🟢' }}
        </span>
        <span class="suggestion-text">{{ suggestion.message }}</span>
      </div>
    </div>

    <!-- 关键词建议 -->
    <div class="score-keywords" v-if="suggestions && suggestions.missing_keywords?.length">
      <h4 class="keywords-title">✨ 推荐关键词</h4>
      <div class="keyword-tags">
        <span 
          class="keyword-tag" 
          v-for="(keyword, index) in suggestions.missing_keywords.slice(0, 5)" 
          :key="index"
        >
          {{ keyword.keyword }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ScoreFactor {
  attractiveness: number
  clarity: number
  relevance: number
  urgency: number
  emotion: number
  keyword: number
}

interface Score {
  total: number
  predicted_ctr: number
  rating: string
  factors: ScoreFactor
  max_score: number
}

interface Suggestion {
  type: string
  message: string
  priority: 'high' | 'medium' | 'low'
}

interface KeywordSuggestion {
  keyword: string
  category: string
  weight: number
  reason: string
}

interface Suggestions {
  current_keywords: Array<{ keyword: string; category: string; weight: number }>
  missing_keywords: KeywordSuggestion[]
  recommendations: Suggestion[]
}

interface Props {
  score?: Score
  suggestions?: Suggestions
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true
})

// 评分等级样式
const scoreClass = computed(() => {
  const total = props.score?.total || 0
  if (total >= 90) return 'excellent'
  if (total >= 80) return 'good'
  if (total >= 70) return 'average'
  if (total >= 60) return 'poor'
  return 'bad'
})

// 评级样式
const ratingClass = computed(() => {
  const rating = props.score?.rating || ''
  return `rating-${rating.toLowerCase()}`
})

// 获取因子标签
const getFactorLabel = (key: string): string => {
  const labels: Record<string, string> = {
    attractiveness: '吸引力',
    clarity: '清晰度',
    relevance: '相关性',
    urgency: '紧迫感',
    emotion: '情感共鸣',
    keyword: '关键词优化'
  }
  return labels[key] || key
}

// 获取因子样式
const getFactorClass = (value: number): string => {
  if (value >= 80) return 'excellent'
  if (value >= 60) return 'good'
  if (value >= 40) return 'average'
  return 'poor'
}
</script>

<style scoped>
.title-score {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 主分数展示 */
.score-main {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.score-circle {
  width: 100px;
  height: 100px;
  position: relative;
}

.circular-chart {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 2.5;
}

.circle {
  fill: none;
  stroke-width: 2.5;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.score-circle.excellent .circle {
  stroke: #10b981;
}

.score-circle.good .circle {
  stroke: #3b82f6;
}

.score-circle.average .circle {
  stroke: #f59e0b;
}

.score-circle.poor .circle {
  stroke: #ef4444;
}

.score-circle.bad .circle {
  stroke: #6b7280;
}

.score-number {
  fill: #1f2937;
  font-size: 8px;
  font-weight: bold;
  text-anchor: middle;
  transform: rotate(90deg);
  transform-origin: center;
}

.score-info {
  flex: 1;
}

.score-rating {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.rating-s { color: #10b981; }
.rating-a { color: #3b82f6; }
.rating-b { color: #f59e0b; }
.rating-c { color: #ef4444; }
.rating-d { color: #6b7280; }

.score-prediction {
  font-size: 14px;
  color: #6b7280;
}

.ctr-value {
  font-weight: bold;
  color: #3b82f6;
  font-size: 16px;
}

/* 评分因子 */
.score-factors {
  margin-bottom: 24px;
}

.factors-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.factor-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.factor-label {
  width: 80px;
  font-size: 13px;
  color: #6b7280;
}

.factor-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.factor-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.factor-fill.excellent { background: #10b981; }
.factor-fill.good { background: #3b82f6; }
.factor-fill.average { background: #f59e0b; }
.factor-fill.poor { background: #ef4444; }

.factor-value {
  width: 40px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

/* 优化建议 */
.score-suggestions {
  margin-bottom: 24px;
}

.suggestions-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.suggestion-item.high {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}

.suggestion-item.medium {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
}

.suggestion-item.low {
  background: #f0fdf4;
  border-left: 3px solid #10b981;
}

.suggestion-icon {
  font-size: 16px;
}

.suggestion-text {
  color: #1f2937;
  line-height: 1.5;
}

/* 关键词建议 */
.score-keywords {
  margin-top: 20px;
}

.keywords-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  display: inline-block;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .title-score {
    background: #1f2937;
  }
  
  .score-number {
    fill: #f9fafb;
  }
  
  .factors-title,
  .suggestions-title,
  .keywords-title {
    color: #f9fafb;
  }
  
  .factor-label {
    color: #9ca3af;
  }
  
  .factor-value {
    color: #f9fafb;
  }
  
  .suggestion-text {
    color: #f9fafb;
  }
}
</style>
