<template>
  <div class="product-ai-page">
    <div class="page-header">
      <h1>🎯 智能选品系统 2.0</h1>
      <p class="subtitle">AI 驱动的产品选择与决策分析 - 多维度评分、竞品分析、趋势预测</p>
    </div>

    <!-- 功能导航 -->
    <div class="function-nav">
      <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick">
        <el-tab-pane label="📊 产品评分" name="score"></el-tab-pane>
        <el-tab-pane label="🏆 TOP 榜单" name="top"></el-tab-pane>
        <el-tab-pane label="📈 趋势预测" name="trend"></el-tab-pane>
        <el-tab-pane label="⚠️ 供应链风险" name="supply"></el-tab-pane>
        <el-tab-pane label="💰 利润分析" name="profit"></el-tab-pane>
        <el-tab-pane label="📋 决策报告" name="report"></el-tab-pane>
      </el-tabs>
    </div>

    <!-- 产品评分面板 -->
    <div v-if="activeTab === 'score'" class="tab-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>🔍 选择产品</span>
              </div>
            </template>
            
            <el-form label-width="100px">
              <el-form-item label="产品类别">
                <el-select v-model="scoreForm.category" @change="loadProductsByCategory" style="width: 100%">
                  <el-option label="全部类别" value=""></el-option>
                  <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="选择产品">
                <el-select v-model="scoreForm.productId" placeholder="请选择产品" style="width: 100%">
                  <el-option
                    v-for="product in filteredProducts"
                    :key="product.product_id"
                    :label="product.product_name"
                    :value="product.product_id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="runProductScore" :loading="scoreLoading" style="width: 100%">
                  开始评分
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <product-score v-if="scoreResult" :score-data="scoreResult" />
          <el-empty v-else description="请选择产品进行评分" />
        </el-col>
      </el-row>
    </div>

    <!-- TOP 榜单面板 -->
    <div v-if="activeTab === 'top'" class="tab-content">
      <el-card class="top-card">
        <template #header>
          <div class="card-header">
            <span>🏆 推荐产品 TOP 榜</span>
            <el-select v-model="topForm.category" @change="loadTopProducts" style="width: 200px">
              <el-option label="全部类别" value=""></el-option>
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
          </div>
        </template>
        
        <el-table :data="topProducts" stripe style="width: 100%" :default-sort="{prop: 'overall_score', order: 'descending'}">
          <el-table-column prop="rank" label="排名" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getRankType(row.rank)">
                <span v-if="row.rank <= 3">🏆</span>
                {{ row.rank }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="product_name" label="产品名称" min-width="200" />
          <el-table-column prop="category" label="类别" width="100" align="center" />
          <el-table-column prop="overall_score" label="综合评分" width="120" sortable align="center">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.overall_score)">
                {{ row.overall_score }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="market_score" label="市场热度" width="100" sortable align="center" />
          <el-table-column prop="profit_score" label="利润空间" width="100" sortable align="center" />
          <el-table-column prop="trend_score" label="趋势评分" width="100" sortable align="center" />
          <el-table-column prop="recommendation" label="推荐等级" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getRecommendationType(row.recommendation)">
                {{ row.recommendation }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewDecisionReport(row.product_id)">
                查看报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 趋势预测面板 -->
    <div v-if="activeTab === 'trend'" class="tab-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>📈 趋势预测参数</span>
              </div>
            </template>
            
            <el-form label-width="100px">
              <el-form-item label="产品类别">
                <el-select v-model="trendForm.category" style="width: 100%">
                  <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="预测月数">
                <el-input-number v-model="trendForm.monthsAhead" :min="1" :max="12" style="width: 100%" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="runTrendPrediction" :loading="trendLoading" style="width: 100%">
                  开始预测
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card v-if="trendResult" class="result-card">
            <template #header>
              <div class="card-header">
                <span>📊 {{ trendResult.category }} 趋势预测</span>
                <el-tag :type="getTrendOutlookType(trendResult.trend_outlook)">
                  {{ trendResult.trend_outlook }}
                </el-tag>
              </div>
            </template>
            
            <div class="trend-summary">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="当前趋势分">
                  {{ trendResult.current_trend_score }}
                </el-descriptions-item>
                <el-descriptions-item label="30 天变化">
                  <span :class="getChangeClass(trendResult['30d_change'])">
                    {{ trendResult['30d_change'] > 0 ? '+' : '' }}{{ trendResult['30d_change'] }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="90 天变化">
                  <span :class="getChangeClass(trendResult['90d_change'])">
                    {{ trendResult['90d_change'] > 0 ? '+' : '' }}{{ trendResult['90d_change'] }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="平均预测分">
                  {{ trendResult.avg_predicted_score }}
                </el-descriptions-item>
                <el-descriptions-item label="季节性峰值">
                  {{ trendResult.seasonal_peak_month }}月
                </el-descriptions-item>
              </el-descriptions>
            </div>
            
            <div class="trend-predictions">
              <h4>未来{{ trendForm.monthsAhead }}个月预测</h4>
              <el-table :data="trendResult.predictions" stripe style="width: 100%">
                <el-table-column prop="month_name" label="月份" width="120" />
                <el-table-column prop="seasonal_factor" label="季节因子" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.seasonal_factor > 1 ? 'success' : 'warning'">
                      {{ row.seasonal_factor }}x
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="predicted_score" label="预测得分" width="120" align="center" />
                <el-table-column prop="trend_direction" label="趋势方向" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.trend_direction === '上升' ? 'success' : 'danger'">
                      {{ row.trend_direction }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div class="hot-keywords">
              <h4>🔥 热门关键词</h4>
              <div class="keywords-container">
                <el-tag
                  v-for="kw in trendResult.hot_keywords"
                  :key="kw.keyword"
                  :type="kw.growth_rate > 0.3 ? 'success' : 'primary'"
                  style="margin: 5px"
                >
                  {{ kw.keyword }} (搜索量：{{ formatNumber(kw.search_volume) }})
                </el-tag>
              </div>
            </div>
          </el-card>
          <el-empty v-else description="请选择类别进行趋势预测" />
        </el-col>
      </el-row>
    </div>

    <!-- 供应链风险面板 -->
    <div v-if="activeTab === 'supply'" class="tab-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>⚠️ 选择产品</span>
              </div>
            </template>
            
            <el-form label-width="100px">
              <el-form-item label="产品类别">
                <el-select v-model="supplyForm.category" @change="loadProductsByCategory" style="width: 100%">
                  <el-option label="全部类别" value=""></el-option>
                  <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="选择产品">
                <el-select v-model="supplyForm.productId" placeholder="请选择产品" style="width: 100%">
                  <el-option
                    v-for="product in filteredProducts"
                    :key="product.product_id"
                    :label="product.product_name"
                    :value="product.product_id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="runSupplyRiskAssessment" :loading="supplyLoading" style="width: 100%">
                  评估风险
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card v-if="supplyResult" class="result-card">
            <template #header>
              <div class="card-header">
                <span>⚠️ 供应链风险评估</span>
                <el-tag :type="getRiskLevelType(supplyResult.risk_level)">
                  {{ supplyResult.risk_level }}
                </el-tag>
              </div>
            </template>
            
            <div class="risk-overview">
              <el-progress
                :percentage="supplyResult.risk_level_score"
                :color="getRiskColor(supplyResult.risk_level_score)"
                :format="() => supplyResult.risk_level_score + '分'"
              />
              <div class="risk-breakdown">
                <h4>风险构成</h4>
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="risk-item">
                      <div class="risk-label">稳定性风险</div>
                      <div class="risk-value">{{ supplyResult.risk_breakdown.stability_risk }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="risk-item">
                      <div class="risk-label">供应商风险</div>
                      <div class="risk-value">{{ supplyResult.risk_breakdown.supplier_risk }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="risk-item">
                      <div class="risk-label">库存风险</div>
                      <div class="risk-value">{{ supplyResult.risk_breakdown.inventory_risk }}</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="risk-item">
                      <div class="risk-label">退货风险</div>
                      <div class="risk-value">{{ supplyResult.risk_breakdown.return_risk }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
            
            <div class="risk-details">
              <h4>风险因素</h4>
              <el-alert
                v-for="(factor, index) in supplyResult.risk_factors"
                :key="index"
                :title="factor.factor"
                :type="factor.status === '警告' ? 'warning' : 'info'"
                :description="`当前值：${factor.value} | 建议：${factor.suggestion}`"
                show-icon
                style="margin-bottom: 10px"
              />
              <el-alert v-if="supplyResult.risk_factors.length === 0" type="success" description="供应链状况良好，无明显风险因素" show-icon />
            </div>
            
            <div class="risk-recommendations">
              <h4>💡 优化建议</h4>
              <ul>
                <li v-for="(rec, index) in supplyResult.recommendations" :key="index">{{ rec }}</li>
              </ul>
            </div>
          </el-card>
          <el-empty v-else description="请选择产品进行风险评估" />
        </el-col>
      </el-row>
    </div>

    <!-- 利润分析面板 -->
    <div v-if="activeTab === 'profit'" class="tab-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>💰 选择产品</span>
              </div>
            </template>
            
            <el-form label-width="100px">
              <el-form-item label="产品类别">
                <el-select v-model="profitForm.category" @change="loadProductsByCategory" style="width: 100%">
                  <el-option label="全部类别" value=""></el-option>
                  <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="选择产品">
                <el-select v-model="profitForm.productId" placeholder="请选择产品" style="width: 100%">
                  <el-option
                    v-for="product in filteredProducts"
                    :key="product.product_id"
                    :label="product.product_name"
                    :value="product.product_id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="runProfitAnalysis" :loading="profitLoading" style="width: 100%">
                  分析利润
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card v-if="profitResult" class="result-card">
            <template #header>
              <div class="card-header">
                <span>💰 利润空间分析</span>
                <el-tag :type="getProfitType(profitResult.profit_rating)">
                  {{ profitResult.profit_rating }}
                </el-tag>
              </div>
            </template>
            
            <div class="profit-summary">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="profit-stat">
                    <div class="stat-label">销售价格</div>
                    <div class="stat-value">¥{{ profitResult.base_price }}</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="profit-stat">
                    <div class="stat-label">产品成本</div>
                    <div class="stat-value">¥{{ profitResult.cost_price }}</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="profit-stat">
                    <div class="stat-label">毛利润</div>
                    <div class="stat-value">¥{{ profitResult.gross_profit }}</div>
                    <div class="stat-sub">毛利率：{{ profitResult.gross_margin_percent }}%</div>
                  </div>
                </el-col>
              </el-row>
              
              <el-row :gutter="20" style="margin-top: 20px">
                <el-col :span="12">
                  <div class="profit-stat">
                    <div class="stat-label">净利润</div>
                    <div class="stat-value">¥{{ profitResult.net_profit }}</div>
                    <div class="stat-sub">净利率：{{ profitResult.net_margin_percent }}%</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="profit-stat">
                    <div class="stat-label">月利润潜力</div>
                    <div class="stat-value">¥{{ formatNumber(profitResult.monthly_profit_potential) }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="cost-structure">
              <h4>📊 成本结构</h4>
              <el-table :data="getCostStructureTableData()" stripe style="width: 100%">
                <el-table-column prop="name" label="项目" width="150" />
                <el-table-column prop="amount" label="金额" width="120" align="right">
                  <template #default="{ row }">¥{{ row.amount }}</template>
                </el-table-column>
                <el-table-column prop="percent" label="占比" align="center">
                  <template #default="{ row }">
                    <el-progress :percentage="row.percent" :stroke-width="15" :show-text="false" />
                    <span style="margin-left: 10px">{{ row.percent }}%</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div class="optimization-suggestions">
              <h4>💡 优化建议</h4>
              <ul>
                <li v-for="(suggestion, index) in profitResult.optimization_suggestions" :key="index">{{ suggestion }}</li>
              </ul>
            </div>
          </el-card>
          <el-empty v-else description="请选择产品进行利润分析" />
        </el-col>
      </el-row>
    </div>

    <!-- 决策报告面板 -->
    <div v-if="activeTab === 'report'" class="tab-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>📋 选择产品</span>
              </div>
            </template>
            
            <el-form label-width="100px">
              <el-form-item label="产品类别">
                <el-select v-model="reportForm.category" @change="loadProductsByCategory" style="width: 100%">
                  <el-option label="全部类别" value=""></el-option>
                  <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="选择产品">
                <el-select v-model="reportForm.productId" placeholder="请选择产品" style="width: 100%">
                  <el-option
                    v-for="product in filteredProducts"
                    :key="product.product_id"
                    :label="product.product_name"
                    :value="product.product_id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="generateDecisionReport" :loading="reportLoading" style="width: 100%">
                  生成报告
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <el-card v-if="reportResult" class="result-card report-card">
            <template #header>
              <div class="card-header">
                <span>📋 选品决策报告</span>
                <div class="report-tags">
                  <el-tag :type="getDecisionType(reportResult.final_decision)" size="large">
                    {{ reportResult.final_decision }}
                  </el-tag>
                  <el-tag type="info" size="large" style="margin-left: 10px">
                    置信度：{{ reportResult.confidence_level }}
                  </el-tag>
                </div>
              </div>
            </template>
            
            <div class="report-header">
              <div class="product-info">
                <h3>{{ reportResult.product_name }}</h3>
                <p>类别：{{ reportResult.category }} | 产品 ID: {{ reportResult.product_id }}</p>
                <p>报告时间：{{ reportResult.report_date }}</p>
              </div>
              <div class="overall-score">
                <div class="score-circle" :style="{ borderColor: getScoreColor(reportResult.overall_score) }">
                  <span class="score-value">{{ reportResult.overall_score }}</span>
                  <span class="score-label">综合评分</span>
                </div>
              </div>
            </div>
            
            <div class="score-breakdown">
              <h4>📊 评分明细</h4>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="score-item">
                    <div class="score-name">市场热度</div>
                    <el-progress :percentage="reportResult.score_breakdown.market_score" :color="getScoreColor(reportResult.score_breakdown.market_score)" />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="score-item">
                    <div class="score-name">竞争程度</div>
                    <el-progress :percentage="reportResult.score_breakdown.competition_score" :color="getScoreColor(reportResult.score_breakdown.competition_score)" />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="score-item">
                    <div class="score-name">趋势评分</div>
                    <el-progress :percentage="reportResult.score_breakdown.trend_score" :color="getScoreColor(reportResult.score_breakdown.trend_score)" />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="score-item">
                    <div class="score-name">供应链风险</div>
                    <el-progress :percentage="reportResult.score_breakdown.supply_risk_score" :color="getScoreColor(reportResult.score_breakdown.supply_risk_score)" />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="score-item">
                    <div class="score-name">利润空间</div>
                    <el-progress :percentage="reportResult.score_breakdown.profit_score" :color="getScoreColor(reportResult.score_breakdown.profit_score)" />
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="decision-factors">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="factor-section positive">
                    <h4>✅ 正面因素</h4>
                    <ul>
                      <li v-for="(factor, index) in reportResult.decision_factors.positive" :key="index">{{ factor }}</li>
                    </ul>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="factor-section negative">
                    <h4>⚠️ 负面因素</h4>
                    <ul>
                      <li v-for="(factor, index) in reportResult.decision_factors.negative" :key="index">{{ factor }}</li>
                    </ul>
                    <p v-if="reportResult.decision_factors.negative.length === 0" class="empty-factor">无明显负面因素</p>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="key-insights">
              <h4>💡 关键洞察</h4>
              <div class="insights-container">
                <el-alert
                  v-for="(insight, index) in reportResult.key_insights"
                  :key="index"
                  :title="insight"
                  type="info"
                  show-icon
                  style="margin-bottom: 10px"
                  :closable="false"
                />
              </div>
            </div>
            
            <div class="report-footer">
              <el-button type="primary" @click="exportReport">📥 导出报告</el-button>
              <el-button @click="printReport">🖨️ 打印报告</el-button>
            </div>
          </el-card>
          <el-empty v-else description="请选择产品生成决策报告" />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import ProductScore from '../components/ProductScore.vue'

export default {
  name: 'ProductAI',
  components: {
    ProductScore
  },
  data() {
    return {
      activeTab: 'score',
      categories: [],
      allProducts: [],
      filteredProducts: [],
      
      // 产品评分
      scoreLoading: false,
      scoreForm: {
        category: '',
        productId: ''
      },
      scoreResult: null,
      
      // TOP 榜单
      topForm: {
        category: ''
      },
      topProducts: [],
      
      // 趋势预测
      trendLoading: false,
      trendForm: {
        category: '',
        monthsAhead: 3
      },
      trendResult: null,
      
      // 供应链风险
      supplyLoading: false,
      supplyForm: {
        category: '',
        productId: ''
      },
      supplyResult: null,
      
      // 利润分析
      profitLoading: false,
      profitForm: {
        category: '',
        productId: ''
      },
      profitResult: null,
      
      // 决策报告
      reportLoading: false,
      reportForm: {
        category: '',
        productId: ''
      },
      reportResult: null
    }
  },
  mounted() {
    this.loadCategories()
    this.loadAllProducts()
  },
  methods: {
    // 加载类别
    async loadCategories() {
      try {
        const response = await fetch('/api/product-ai/categories', {
          method: 'GET'
        })
        const data = await response.json()
        if (data.success) {
          this.categories = data.data.categories
        }
      } catch (error) {
        console.error('加载类别失败:', error)
      }
    },
    
    // 加载所有产品
    async loadAllProducts() {
      try {
        const response = await fetch('/api/product-ai/top/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ limit: 200 })
        })
        const data = await response.json()
        if (data.success) {
          this.allProducts = data.data.products.map(p => p.product)
          this.filteredProducts = this.allProducts
        }
      } catch (error) {
        console.error('加载产品失败:', error)
      }
    },
    
    // 按类别加载产品
    loadProductsByCategory() {
      const category = this.scoreForm.category || this.supplyForm.category || this.profitForm.category || this.reportForm.category
      if (category) {
        this.filteredProducts = this.allProducts.filter(p => p.category === category)
      } else {
        this.filteredProducts = this.allProducts
      }
      // 重置产品选择
      this.scoreForm.productId = ''
      this.supplyForm.productId = ''
      this.profitForm.productId = ''
      this.reportForm.productId = ''
    },
    
    // 处理标签页切换
    handleTabClick(tab) {
      // 如果切换到 TOP 榜单，自动加载数据
      if (tab.name === 'top') {
        this.loadTopProducts()
      }
    },
    
    // 运行产品评分
    async runProductScore() {
      if (!this.scoreForm.productId) {
        ElMessage.warning('请选择产品')
        return
      }
      
      this.scoreLoading = true
      try {
        const response = await fetch('/api/product-ai/score/product', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: this.scoreForm.productId })
        })
        const data = await response.json()
        if (data.success) {
          this.scoreResult = data.data
          ElMessage.success(data.message)
        } else {
          ElMessage.error(data.detail || '评分失败')
        }
      } catch (error) {
        console.error('评分失败:', error)
        ElMessage.error('评分失败，请重试')
      } finally {
        this.scoreLoading = false
      }
    },
    
    // 加载 TOP 产品
    async loadTopProducts() {
      try {
        const response = await fetch('/api/product-ai/top/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            category: this.topForm.category || undefined,
            limit: 20 
          })
        })
        const data = await response.json()
        if (data.success) {
          this.topProducts = data.data.products.map((p, index) => ({
            rank: index + 1,
            ...p.score
          }))
        }
      } catch (error) {
        console.error('加载 TOP 产品失败:', error)
      }
    },
    
    // 运行趋势预测
    async runTrendPrediction() {
      if (!this.trendForm.category) {
        ElMessage.warning('请选择类别')
        return
      }
      
      this.trendLoading = true
      try {
        const response = await fetch('/api/product-ai/predict/trend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            category: this.trendForm.category,
            months_ahead: this.trendForm.monthsAhead
          })
        })
        const data = await response.json()
        if (data.success) {
          this.trendResult = data.data
          ElMessage.success(data.message)
        } else {
          ElMessage.error(data.detail || '预测失败')
        }
      } catch (error) {
        console.error('预测失败:', error)
        ElMessage.error('预测失败，请重试')
      } finally {
        this.trendLoading = false
      }
    },
    
    // 运行供应链风险评估
    async runSupplyRiskAssessment() {
      if (!this.supplyForm.productId) {
        ElMessage.warning('请选择产品')
        return
      }
      
      this.supplyLoading = true
      try {
        const response = await fetch('/api/product-ai/assess/supply-risk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: this.supplyForm.productId })
        })
        const data = await response.json()
        if (data.success) {
          this.supplyResult = data.data
          ElMessage.success(data.message)
        } else {
          ElMessage.error(data.detail || '评估失败')
        }
      } catch (error) {
        console.error('评估失败:', error)
        ElMessage.error('评估失败，请重试')
      } finally {
        this.supplyLoading = false
      }
    },
    
    // 运行利润分析
    async runProfitAnalysis() {
      if (!this.profitForm.productId) {
        ElMessage.warning('请选择产品')
        return
      }
      
      this.profitLoading = true
      try {
        const response = await fetch('/api/product-ai/analyze/profit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: this.profitForm.productId })
        })
        const data = await response.json()
        if (data.success) {
          this.profitResult = data.data
          ElMessage.success(data.message)
        } else {
          ElMessage.error(data.detail || '分析失败')
        }
      } catch (error) {
        console.error('分析失败:', error)
        ElMessage.error('分析失败，请重试')
      } finally {
        this.profitLoading = false
      }
    },
    
    // 生成决策报告
    async generateDecisionReport() {
      if (!this.reportForm.productId) {
        ElMessage.warning('请选择产品')
        return
      }
      
      this.reportLoading = true
      try {
        const response = await fetch('/api/product-ai/report/decision', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: this.reportForm.productId })
        })
        const data = await response.json()
        if (data.success) {
          this.reportResult = data.data
          ElMessage.success(data.message)
          // 自动切换到报告标签页
          this.activeTab = 'report'
        } else {
          ElMessage.error(data.detail || '生成报告失败')
        }
      } catch (error) {
        console.error('生成报告失败:', error)
        ElMessage.error('生成报告失败，请重试')
      } finally {
        this.reportLoading = false
      }
    },
    
    // 查看决策报告
    async viewDecisionReport(productId) {
      this.reportForm.productId = productId
      await this.generateDecisionReport()
    },
    
    // 获取成本结构表格数据
    getCostStructureTableData() {
      if (!this.profitResult || !this.profitResult.cost_structure) return []
      
      const cs = this.profitResult.cost_structure
      return [
        { name: '产品成本', amount: cs.product_cost.amount, percent: cs.product_cost.percent },
        { name: '平台佣金', amount: cs.platform_fee.amount, percent: cs.platform_fee.percent },
        { name: '物流成本', amount: cs.logistics.amount, percent: cs.logistics.percent },
        { name: '营销成本', amount: cs.marketing.amount, percent: cs.marketing.percent },
        { name: '毛利润', amount: cs.gross_profit.amount, percent: cs.gross_profit.percent },
        { name: '净利润', amount: cs.net_profit.amount, percent: cs.net_profit.percent }
      ]
    },
    
    // 格式化数字
    formatNumber(num) {
      return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },
    
    // 获取排名类型
    getRankType(rank) {
      if (rank === 1) return 'warning'
      if (rank === 2) return 'success'
      if (rank === 3) return 'primary'
      return 'info'
    },
    
    // 获取评分类型
    getScoreType(score) {
      if (score >= 80) return 'success'
      if (score >= 65) return 'primary'
      if (score >= 50) return 'warning'
      return 'danger'
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
    
    // 获取趋势展望类型
    getTrendOutlookType(outlook) {
      const types = {
        '乐观': 'success',
        '平稳': 'primary',
        '谨慎': 'warning'
      }
      return types[outlook] || 'info'
    },
    
    // 获取变化样式
    getChangeClass(change) {
      if (change > 0) return 'change-positive'
      if (change < 0) return 'change-negative'
      return ''
    },
    
    // 获取风险等级类型
    getRiskLevelType(level) {
      const types = {
        '低风险': 'success',
        '中风险': 'warning',
        '高风险': 'orange',
        '极高风险': 'danger'
      }
      return types[level] || 'info'
    },
    
    // 获取风险颜色
    getRiskColor(score) {
      if (score >= 80) return '#67C23A'
      if (score >= 60) return '#E6A23C'
      if (score >= 40) return '#F56C6C'
      return '#909399'
    },
    
    // 获取利润类型
    getProfitType(rating) {
      const types = {
        '优秀': 'success',
        '良好': 'primary',
        '一般': 'warning',
        '较差': 'danger'
      }
      return types[rating] || 'info'
    },
    
    // 获取决策类型
    getDecisionType(decision) {
      const types = {
        '强烈推荐': 'success',
        '推荐': 'primary',
        '谨慎推荐': 'warning',
        '不推荐': 'danger'
      }
      return types[decision] || 'info'
    },
    
    // 获取评分颜色
    getScoreColor(score) {
      if (score >= 80) return '#67C23A'
      if (score >= 65) return '#409EFF'
      if (score >= 50) return '#E6A23C'
      return '#F56C6C'
    },
    
    // 导出报告
    exportReport() {
      ElMessage.info('报告导出功能开发中...')
    },
    
    // 打印报告
    printReport() {
      ElMessage.info('报告打印功能开发中...')
    }
  }
}
</script>

