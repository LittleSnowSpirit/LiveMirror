<!--
优秀话术推荐组件
功能：
- 展示优秀话术案例
- 按话术类型分类
- 显示表现指标
- 一键复制参考
-->

<template>
  <div class="excellent-examples-container">
    <div class="header">
      <h3 class="title">📚 优秀话术参考</h3>
      <span class="subtitle" v-if="speechType">
        {{ getTypeName(speechType) }}
      </span>
    </div>
    
    <!-- 示例列表 -->
    <div class="examples-list">
      <div 
        v-for="(example, index) in examples" 
        :key="index"
        class="example-card"
        :class="{ 'expanded': expandedIndex === index }"
        @click="toggleExpand(index)"
      >
        <!-- 排名徽章 -->
        <div class="rank-badge" :class="getRankClass(index)">
          Top {{ index + 1 }}
        </div>
        
        <!-- 主要内容 -->
        <div class="example-content">
          <div class="example-header">
            <div class="score-badge" :class="getScoreClass(example.score)">
              {{ example.score }}分
            </div>
            <div class="example-metrics">
              <span class="metric" title="情绪影响">
                😊 {{ (example.emotion_impact * 100).toFixed(0) }}%
              </span>
              <span class="metric" title="互动率">
                💬 {{ example.engagement_rate.toFixed(0) }}/min
              </span>
            </div>
          </div>
          
          <p class="example-text">{{ example.content }}</p>
          
          <!-- 展开详情 -->
          <div class="example-detail" v-if="expandedIndex === index">
            <div class="detail-section">
              <h4>💡 亮点分析</h4>
              <ul class="highlights">
                <li v-if="example.emotion_impact > 0.8">
                  ✓ 情感表达强烈，感染力强
                </li>
                <li v-if="example.engagement_rate > 25">
                  ✓ 互动引导成功，观众参与度高
                </li>
                <li v-if="example.score > 90">
                  ✓ 综合表现优秀，值得学习
                </li>
              </ul>
            </div>
            
            <div class="detail-actions">
              <button class="btn btn-copy" @click.stop="copyContent(example.content)">
                📋 复制话术
              </button>
              <button class="btn btn-view" @click.stop="viewDetail(example)">
                👁️ 查看上下文
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!examples.length">
      <div class="empty-icon">📝</div>
      <p>暂无优秀案例</p>
    </div>
    
    <!-- 复制提示 -->
    <div class="copy-toast" v-if="showCopyToast">
      ✓ 已复制到剪贴板
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// ==================== Types ====================

interface ExcellentExample {
  speech_type: string;
  content: string;
  score: number;
  emotion_impact: number;
  engagement_rate: number;
  session_id?: string;
  timestamp?: number;
}

// ==================== Props ====================

const props = defineProps<{
  examples?: ExcellentExample[];
  speechType?: string;
}>();

const emit = defineEmits<{
  (e: 'view-detail', example: ExcellentExample): void;
}>();

// ==================== State ====================

const expandedIndex = ref<number | null>(null);
const showCopyToast = ref(false);

// ==================== Methods ====================

const getTypeName = (type: string): string => {
  const typeMap: Record<string, string> = {
    'opening': '开场白',
    'product_intro': '产品介绍',
    'price_promotion': '价格优惠',
    'limited_offer': '限时限量',
    'closing': '促单成交'
  };
  return typeMap[type] || type;
};

const getRankClass = (index: number): string => {
  if (index === 0) return 'rank-1';
  if (index === 1) return 'rank-2';
  if (index === 2) return 'rank-3';
  return 'rank-normal';
};

const getScoreClass = (score: number): string => {
  if (score >= 90) return 'score-excellent';
  if (score >= 80) return 'score-good';
  return 'score-average';
};

const toggleExpand = (index: number) => {
  expandedIndex.value = expandedIndex.value === index ? null : index;
};

const copyContent = (content: string) => {
  navigator.clipboard.writeText(content);
  showCopyToast.value = true;
  
  setTimeout(() => {
    showCopyToast.value = false;
  }, 2000);
};

const viewDetail = (example: ExcellentExample) => {
  emit('view-detail', example);
};
</script>

<style scoped>
.excellent-examples-container {
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

.subtitle {
  font-size: 14px;
  color: #666;
  padding: 4px 12px;
  background: #f0f0f0;
  border-radius: 4px;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.example-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.example-card:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24,144,255,0.15);
}

.example-card.expanded {
  border-color: #1890ff;
  background: #f0f5ff;
}

.rank-badge {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
  flex-shrink: 0;
  color: #fff;
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

.rank-normal {
  background: #f0f0f0;
  color: #666;
}

.example-content {
  flex: 1;
  min-width: 0;
}

.example-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.score-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 14px;
}

.score-excellent {
  background: #f6ffed;
  color: #389e0d;
}

.score-good {
  background: #e6f7ff;
  color: #1890ff;
}

.score-average {
  background: #f0f0f0;
  color: #666;
}

.example-metrics {
  display: flex;
  gap: 12px;
}

.metric {
  font-size: 13px;
  color: #666;
}

.example-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.example-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #d9d9d9;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section h4 {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: #333;
}

.highlights {
  margin: 0;
  padding-left: 16px;
}

.highlights li {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
  line-height: 1.5;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-copy {
  background: #1890ff;
  color: #fff;
}

.btn-copy:hover {
  background: #40a9ff;
}

.btn-view {
  background: #f0f0f0;
  color: #666;
}

.btn-view:hover {
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
