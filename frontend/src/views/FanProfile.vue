<template>
  <div class="fan-profile-page">
    <h1 class="page-title">📊 粉丝画像分析</h1>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <p>正在加载粉丝数据...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error">
      <p>❌ {{ error }}</p>
      <button @click="loadData">重试</button>
    </div>
    
    <!-- 主要内容 -->
    <div v-else class="content">
      <!-- 概览卡片 -->
      <div class="overview-cards">
        <div class="card">
          <h3>👥 总粉丝数</h3>
          <p class="number">{{ profileData.basic_profile?.total_fans || 0 }}</p>
        </div>
        <div class="card">
          <h3>📈 平均 LTV</h3>
          <p class="number">¥{{ profileData.ltv_analysis?.average_ltv || 0 }}</p>
        </div>
        <div class="card">
          <h3>⚠️ 流失风险</h3>
          <p class="number warning">{{ profileData.churn_warning?.at_risk_percentage || 0 }}%</p>
        </div>
        <div class="card">
          <h3>🚀 月均增长</h3>
          <p class="number">{{ profileData.growth_trend?.average_monthly_growth || 0 }}</p>
        </div>
      </div>
      
      <!-- 基础画像 -->
      <section class="section">
        <h2>📋 基础画像</h2>
        <div class="charts-grid">
          <div class="chart-container">
            <h3>年龄分布</h3>
            <div class="bar-chart">
              <div
                v-for="(item, key) in profileData.basic_profile?.age_distribution"
                :key="key"
                class="bar-item"
              >
                <div class="bar-label">{{ key }}</div>
                <div class="bar-wrapper">
                  <div
                    class="bar"
                    :style="{ width: item.percentage + '%' }"
                  ></div>
                  <span class="bar-value">{{ item.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="chart-container">
            <h3>性别比例</h3>
            <div class="pie-chart-simple">
              <div
                v-for="(item, key) in profileData.basic_profile?.gender_distribution"
                :key="key"
                class="gender-item"
              >
                <span class="gender-label">
                  {{ key === 'male' ? '👨 男性' : '👩 女性' }}
                </span>
                <span class="gender-value">{{ item.percentage }}%</span>
              </div>
            </div>
          </div>
          
          <div class="chart-container full-width">
            <h3>地区分布 TOP 10</h3>
            <div class="city-list">
              <div
                v-for="(item, city) in profileData.basic_profile?.city_distribution"
                :key="city"
                class="city-item"
              >
                <span class="city-name">{{ city }}</span>
                <div class="city-bar">
                  <div
                    class="city-fill"
                    :style="{ width: item.percentage * 3 + '%' }"
                  ></div>
                </div>
                <span class="city-value">{{ item.count }} ({{ item.percentage }}%)</span>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 活跃度分层 -->
      <section class="section">
        <h2>🔥 活跃度分层</h2>
        <div class="activity-grid">
          <div class="activity-card high">
            <h3>🌟 高活跃</h3>
            <p class="big-number">{{ profileData.activity_levels?.high_activity?.count || 0 }}</p>
            <p class="percentage">{{ profileData.activity_levels?.high_activity?.percentage || 0 }}%</p>
          </div>
          <div class="activity-card medium">
            <h3>💪 中活跃</h3>
            <p class="big-number">{{ profileData.activity_levels?.medium_activity?.count || 0 }}</p>
            <p class="percentage">{{ profileData.activity_levels?.medium_activity?.percentage || 0 }}%</p>
          </div>
          <div class="activity-card low">
            <h3>😴 低活跃</h3>
            <p class="big-number">{{ profileData.activity_levels?.low_activity?.count || 0 }}</p>
            <p class="percentage">{{ profileData.activity_levels?.low_activity?.percentage || 0 }}%</p>
          </div>
          <div class="activity-card dormant">
            <h3>💤 沉睡粉丝</h3>
            <p class="big-number">{{ profileData.activity_levels?.dormant?.count || 0 }}</p>
            <p class="percentage">{{ profileData.activity_levels?.dormant?.percentage || 0 }}%</p>
          </div>
        </div>
      </section>
      
      <!-- 兴趣标签 -->
      <section class="section">
        <h2>🏷️ 兴趣标签</h2>
        <div class="tags-cloud">
          <span
            v-for="tag in profileData.interest_tags?.tags"
            :key="tag.name"
            class="tag"
            :style="{ fontSize: getTagFontSize(tag.percentage) + 'px' }"
          >
            {{ tag.name }} ({{ tag.percentage }}%)
          </span>
        </div>
      </section>
      
      <!-- LTV 价值评估 -->
      <section class="section">
        <h2>💰 粉丝价值评估 (LTV)</h2>
        <div class="ltv-grid">
          <div class="ltv-card vip">
            <h3>👑 VIP</h3>
            <p class="big-number">{{ profileData.ltv_analysis?.distribution?.VIP?.count || 0 }}</p>
            <p class="percentage">{{ profileData.ltv_analysis?.distribution?.VIP?.percentage || 0 }}%</p>
            <p class="desc">LTV > ¥5000</p>
          </div>
          <div class="ltv-card high">
            <h3>💎 高价值</h3>
            <p class="big-number">{{ profileData.ltv_analysis?.distribution?.high_value?.count || 0 }}</p>
            <p class="percentage">{{ profileData.ltv_analysis?.distribution?.high_value?.percentage || 0 }}%</p>
            <p class="desc">¥2000 - ¥5000</p>
          </div>
          <div class="ltv-card medium">
            <h3>📦 中价值</h3>
            <p class="big-number">{{ profileData.ltv_analysis?.distribution?.medium_value?.count || 0 }}</p>
            <p class="percentage">{{ profileData.ltv_analysis?.distribution?.medium_value?.percentage || 0 }}%</p>
            <p class="desc">¥500 - ¥2000</p>
          </div>
          <div class="ltv-card low">
            <h3>🌱 低价值</h3>
            <p class="big-number">{{ profileData.ltv_analysis?.distribution?.low_value?.count || 0 }}</p>
            <p class="percentage">{{ profileData.ltv_analysis?.distribution?.low_value?.percentage || 0 }}%</p>
            <p class="desc">LTV ≤ ¥500</p>
          </div>
        </div>
        <div class="total-revenue">
          <h3>💵 总营收</h3>
          <p class="revenue-number">¥{{ profileData.ltv_analysis?.total_revenue || 0 }}</p>
        </div>
      </section>
      
      <!-- 流失预警 -->
      <section class="section">
        <h2>⚠️ 流失预警</h2>
        <div class="churn-warning">
          <div class="warning-stats">
            <div class="warning-item high-risk">
              <span class="warning-label">🔴 高风险</span>
              <span class="warning-count">{{ profileData.churn_warning?.risk_distribution?.high?.count || 0 }}</span>
            </div>
            <div class="warning-item medium-risk">
              <span class="warning-label">🟡 中风险</span>
              <span class="warning-count">{{ profileData.churn_warning?.risk_distribution?.medium?.count || 0 }}</span>
            </div>
            <div class="warning-item low-risk">
              <span class="warning-label">🟢 低风险</span>
              <span class="warning-count">{{ profileData.churn_warning?.risk_distribution?.low?.count || 0 }}</span>
            </div>
          </div>
          
          <div class="high-risk-list" v-if="profileData.churn_warning?.high_risk_fans?.length">
            <h3>高风险粉丝列表 (前 20)</h3>
            <table class="risk-table">
              <thead>
                <tr>
                  <th>粉丝 ID</th>
                  <th>风险分数</th>
                  <th>未活跃天数</th>
                  <th>互动分数</th>
                  <th>风险因素</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="fan in profileData.churn_warning?.high_risk_fans"
                  :key="fan.fan_id"
                >
                  <td>#{{ fan.fan_id }}</td>
                  <td class="risk-score">{{ fan.risk_score }}</td>
                  <td>{{ fan.days_inactive }}天</td>
                  <td>{{ fan.engagement_score }}</td>
                  <td>
                    <span
                      v-for="factor in fan.risk_factors"
                      :key="factor"
                      class="risk-factor"
                    >
                      {{ getRiskFactorLabel(factor) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
      
      <!-- 增长趋势 -->
      <section class="section">
        <h2>📈 粉丝增长趋势</h2>
        <div class="growth-chart">
          <div class="growth-stats">
            <div class="stat-item">
              <span class="stat-label">总增长</span>
              <span class="stat-value">{{ profileData.growth_trend?.total_growth || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">月均增长</span>
              <span class="stat-value">{{ profileData.growth_trend?.average_monthly_growth || 0 }}</span>
            </div>
          </div>
          <div class="monthly-growth">
            <div
              v-for="month in profileData.growth_trend?.monthly_data?.slice(0, 12)"
              :key="month.month"
              class="month-bar"
            >
              <div class="month-label">{{ month.month }}</div>
              <div class="month-bar-wrapper">
                <div
                  class="month-bar-fill"
                  :style="{ height: getMonthBarHeight(month.new_fans) + 'px' }"
                ></div>
              </div>
              <div class="month-value">{{ month.new_fans }}</div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 刷新按钮 -->
      <div class="actions">
        <button @click="loadData" class="refresh-btn">🔄 刷新数据</button>
        <button @click="exportReport" class="export-btn">📥 导出报告</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, defineComponent } from 'vue'

export default defineComponent({
  name: 'FanProfile',
  
  setup() {
    const loading = ref(true)
    const error = ref(null)
    const profileData = ref({})
    
    // API 基础 URL
    const API_BASE = '/api/fan'
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      error.value = null
      
      try {
        // 模拟 API 调用（实际项目中替换为真实 API）
        // const response = await fetch(`${API_BASE}/profile/full`)
        // const result = await response.json()
        // profileData.value = result.data
        
        // 使用模拟数据
        await simulateApiCall()
      } catch (err) {
        error.value = '加载失败：' + err.message
      } finally {
        loading.value = false
      }
    }
    
    // 模拟 API 调用
    const simulateApiCall = async () => {
      // 这里调用后端 API 获取真实数据
      // 暂时使用模拟数据展示效果
      profileData.value = {
        basic_profile: {
          total_fans: 1000,
          age_distribution: {
            '18-24': { count: 250, percentage: 25 },
            '25-34': { count: 350, percentage: 35 },
            '35-44': { count: 200, percentage: 20 },
            '45-54': { count: 150, percentage: 15 },
            '55+': { count: 50, percentage: 5 }
          },
          gender_distribution: {
            male: { count: 520, percentage: 52 },
            female: { count: 480, percentage: 48 }
          },
          city_distribution: {
            '北京': { count: 150, percentage: 15 },
            '上海': { count: 140, percentage: 14 },
            '广州': { count: 120, percentage: 12 },
            '深圳': { count: 110, percentage: 11 },
            '杭州': { count: 100, percentage: 10 },
            '成都': { count: 90, percentage: 9 },
            '武汉': { count: 80, percentage: 8 },
            '西安': { count: 70, percentage: 7 },
            '南京': { count: 70, percentage: 7 },
            '重庆': { count: 70, percentage: 7 }
          }
        },
        activity_levels: {
          high_activity: { count: 180, percentage: 18 },
          medium_activity: { count: 320, percentage: 32 },
          low_activity: { count: 350, percentage: 35 },
          dormant: { count: 150, percentage: 15 }
        },
        interest_tags: {
          tags: [
            { name: '科技', count: 450, percentage: 45 },
            { name: '娱乐', count: 380, percentage: 38 },
            { name: '美食', count: 320, percentage: 32 },
            { name: '旅游', count: 280, percentage: 28 },
            { name: '时尚', count: 250, percentage: 25 },
            { name: '体育', count: 220, percentage: 22 },
            { name: '游戏', count: 200, percentage: 20 },
            { name: '教育', count: 180, percentage: 18 },
            { name: '财经', count: 150, percentage: 15 },
            { name: '健康', count: 120, percentage: 12 }
          ],
          top_tags: ['科技', '娱乐', '美食', '旅游', '时尚']
        },
        ltv_analysis: {
          average_ltv: 2850.5,
          distribution: {
            VIP: { count: 85, percentage: 8.5 },
            high_value: { count: 220, percentage: 22 },
            medium_value: { count: 445, percentage: 44.5 },
            low_value: { count: 250, percentage: 25 }
          },
          total_revenue: 2850500
        },
        churn_warning: {
          total_at_risk: 280,
          at_risk_percentage: 28,
          risk_distribution: {
            high: { count: 45, percentage: 4.5 },
            medium: { count: 95, percentage: 9.5 },
            low: { count: 140, percentage: 14 }
          },
          high_risk_fans: [
            { fan_id: 123, risk_score: 85, days_inactive: 75, engagement_score: 22, risk_factors: ['long_inactive', 'low_engagement', 'low_interaction'] },
            { fan_id: 456, risk_score: 80, days_inactive: 68, engagement_score: 25, risk_factors: ['long_inactive', 'low_engagement'] },
            { fan_id: 789, risk_score: 75, days_inactive: 62, engagement_score: 28, risk_factors: ['long_inactive', 'low_interaction'] }
          ]
        },
        growth_trend: {
          total_growth: 1000,
          average_monthly_growth: 83.33,
          monthly_data: [
            { month: '2025-05', new_fans: 65 },
            { month: '2025-06', new_fans: 72 },
            { month: '2025-07', new_fans: 80 },
            { month: '2025-08', new_fans: 85 },
            { month: '2025-09', new_fans: 90 },
            { month: '2025-10', new_fans: 88 },
            { month: '2025-11', new_fans: 92 },
            { month: '2025-12', new_fans: 95 },
            { month: '2026-01', new_fans: 98 },
            { month: '2026-02', new_fans: 102 },
            { month: '2026-03', new_fans: 105 },
            { month: '2026-04', new_fans: 128 }
          ]
        }
      }
    }
    
    // 获取标签字体大小
    const getTagFontSize = (percentage) => {
      const minSize = 12
      const maxSize = 24
      return minSize + (percentage / 100) * (maxSize - minSize)
    }
    
    // 获取月份柱状图高度
    const getMonthBarHeight = (value) => {
      const maxValue = Math.max(...(profileData.value.growth_trend?.monthly_data?.map(m => m.new_fans) || [1]))
      return (value / maxValue) * 150
    }
    
    // 获取风险因素标签
    const getRiskFactorLabel = (factor) => {
      const labels = {
        'long_inactive': '长期未活跃',
        'moderate_inactive': '中度未活跃',
        'low_engagement': '低互动',
        'moderate_engagement': '中互动',
        'low_interaction': '互动少'
      }
      return labels[factor] || factor
    }
    
    // 导出报告
    const exportReport = () => {
      const dataStr = JSON.stringify(profileData.value, null, 2)
      const blob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `fan-profile-report-${new Date().toISOString().split('T')[0]}.json`
      link.click()
      URL.revokeObjectURL(url)
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      loading,
      error,
      profileData,
      loadData,
      getTagFontSize,
      getMonthBarHeight,
      getRiskFactorLabel,
      exportReport
    }
  }
})
</script>

<style scoped>
.fan-profile-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 30px;
  color: #1a1a1a;
}

.loading, .error {
  text-align: center;
  padding: 60px 20px;
  font-size: 18px;
}

.error {
  color: #dc3545;
}

.error button {
  margin-top: 15px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card h3 {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px 0;
}

.card .number {
  font-size: 32px;
  font-weight: bold;
  color: #1a1a1a;
  margin: 0;
}

.card .number.warning {
  color: #dc3545;
}

/* 区块 */
.section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.section h2 {
  font-size: 20px;
  margin: 0 0 20px 0;
  color: #1a1a1a;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.section h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 15px 0;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-container {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

/* 条形图 */
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 60px;
  font-size: 13px;
  color: #666;
}

.bar-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar {
  height: 20px;
  background: linear-gradient(90deg, #4facfe, #00f2fe);
  border-radius: 4px;
  min-width: 2px;
}

.bar-value {
  font-size: 13px;
  color: #666;
  min-width: 50px;
}

/* 饼图简化 */
.pie-chart-simple {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.gender-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 6px;
}

.gender-label {
  font-size: 14px;
}

.gender-value {
  font-weight: bold;
  color: #4facfe;
}

/* 城市列表 */
.city-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.city-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.city-name {
  width: 60px;
  font-size: 13px;
}

.city-bar {
  flex: 1;
  height: 12px;
  background: #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.city-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 6px;
}

.city-value {
  width: 100px;
  font-size: 12px;
  color: #666;
  text-align: right;
}

/* 活跃度网格 */
.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.activity-card {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  color: white;
}

.activity-card.high {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.activity-card.medium {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.activity-card.low {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.activity-card.dormant {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.activity-card h3 {
  color: white;
  margin: 0 0 10px 0;
  font-size: 16px;
}

.activity-card .big-number {
  font-size: 36px;
  font-weight: bold;
  margin: 10px 0;
}

.activity-card .percentage {
  font-size: 14px;
  opacity: 0.9;
}

/* 标签云 */
.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 15px;
}

.tag {
  display: inline-block;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  transition: transform 0.2s;
}

.tag:hover {
  transform: scale(1.05);
}

/* LTV 网格 */
.ltv-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.ltv-card {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  border: 2px solid;
}

.ltv-card.vip {
  border-color: #ffd700;
  background: #fffbea;
}

.ltv-card.high {
  border-color: #silver;
  background: #f8f9fa;
}

.ltv-card.medium {
  border-color: #cd7f32;
  background: #fff8f0;
}

.ltv-card.low {
  border-color: #8b4513;
  background: #f5f5f5;
}

.ltv-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.ltv-card .big-number {
  font-size: 32px;
  font-weight: bold;
  margin: 10px 0;
}

.ltv-card .percentage {
  font-size: 14px;
  color: #666;
}

.ltv-card .desc {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.total-revenue {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 10px;
}

.total-revenue h3 {
  color: white;
  margin: 0 0 10px 0;
}

.revenue-number {
  font-size: 36px;
  font-weight: bold;
  margin: 0;
}

/* 流失预警 */
.churn-warning {
  padding: 15px;
}

.warning-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.warning-item {
  flex: 1;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.warning-item.high-risk {
  background: #ffe6e6;
  border: 2px solid #dc3545;
}

.warning-item.medium-risk {
  background: #fff3cd;
  border: 2px solid #ffc107;
}

.warning-item.low-risk {
  background: #d4edda;
  border: 2px solid #28a745;
}

.warning-label {
  font-size: 14px;
  font-weight: bold;
}

.warning-count {
  font-size: 28px;
  font-weight: bold;
}

.risk-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.risk-table th,
.risk-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.risk-table th {
  background: #f8f9fa;
  font-weight: 600;
  font-size: 13px;
}

.risk-table td {
  font-size: 13px;
}

.risk-score {
  font-weight: bold;
  color: #dc3545;
}

.risk-factor {
  display: inline-block;
  padding: 4px 8px;
  background: #ffe6e6;
  color: #dc3545;
  border-radius: 4px;
  font-size: 11px;
  margin-right: 5px;
}

/* 增长趋势 */
.growth-chart {
  padding: 15px;
}

.growth-stats {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a;
}

.monthly-growth {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  height: 200px;
  padding: 20px 10px;
  background: #f8f9fa;
  border-radius: 8px;
  overflow-x: auto;
}

.month-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 50px;
}

.month-label {
  font-size: 11px;
  color: #666;
  transform: rotate(-45deg);
  transform-origin: right top;
}

.month-bar-wrapper {
  width: 30px;
  height: 150px;
  background: #e9ecef;
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.month-bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #4facfe, #00f2fe);
  border-radius: 4px 4px 0 0;
  min-height: 2px;
}

.month-value {
  font-size: 12px;
  font-weight: bold;
  color: #1a1a1a;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  padding: 20px;
}

.refresh-btn,
.export-btn {
  padding: 12px 30px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn {
  background: #007bff;
  color: white;
}

.refresh-btn:hover {
  background: #0056b3;
}

.export-btn {
  background: #28a745;
  color: white;
}

.export-btn:hover {
  background: #1e7e34;
}

/* 响应式 */
@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-grid,
  .ltv-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .warning-stats {
    flex-direction: column;
  }
  
  .monthly-growth {
    height: 250px;
  }
}
</style>
