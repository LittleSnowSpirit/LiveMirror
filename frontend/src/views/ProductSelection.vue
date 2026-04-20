<template>
  <div class="product-selection-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <h1 class="page-title">🛍️ 供应链选品推荐</h1>
      <p class="page-subtitle">智能分析商品热度、价格、利润，帮助主播选择高潜力商品</p>
    </header>

    <!-- 筛选和控制面板 -->
    <div class="control-panel">
      <div class="filter-group">
        <label class="filter-label">最低推荐分数:</label>
        <input 
          type="range" 
          v-model.number="minScore" 
          min="0" 
          max="100" 
          step="5"
          class="score-slider"
        />
        <span class="score-value">{{ minScore }}</span>
      </div>

      <div class="filter-group">
        <label class="filter-label">显示数量:</label>
        <select v-model.number="displayLimit" class="limit-select">
          <option :value="3">3 个</option>
          <option :value="5">5 个</option>
          <option :value="10">10 个</option>
          <option :value="20">20 个</option>
        </select>
      </div>

      <button @click="loadRecommendations" class="refresh-btn" :disabled="loading">
        {{ loading ? '加载中...' : '🔄 刷新推荐' }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在分析商品数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>❌ {{ error }}</p>
      <button @click="loadRecommendations" class="retry-btn">重试</button>
    </div>

    <!-- 商品列表 -->
    <div v-else class="product-list">
      <!-- 统计信息 -->
      <div class="stats-bar" v-if="products.length > 0">
        <span class="stat-item">
          📦 共 <strong>{{ products.length }}</strong> 个推荐商品
        </span>
        <span class="stat-item">
          ⭐ 平均分 <strong>{{ averageScore }}</strong>
        </span>
        <span class="stat-item">
          📈 高分商品 <strong>{{ highScoreCount }}</strong> 个
        </span>
      </div>

      <!-- 商品卡片 -->
      <ProductCard
        v-for="product in products"
        :key="product.product_id"
        :product="product"
        :is-recommended="product.recommendation_score >= 80"
        @expand-change="handleExpandChange"
      />

      <!-- 空状态 -->
      <div v-if="products.length === 0" class="empty-state">
        <p>😕 暂无符合条件的推荐商品</p>
        <p>尝试降低最低推荐分数或刷新数据</p>
      </div>
    </div>

    <!-- 批量操作面板 -->
    <div class="batch-actions" v-if="products.length > 0">
      <button @click="exportReport" class="action-btn export">
        📄 导出选品报告
      </button>
      <button @click="compareProducts" class="action-btn compare">
        ⚖️ 对比选品
      </button>
      <button @click="viewDetails" class="action-btn details">
        📊 查看详情
      </button>
    </div>
  </div>
</template>

<script>
import ProductCard from '../components/ProductCard.vue'

export default {
  name: 'ProductSelection',
  components: {
    ProductCard
  },
  data() {
    return {
      loading: false,
      error: null,
      products: [],
      minScore: 60,
      displayLimit: 5,
      expandedCount: 0
    }
  },
  computed: {
    averageScore() {
      if (this.products.length === 0) return 0
      const sum = this.products.reduce((acc, p) => acc + (p.recommendation_score || 0), 0)
      return (sum / this.products.length).toFixed(1)
    },
    highScoreCount() {
      return this.products.filter(p => p.recommendation_score >= 80).length
    }
  },
  mounted() {
    this.loadRecommendations()
  },
  methods: {
    async loadRecommendations() {
      this.loading = true
      this.error = null
      
      try {
        // 模拟 API 调用（实际使用时替换为真实 API）
        // const response = await fetch(`/api/product/recommendations?min_score=${this.minScore}&limit=${this.displayLimit}`)
        // const result = await response.json()
        // this.products = result.data
        
        // 模拟数据
        await this.simulateApiCall()
      } catch (err) {
        this.error = '加载推荐商品失败：' + err.message
      } finally {
        this.loading = false
      }
    },
    
    async simulateApiCall() {
      // 模拟 API 延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 模拟推荐商品数据
      this.products = [
        {
          product_id: 'P001',
          product_name: '智能保温杯',
          recommendation_score: 85.5,
          category: '家居用品',
          summary: '强烈推荐！智能保温杯在当前市场表现优异，利润空间充足，供应商可靠。',
          heat_analysis: {
            heat_score: 88.5,
            search_trend: {
              growth_rate: 15.3
            },
            social_media: {
              mentions: 3500
            },
            trend_status: 'rising'
          },
          price_comparison: {
            our_price: 89.0,
            market_avg_price: 95.0,
            price_advantage: 6.32
          },
          profit_analysis: {
            gross_margin_percent: 60.67,
            net_margin_percent: 45.2,
            roi_percent: 82.5,
            profitability_rating: 'high'
          },
          seasonality_analysis: {
            current_month_factor: 1.0,
            peak_season: '12 月',
            low_season: '7 月',
            recommendation: 'good_time'
          },
          supplier_evaluation: {
            supplier_name: '优质家居供应商',
            overall_rating: 4.5,
            on_time_delivery_rate: 95.5,
            defect_rate_percent: 0.8,
            risk_level: 'low'
          }
        },
        {
          product_id: 'P002',
          product_name: '无线蓝牙耳机',
          recommendation_score: 78.2,
          category: '数码配件',
          summary: '推荐考虑。无线蓝牙耳机具有不错的市场潜力，建议关注价格竞争力和季节因素。',
          heat_analysis: {
            heat_score: 82.0,
            search_trend: {
              growth_rate: 8.5
            },
            social_media: {
              mentions: 4200
            },
            trend_status: 'rising'
          },
          price_comparison: {
            our_price: 199.0,
            market_avg_price: 205.0,
            price_advantage: 2.93
          },
          profit_analysis: {
            gross_margin_percent: 59.8,
            net_margin_percent: 38.5,
            roi_percent: 62.8,
            profitability_rating: 'high'
          },
          seasonality_analysis: {
            current_month_factor: 1.0,
            peak_season: '11 月',
            low_season: '7 月',
            recommendation: 'good_time'
          },
          supplier_evaluation: {
            supplier_name: '数码精品厂',
            overall_rating: 4.2,
            on_time_delivery_rate: 92.0,
            defect_rate_percent: 1.2,
            risk_level: 'low'
          }
        },
        {
          product_id: 'P003',
          product_name: '便携式榨汁机',
          recommendation_score: 72.8,
          category: '小家电',
          summary: '推荐考虑。便携式榨汁机具有不错的市场潜力，建议关注价格竞争力和季节因素。',
          heat_analysis: {
            heat_score: 75.5,
            search_trend: {
              growth_rate: 5.2
            },
            social_media: {
              mentions: 2800
            },
            trend_status: 'stable'
          },
          price_comparison: {
            our_price: 159.0,
            market_avg_price: 165.0,
            price_advantage: 3.64
          },
          profit_analysis: {
            gross_margin_percent: 59.12,
            net_margin_percent: 35.8,
            roi_percent: 55.2,
            profitability_rating: 'medium'
          },
          seasonality_analysis: {
            current_month_factor: 0.9,
            peak_season: '12 月',
            low_season: '6 月',
            recommendation: 'wait_for_peak'
          },
          supplier_evaluation: {
            supplier_name: '家电制造商',
            overall_rating: 4.0,
            on_time_delivery_rate: 89.5,
            defect_rate_percent: 1.5,
            risk_level: 'medium'
          }
        },
        {
          product_id: 'P004',
          product_name: '瑜伽垫',
          recommendation_score: 68.5,
          category: '运动健身',
          summary: '谨慎选择。瑜伽垫当前市场表现一般，建议进一步优化或寻找替代品。',
          heat_analysis: {
            heat_score: 70.0,
            search_trend: {
              growth_rate: 3.8
            },
            social_media: {
              mentions: 2100
            },
            trend_status: 'stable'
          },
          price_comparison: {
            our_price: 79.0,
            market_avg_price: 75.0,
            price_advantage: -5.33
          },
          profit_analysis: {
            gross_margin_percent: 68.35,
            net_margin_percent: 42.5,
            roi_percent: 74.2,
            profitability_rating: 'high'
          },
          seasonality_analysis: {
            current_month_factor: 1.1,
            peak_season: '5 月',
            low_season: '1 月',
            recommendation: 'good_time'
          },
          supplier_evaluation: {
            supplier_name: '运动用品厂',
            overall_rating: 3.8,
            on_time_delivery_rate: 88.0,
            defect_rate_percent: 1.8,
            risk_level: 'medium'
          }
        },
        {
          product_id: 'P005',
          product_name: 'LED 化妆镜',
          recommendation_score: 81.3,
          category: '美妆工具',
          summary: '强烈推荐！LED 化妆镜在当前市场表现优异，利润空间充足，供应商可靠。',
          heat_analysis: {
            heat_score: 85.0,
            search_trend: {
              growth_rate: 12.5
            },
            social_media: {
              mentions: 3800
            },
            trend_status: 'rising'
          },
          price_comparison: {
            our_price: 129.0,
            market_avg_price: 138.0,
            price_advantage: 6.52
          },
          profit_analysis: {
            gross_margin_percent: 65.12,
            net_margin_percent: 48.5,
            roi_percent: 94.2,
            profitability_rating: 'high'
          },
          seasonality_analysis: {
            current_month_factor: 1.0,
            peak_season: '11 月',
            low_season: '3 月',
            recommendation: 'good_time'
          },
          supplier_evaluation: {
            supplier_name: '美妆供应商',
            overall_rating: 4.6,
            on_time_delivery_rate: 96.5,
            defect_rate_percent: 0.5,
            risk_level: 'low'
          }
        }
      ]
      
      // 根据筛选条件过滤
      this.products = this.products.filter(p => p.recommendation_score >= this.minScore)
      this.products = this.products.slice(0, this.displayLimit)
    },
    
    handleExpandChange(isExpanded) {
      if (isExpanded) {
        this.expandedCount++
      } else {
        this.expandedCount--
      }
    },
    
    exportReport() {
      // 导出选品报告逻辑
      const reportData = {
        exportTime: new Date().toISOString(),
        minScore: this.minScore,
        products: this.products
      }
      
      const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `选品报告_${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
      
      alert('✅ 选品报告已导出！')
    },
    
    compareProducts() {
      // 对比选品逻辑
      if (this.products.length < 2) {
        alert('至少需要 2 个商品才能进行对比')
        return
      }
      
      alert(`📊 将对比 ${this.products.length} 个商品\n\n功能开发中...`)
    },
    
    viewDetails() {
      // 查看详情逻辑
      alert('📊 详细分析页面\n\n功能开发中...')
    }
  },
  
  watch: {
    minScore() {
      // 防抖处理
      clearTimeout(this.scoreTimer)
      this.scoreTimer = setTimeout(() => {
        this.loadRecommendations()
      }, 500)
    },
    
    displayLimit() {
      this.loadRecommendations()
    }
  }
}
</script>

<style scoped>
.product-selection-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.control-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #555;
}

.score-slider {
  width: 150px;
  cursor: pointer;
}

.score-value {
  font-weight: 700;
  color: #667eea;
  min-width: 40px;
}

.limit-select {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.refresh-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p,
.error-state p,
.empty-state p {
  color: #666;
  margin: 8px 0;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.product-list {
  margin-bottom: 24px;
}

.stats-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.stat-item {
  font-size: 14px;
  color: #666;
}

.stat-item strong {
  color: #667eea;
  font-size: 18px;
}

.batch-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.export {
  background: #4CAF50;
  color: white;
}

.action-btn.compare {
  background: #2196F3;
  color: white;
}

.action-btn.details {
  background: #FF9800;
  color: white;
}
</style>
