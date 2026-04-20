<template>
  <div class="product-card" :class="{ 'recommended': isRecommended, 'expanded': isExpanded }">
    <!-- 卡片头部 -->
    <div class="card-header" @click="toggleExpand">
      <div class="product-info">
        <h3 class="product-name">{{ product.product_name || product.name }}</h3>
        <span class="product-category">{{ product.category || '未知分类' }}</span>
      </div>
      <div class="score-badge" :class="scoreClass">
        <span class="score-value">{{ recommendationScore }}</span>
        <span class="score-label">推荐分</span>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div v-if="isExpanded" class="card-content">
      <!-- 热度分析 -->
      <div class="analysis-section">
        <h4 class="section-title">🔥 热度分析</h4>
        <div class="analysis-grid">
          <div class="metric-item">
            <span class="metric-label">热度分数</span>
            <span class="metric-value">{{ heatData.heat_score || 0 }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">搜索趋势</span>
            <span class="metric-value" :class="trendClass">
              {{ heatData.search_trend?.growth_rate || 0 }}%
            </span>
          </div>
          <div class="metric-item">
            <span class="metric-label">社交讨论</span>
            <span class="metric-value">{{ heatData.social_media?.mentions || 0 }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">趋势状态</span>
            <span class="metric-value status-tag">{{ heatData.trend_status || 'stable' }}</span>
          </div>
        </div>
      </div>

      <!-- 价格对比 -->
      <div class="analysis-section">
        <h4 class="section-title">💰 价格对比</h4>
        <div class="price-comparison">
          <div class="price-item our-price">
            <span class="price-label">我们的价格</span>
            <span class="price-value">¥{{ priceData.our_price || 0 }}</span>
          </div>
          <div class="price-item market-price">
            <span class="price-label">市场均价</span>
            <span class="price-value">¥{{ priceData.market_avg_price || 0 }}</span>
          </div>
          <div class="price-advantage" v-if="priceData.price_advantage">
            <span class="advantage-text">
              {{ priceData.price_advantage > 0 ? '价格优势' : '价格劣势' }}: 
              {{ Math.abs(priceData.price_advantage) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- 利润分析 -->
      <div class="analysis-section">
        <h4 class="section-title">📊 利润分析</h4>
        <div class="analysis-grid">
          <div class="metric-item">
            <span class="metric-label">毛利率</span>
            <span class="metric-value highlight">{{ profitData.gross_margin_percent || 0 }}%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">净利率</span>
            <span class="metric-value">{{ profitData.net_margin_percent || 0 }}%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">ROI</span>
            <span class="metric-value">{{ profitData.roi_percent || 0 }}%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">盈利评级</span>
            <span class="metric-value rating-tag" :class="profitRatingClass">
              {{ profitData.profitability_rating || 'unknown' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 季节性分析 -->
      <div class="analysis-section">
        <h4 class="section-title">📅 季节性分析</h4>
        <div class="seasonality-info">
          <div class="season-item">
            <span class="season-label">当前月份系数</span>
            <span class="season-value">{{ seasonalityData.current_month_factor || 1.0 }}</span>
          </div>
          <div class="season-item">
            <span class="season-label">旺季</span>
            <span class="season-value peak">{{ seasonalityData.peak_season || '-' }}</span>
          </div>
          <div class="season-item">
            <span class="season-label">淡季</span>
            <span class="season-value low">{{ seasonalityData.low_season || '-' }}</span>
          </div>
          <div class="season-recommendation" :class="seasonalityData.recommendation">
            {{ seasonalityData.recommendation === 'good_time' ? '✅ 当前是销售好时机' : '⏳ 建议等待旺季' }}
          </div>
        </div>
      </div>

      <!-- 供应商评估 -->
      <div class="analysis-section">
        <h4 class="section-title">🏭 供应商评估</h4>
        <div class="supplier-info">
          <div class="supplier-name">{{ supplierData.supplier_name || '未知供应商' }}</div>
          <div class="supplier-rating">
            <span class="rating-stars">
              {{ '★'.repeat(Math.floor(supplierData.overall_rating || 0)) }}
              {{ '☆'.repeat(5 - Math.floor(supplierData.overall_rating || 0)) }}
            </span>
            <span class="rating-score">{{ supplierData.overall_rating || 0 }}</span>
          </div>
          <div class="supplier-metrics">
            <span class="metric-tag">准时交付：{{ supplierData.on_time_delivery_rate || 0 }}%</span>
            <span class="metric-tag">缺陷率：{{ supplierData.defect_rate_percent || 0 }}%</span>
            <span class="metric-tag">风险等级：{{ supplierData.risk_level || 'medium' }}</span>
          </div>
        </div>
      </div>

      <!-- 总结 -->
      <div class="summary-section">
        <h4 class="section-title">📝 总结建议</h4>
        <p class="summary-text">{{ product.summary || '暂无总结' }}</p>
      </div>
    </div>

    <!-- 展开/收起按钮 -->
    <div class="card-footer" @click="toggleExpand">
      <span class="expand-text">{{ isExpanded ? '收起详情' : '查看详情' }}</span>
      <span class="expand-icon">{{ isExpanded ? '▲' : '▼' }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductCard',
  props: {
    product: {
      type: Object,
      required: true
    },
    isRecommended: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isExpanded: false
    }
  },
  computed: {
    recommendationScore() {
      return this.product.recommendation_score || 0
    },
    scoreClass() {
      if (this.recommendationScore >= 80) return 'score-high'
      if (this.recommendationScore >= 60) return 'score-medium'
      return 'score-low'
    },
    heatData() {
      return this.product.heat_analysis || {}
    },
    priceData() {
      return this.product.price_comparison || {}
    },
    profitData() {
      return this.product.profit_analysis || {}
    },
    seasonalityData() {
      return this.product.seasonality_analysis || {}
    },
    supplierData() {
      return this.product.supplier_evaluation || {}
    },
    trendClass() {
      const growth = this.heatData.search_trend?.growth_rate || 0
      return growth > 10 ? 'trend-up' : growth < 0 ? 'trend-down' : 'trend-stable'
    },
    profitRatingClass() {
      const rating = this.profitData.profitability_rating || 'medium'
      return `rating-${rating}`
    }
  },
  methods: {
    toggleExpand() {
      this.isExpanded = !this.isExpanded
      this.$emit('expand-change', this.isExpanded)
    }
  }
}
</script>

<style scoped>
.product-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.product-card.recommended {
  border-color: #4CAF50;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.product-card.expanded {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.product-info {
  flex: 1;
}

.product-name {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}

.product-category {
  font-size: 12px;
  opacity: 0.9;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
}

.score-badge {
  text-align: center;
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.2);
}

.score-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
}

.score-label {
  font-size: 12px;
  opacity: 0.9;
}

.score-high {
  background: #4CAF50;
}

.score-medium {
  background: #FF9800;
}

.score-low {
  background: #F44336;
}

.card-content {
  padding: 16px;
}

.analysis-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.analysis-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.metric-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.metric-value.highlight {
  color: #4CAF50;
}

.trend-up {
  color: #4CAF50;
}

.trend-down {
  color: #F44336;
}

.trend-stable {
  color: #FF9800;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  background: #e3f2fd;
  color: #1976d2;
}

.rating-tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  text-transform: capitalize;
}

.rating-high {
  background: #e8f5e9;
  color: #2e7d32;
}

.rating-medium {
  background: #fff3e0;
  color: #ef6c00;
}

.rating-low {
  background: #ffebee;
  color: #c62828;
}

.price-comparison {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.price-item:last-child {
  margin-bottom: 0;
}

.price-label {
  color: #666;
}

.price-value {
  font-weight: 600;
  color: #333;
}

.our-price .price-value {
  color: #4CAF50;
  font-size: 18px;
}

.price-advantage {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ddd;
  text-align: center;
}

.advantage-text {
  font-size: 14px;
  color: #4CAF50;
}

.seasonality-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.season-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.season-label {
  color: #666;
}

.season-value {
  font-weight: 600;
}

.season-value.peak {
  color: #FF9800;
}

.season-value.low {
  color: #2196F3;
}

.season-recommendation {
  margin-top: 12px;
  padding: 8px;
  border-radius: 6px;
  text-align: center;
  font-weight: 600;
}

.season-recommendation.good_time {
  background: #e8f5e9;
  color: #2e7d32;
}

.season-recommendation.wait_for_peak {
  background: #fff3e0;
  color: #ef6c00;
}

.supplier-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.supplier-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.supplier-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.rating-stars {
  color: #FF9800;
  font-size: 18px;
}

.rating-score {
  font-weight: 600;
  color: #333;
}

.supplier-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.metric-tag {
  background: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  color: #666;
  border: 1px solid #ddd;
}

.summary-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
  border-radius: 8px;
  color: white;
}

.summary-section .section-title {
  color: white;
}

.summary-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.95;
}

.card-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  cursor: pointer;
  transition: background 0.2s;
}

.card-footer:hover {
  background: #e9ecef;
}

.expand-text {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
}

.expand-icon {
  margin-left: 8px;
  font-size: 12px;
}
</style>