<style scoped>
.product-ai-page {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.function-nav {
  margin-bottom: 20px;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.input-card, .result-card, .top-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 趋势预测样式 */
.trend-summary {
  margin-bottom: 20px;
}

.trend-predictions h4, .hot-keywords h4 {
  margin: 20px 0 10px;
  color: #303133;
}

.keywords-container {
  display: flex;
  flex-wrap: wrap;
}

/* 供应链风险样式 */
.risk-overview {
  margin-bottom: 20px;
}

.risk-breakdown {
  margin-top: 20px;
}

.risk-item {
  text-align: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.risk-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.risk-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.risk-details h4, .risk-recommendations h4 {
  margin: 20px 0 10px;
  color: #303133;
}

.risk-recommendations ul {
  padding-left: 20px;
  color: #606266;
}

.risk-recommendations li {
  margin-bottom: 8px;
}

/* 利润分析样式 */
.profit-summary {
  margin-bottom: 20px;
}

.profit-stat {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.stat-sub {
  font-size: 12px;
  color: #67C23A;
  margin-top: 5px;
}

.cost-structure h4, .optimization-suggestions h4 {
  margin: 20px 0 10px;
  color: #303133;
}

.optimization-suggestions ul {
  padding-left: 20px;
  color: #606266;
}

.optimization-suggestions li {
  margin-bottom: 8px;
}

/* 决策报告样式 */
.report-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.report-card ::v-deep .el-card__header {
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.report-card ::v-deep .el-card__body {
  background: rgba(255, 255, 255, 0.95);
  color: #303133;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.product-info h3 {
  margin: 0 0 10px;
  color: #303133;
}

.product-info p {
  margin: 5px 0;
  color: #909399;
  font-size: 13px;
}

.overall-score {
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 6px solid #409EFF;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.score-breakdown h4, .decision-factors h4, .key-insights h4 {
  margin: 20px 0 10px;
  color: #303133;
}

.score-item {
  margin-bottom: 15px;
}

.score-name {
  font-size: 13px;
  color: #606266;
  margin-bottom: 5px;
}

.decision-factors {
  margin-top: 20px;
}

.factor-section {
  padding: 15px;
  border-radius: 4px;
  min-height: 150px;
}

.factor-section.positive {
  background: #f0f9ff;
  border: 1px solid #d9ecff;
}

.factor-section.negative {
  background: #fef0f0;
  border: 1px solid #fde2e2;
}

.factor-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
}

.factor-section.positive h4 {
  color: #409EFF;
}

.factor-section.negative h4 {
  color: #F56C6C;
}

.factor-section ul {
  padding-left: 20px;
  margin: 0;
}

.factor-section li {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.empty-factor {
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

.key-insights {
  margin-top: 20px;
}

.insights-container {
  margin-top: 10px;
}

.report-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.report-footer .el-button {
  margin: 0 10px;
}

.report-tags {
  display: flex;
  align-items: center;
}

/* 变化样式 */
.change-positive {
  color: #67C23A;
  font-weight: bold;
}

.change-negative {
  color: #F56C6C;
  font-weight: bold;
}
</style>
