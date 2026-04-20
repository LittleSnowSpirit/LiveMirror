<template>
  <el-card class="product-score-card">
    <template #header>
      <div class="card-header">
        <span>📊 产品评分详情</span>
        <el-tag :type="getRecommendationType(scoreData.recommendation)" size="large">
          {{ scoreData.recommendation }}
        </el-tag>
      </div>
    </template>
    
    <div class="score-content">
      <!-- 产品基本信息 -->
      <div class="product-info">
        <h3>{{ scoreData.product_name }}</h3>
        <p>
          <el-tag size="small">{{ scoreData.category }}</el-tag>
          <span class="product-id">ID: {{ scoreData.product_id }}</span>
        </p>
        <p class="analysis-date">分析时间：{{ scoreData.analysis_date }}</p>
      </div>
      
      <!-- 综合评分展示 -->
      <div class="overall-score-section">
        <div class="score-gauge">
          <div class="gauge-circle" :style="{ borderColor: getScoreColor(scoreData.overall_score) }">
            <svg class="gauge-svg" viewBox="0 0 100 100">
              <circle class="gauge-bg" cx="50" cy="50" r="45" />
              <circle 
                class="gauge-progress" 
                cx="50" 
                cy="50" 
                r="45"
                :style="getCircleStyle(scoreData.overall_score)"
              />
            </svg>
            <div class="gauge-value">
              <span class="value-number">{{ scoreData.overall_score }}</span>
              <span class="value-label">综合评分</span>
            </div>
          </div>
        </div>
        
        <div class="score-interpretation">
          <h4>评分解读</h4>
          <div class="interpretation-item">
            <span class="level" :class="getScoreLevelClass(scoreData.overall_score)">
              {{ getScoreLevel(scoreData.overall_score) }}
            </span>
            <p>{{ getScoreInterpretation(scoreData.overall_score) }}</p>
          </div>
        </div>
      </div>
      
      <!-- 维度评分 -->
      <div class="dimension-scores">
        <h4>📈 维度评分详情</h4>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="dimension-item">
              <div class="dimension-header">
                <span class="dimension-name">🔥 市场热度</span>
                <span class="dimension-value" :style="{ color: getScoreColor(scoreData.market_score) }">
                  {{ scoreData.market_score }}
                </span>
              </div>
              <el-progress 
                :percentage="scoreData.market_score" 
                :color="getScoreColor(scoreData.market_score)"
                :stroke-width="10"
              />
              <p class="dimension-desc">基于销量、增长率、用户评分综合计算</p>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="dimension-item">
              <div class="dimension-header">
                <span class="dimension-name">⚔️ 竞争程度</span>
                <span class="dimension-value" :style="{ color: getScoreColor(scoreData.competition_score) }">
                  {{ scoreData.competition_score }}
                </span>
              </div>
              <el-progress 
                :percentage="scoreData.competition_score" 
                :color="getScoreColor(scoreData.competition_score)"
                :stroke-width="10"
              />
              <p class="dimension-desc">分数越高表示竞争越小，越有利</p>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="dimension-item">
              <div class="dimension-header">
                <span class="dimension-name">📊 趋势评分</span>
                <span class="dimension-value" :style="{ color: getScoreColor(scoreData.trend_score) }">
                  {{ scoreData.trend_score }}
                </span>
              </div>
              <el-progress 
                :percentage="scoreData.trend_score" 
                :color="getScoreColor(scoreData.trend_score)"
                :stroke-width="10"
              />
              <p class="dimension-desc">基于市场趋势和增长潜力评估</p>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="dimension-item">
              <div class="dimension-header">
                <span class="dimension-name">🚚 供应链风险</span>
                <span class="dimension-value" :style="{ color: getScoreColor(scoreData.supply_risk_score) }">
                  {{ scoreData.supply_risk_score }}
                </span>
              </div>
              <el-progress 
                :percentage="scoreData.supply_risk_score" 
                :color="getScoreColor(scoreData.supply_risk_score)"
                :stroke-width="10"
              />
              <p class="dimension-desc">分数越高表示风险越低，越稳定</p>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="dimension-item">
              <div class="dimension-header">
                <span class="dimension-name">💰 利润空间</span>
                <span class="dimension-value" :style="{ color: getScoreColor(scoreData.profit_score) }">
                  {{ scoreData.profit_score }}
                </span>
              </div>
              <el-progress 
                :percentage="scoreData.profit_score" 
                :color="getScoreColor(scoreData.profit_score)"
                :stroke-width="10"
              />
              <p class="dimension-desc">基于利润率和成本结构评估</p>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 评分权重说明 -->
      <div class="weight-explanation">
        <h4>⚖️ 评分权重</h4>
        <el-table :data="weightData" stripe style="width: 100%" size="small">
          <el-table-column prop="name" label="维度" width="150" />
          <el-table-column prop="weight" label="权重" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small">{{ row.weight }}%</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="当前得分" width="120" align="center">
            <template #default="{ row }">
              <span :style="{ color: getScoreColor(row.score) }" style="font-weight: bold">
                {{ row.score }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="contribution" label="贡献分数" align="center">
            <template #default="{ row }">
              {{ row.contribution }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 行动建议 -->
      <div class="action-suggestions">
        <h4>💡 行动建议</h4>
        <div class="suggestions-grid">
          <div 
            v-for="(suggestion, index) in actionSuggestions" 
            :key="index"
            class="suggestion-item"
            :class="getSuggestionType(suggestion.type)"
          >
            <div class="suggestion-icon">{{ suggestion.icon }}</div>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-desc">{{ suggestion.desc }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 下一步操作 -->
      <div class="next-actions">
        <h4>🚀 下一步操作</h4>
        <div class="action-buttons">
          <el-button type="primary" @click="$emit('view-report', scoreData.product_id)">
            📋 查看决策报告
          </el-button>
          <el-button type="success" @click="$emit('analyze-competitors', scoreData.product_id, scoreData.category)">
            🏆 竞品分析
          </el-button>
          <el-button type="warning" @click="$emit('assess-supply', scoreData.product_id)">
            ⚠️ 供应链评估
          </el-button>
          <el-button type="info" @click="$emit('analyze-profit', scoreData.product_id)">
            💰 利润分析
          </el-button>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'ProductScore',
  props: {
    scoreData: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  emits: ['view-report', 'analyze-competitors', 'assess-supply', 'analyze-profit'],
  data() {
    return {
      weightData: [
        { name: '市场热度', weight: 30, score: 0, contribution: 0 },
        { name: '竞争程度', weight: 20, score: 0, contribution: 0 },
        { name: '趋势评分', weight: 20, score: 0, contribution: 0 },
        { name: '供应链风险', weight: 15, score: 0, contribution: 0 },
        { name: '利润空间', weight: 15, score: 0, contribution: 0 }
      ]
    }
  },
  computed: {
    actionSuggestions() {
      const suggestions = []
      
      // 基于各维度评分生成建议
      if (this.scoreData.market_score >= 80) {
        suggestions.push({
          type: 'positive',
          icon: '🔥',
          title: '市场热度高',
          desc: '建议加大营销投入，快速占领市场'
        })
      } else if (this.scoreData.market_score < 50) {
        suggestions.push({
          type: 'warning',
          icon: '📉',
          title: '市场热度低',
          desc: '建议先进行市场调研，谨慎进入'
        })
      }
      
      if (this.scoreData.competition_score >= 70) {
        suggestions.push({
          type: 'positive',
          icon: '✅',
          title: '竞争环境良好',
          desc: '市场竞争较小，有利于新进入者'
        })
      } else if (this.scoreData.competition_score < 50) {
        suggestions.push({
          type: 'warning',
          icon: '⚠️',
          title: '竞争激烈',
          desc: '建议差异化定位，避免正面竞争'
        })
      }
      
      if (this.scoreData.trend_score >= 75) {
        suggestions.push({
          type: 'positive',
          icon: '📈',
          title: '趋势向好',
          desc: '产品处于上升期，建议把握时机'
        })
      }
      
      if (this.scoreData.supply_risk_score < 60) {
        suggestions.push({
          type: 'warning',
          icon: '🚚',
          title: '供应链风险',
          desc: '建议拓展供应商渠道，降低风险'
        })
      }
      
      if (this.scoreData.profit_score >= 70) {
        suggestions.push({
          type: 'positive',
          icon: '💰',
          title: '利润空间充足',
          desc: '盈利能力强，可考虑扩大规模'
        })
      } else if (this.scoreData.profit_score < 50) {
        suggestions.push({
          type: 'warning',
          icon: '💸',
          title: '利润空间有限',
          desc: '建议优化成本结构或提升定价'
        })
      }
      
      // 如果没有建议，添加默认建议
      if (suggestions.length === 0) {
        suggestions.push({
          type: 'info',
          icon: 'ℹ️',
          title: '综合评估',
          desc: '建议结合其他维度进行深入分析'
        })
      }
      
      return suggestions
    }
  },
  watch: {
    scoreData: {
      immediate: true,
      handler(newData) {
        if (newData && newData.overall_score !== undefined) {
          this.updateWeightData()
        }
      }
    }
  },
  methods: {
    // 更新权重数据
    updateWeightData() {
      this.weightData[0].score = this.scoreData.market_score
      this.weightData[0].contribution = (this.scoreData.market_score * 0.30).toFixed(1)
      
      this.weightData[1].score = this.scoreData.competition_score
      this.weightData[1].contribution = (this.scoreData.competition_score * 0.20).toFixed(1)
      
      this.weightData[2].score = this.scoreData.trend_score
      this.weightData[2].contribution = (this.scoreData.trend_score * 0.20).toFixed(1)
      
      this.weightData[3].score = this.scoreData.supply_risk_score
      this.weightData[3].contribution = (this.scoreData.supply_risk_score * 0.15).toFixed(1)
      
      this.weightData[4].score = this.scoreData.profit_score
      this.weightData[4].contribution = (this.scoreData.profit_score * 0.15).toFixed(1)
    },
    
    // 获取评分颜色
    getScoreColor(score) {
      if (score >= 80) return '#67C23A'
      if (score >= 65) return '#409EFF'
      if (score >= 50) return '#E6A23C'
      return '#F56C6C'
    },
    
    // 获取推荐类型
    getRecommendationType(rec) {
      const types = {
        '强烈推荐': 'success',
        '推荐': 'primary',
        '谨慎考虑': 'warning',
        '不推荐': 'danger'
      }
      return types[rec] || 'info'
    },
    
    // 获取圆形进度条样式
    getCircleStyle(score) {
      const circumference = 2 * Math.PI * 45
      const offset = circumference - (score / 100) * circumference
      return {
        strokeDasharray: `${circumference} ${circumference}`,
        strokeDashoffset: offset,
        stroke: this.getScoreColor(score)
      }
    },
    
    // 获取评分等级
    getScoreLevel(score) {
      if (score >= 90) return '卓越'
      if (score >= 80) return '优秀'
      if (score >= 70) return '良好'
      if (score >= 60) return '中等'
      if (score >= 50) return '及格'
      return '较差'
    },
    
    // 获取评分等级样式
    getScoreLevelClass(score) {
      if (score >= 90) return 'level-excellent'
      if (score >= 80) return 'level-great'
      if (score >= 70) return 'level-good'
      if (score >= 60) return 'level-average'
      if (score >= 50) return 'level-pass'
      return 'level-poor'
    },
    
    // 获取评分解读
    getScoreInterpretation(score) {
      if (score >= 90) return '产品表现卓越，各项指标均优秀，强烈建议推进'
      if (score >= 80) return '产品表现优秀，具有较好的市场前景和盈利潜力'
      if (score >= 70) return '产品表现良好，存在一定优势，建议进一步分析'
      if (score >= 60) return '产品表现中等，需要优化部分维度后再决策'
      if (score >= 50) return '产品表现及格，存在明显短板，谨慎考虑'
      return '产品表现较差，不建议作为选品方向'
    },
    
    // 获取建议类型
    getSuggestionType(type) {
      return `suggestion-${type}`
    }
  }
}
</script>

<style scoped>
.product-score-card {
  animation: slideIn 0.4s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-content {
  padding: 10px 0;
}

/* 产品基本信息 */
.product-info {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.product-info h3 {
  margin: 0 0 10px;
  color: #303133;
  font-size: 20px;
}

.product-info p {
  margin: 5px 0;
  color: #606266;
}

.product-id {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.analysis-date {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 综合评分展示 */
.overall-score-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.score-gauge {
  flex: 0 0 150px;
  display: flex;
  justify-content: center;
}

.gauge-circle {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 8px solid rgba(255, 255, 255, 0.3);
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gauge-svg {
  position: absolute;
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.gauge-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.3);
  stroke-width: 10;
}

.gauge-progress {
  fill: none;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
}

.gauge-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.value-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.value-label {
  font-size: 12px;
  color: #909399;
}

.score-interpretation {
  flex: 1;
  margin-left: 30px;
}

.score-interpretation h4 {
  margin: 0 0 15px;
  font-size: 16px;
  opacity: 0.9;
}

.interpretation-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 4px;
}

.level {
  display: inline-block;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  background: white;
  color: #303133;
}

.level-excellent { background: #67C23A; color: white; }
.level-great { background: #85ce61; color: white; }
.level-good { background: #409EFF; color: white; }
.level-average { background: #E6A23C; color: white; }
.level-pass { background: #F56C6C; color: white; }
.level-poor { background: #909399; color: white; }

.interpretation-item p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  opacity: 0.9;
}

/* 维度评分 */
.dimension-scores {
  margin-bottom: 30px;
}

.dimension-scores h4 {
  margin: 0 0 20px;
  color: #303133;
}

.dimension-item {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dimension-name {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.dimension-value {
  font-size: 18px;
  font-weight: bold;
}

.dimension-desc {
  margin: 8px 0 0;
  font-size: 12px;
  color: #909399;
}

/* 权重说明 */
.weight-explanation {
  margin-bottom: 30px;
}

.weight-explanation h4 {
  margin: 0 0 15px;
  color: #303133;
}

/* 行动建议 */
.action-suggestions {
  margin-bottom: 30px;
}

.action-suggestions h4 {
  margin: 0 0 15px;
  color: #303133;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid;
}

.suggestion-positive {
  background: #f0f9ff;
  border-left-color: #409EFF;
}

.suggestion-warning {
  background: #fdf6ec;
  border-left-color: #E6A23C;
}

.suggestion-info {
  background: #f4f4f5;
  border-left-color: #909399;
}

.suggestion-icon {
  font-size: 24px;
  margin-right: 12px;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.suggestion-desc {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

/* 下一步操作 */
.next-actions {
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.next-actions h4 {
  margin: 0 0 15px;
  color: #303133;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 150px;
}
</style>
