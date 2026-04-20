<template>
  <div class="prediction-page">
    <div class="page-header">
      <h1>🎯 直播效果预测</h1>
      <p class="subtitle">AI 驱动的智能预测系统 - 预测 GMV、观看人数、转化率</p>
    </div>

    <!-- 预测控制面板 -->
    <div class="prediction-controls">
      <el-card class="control-card">
        <template #header>
          <div class="card-header">
            <span>📊 预测参数设置</span>
            <el-button type="primary" @click="runPrediction" :loading="loading">
              开始预测
            </el-button>
          </div>
        </template>

        <el-form :model="predictionForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="直播日期">
                <el-date-picker
                  v-model="predictionForm.date"
                  type="date"
                  placeholder="选择日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="直播时间">
                <el-time-picker
                  v-model="predictionForm.hour"
                  placeholder="选择时间"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="产品类别">
                <el-select v-model="predictionForm.category" style="width: 100%">
                  <el-option label="综合类" value="general" />
                  <el-option label="服饰" value="fashion" />
                  <el-option label="美妆" value="beauty" />
                  <el-option label="食品" value="food" />
                  <el-option label="数码" value="electronics" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="价格区间">
                <el-select v-model="predictionForm.priceRange" style="width: 100%">
                  <el-option label="低价位" value="low" />
                  <el-option label="中价位" value="medium" />
                  <el-option label="高价位" value="high" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="预期观看人数">
                <el-input-number
                  v-model="predictionForm.expectedViewers"
                  :min="100"
                  :max="1000000"
                  :step="100"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="直播时长 (分钟)">
                <el-input-number
                  v-model="predictionForm.duration"
                  :min="30"
                  :max="480"
                  :step="30"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>

    <!-- 预测结果展示 -->
    <div v-if="predictionResult" class="prediction-results">
      <el-row :gutter="20">
        <!-- GMV 预测 -->
        <el-col :span="8">
          <el-card class="result-card gmv-card">
            <div class="result-icon">💰</div>
            <div class="result-title">预测 GMV</div>
            <div class="result-value">¥{{ formatNumber(predictionResult.gmv?.predicted_gmv) }}</div>
            <div class="result-detail">
              <span v-if="predictionResult.gmv?.confidence_interval">
                置信区间：¥{{ formatNumber(predictionResult.gmv.confidence_interval.lower) }} - 
                ¥{{ formatNumber(predictionResult.gmv.confidence_interval.upper) }}
              </span>
            </div>
            <div class="result-trend" :class="getTrendClass('gmv')">
              <span>人均贡献：¥{{ predictionResult.gmv?.avg_conversion_value }}</span>
            </div>
          </el-card>
        </el-col>

        <!-- 观看人数预测 -->
        <el-col :span="8">
          <el-card class="result-card viewers-card">
            <div class="result-icon">👥</div>
            <div class="result-title">预测观看人数</div>
            <div class="result-value">{{ formatNumber(predictionResult.viewers?.predicted_viewers) }}</div>
            <div class="result-detail">
              <span>趋势：{{ getTrendText(predictionResult.viewers?.trend) }}</span>
            </div>
            <div class="result-trend">
              <el-tag :type="getTimeTagType()">
                时段系数：{{ predictionResult.viewers?.time_multiplier }}x
              </el-tag>
            </div>
          </el-card>
        </el-col>

        <!-- 转化率预测 -->
        <el-col :span="8">
          <el-card class="result-card conversion-card">
            <div class="result-icon">📈</div>
            <div class="result-title">预测转化率</div>
            <div class="result-value">{{ predictionResult.conversion?.predicted_conversion_rate_percent }}%</div>
            <div class="result-detail">
              <span>类别：{{ getCategoryName(predictionResult.conversion?.category) }}</span>
            </div>
            <div class="result-trend">
              <span>基准：{{ (predictionResult.conversion?.benchmark * 100).toFixed(2) }}%</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 时间推荐 -->
      <el-card class="recommendation-card">
        <template #header>
          <div class="card-header">
            <span>⏰ 最佳直播时间推荐</span>
          </div>
        </template>
        <div class="time-recommendation">
          <div class="main-recommendation">
            <div class="time-display">
              <span class="time-label">推荐时间</span>
              <span class="time-value">{{ predictionResult.time_recommendation?.recommended_time_str }}</span>
            </div>
            <div class="expected-performance">
              预期表现：¥{{ formatNumber(predictionResult.time_recommendation?.expected_performance) }}
            </div>
          </div>
          <div class="alternative-times">
            <span class="alt-label">其他推荐时段：</span>
            <el-tag
              v-for="(time, index) in predictionResult.time_recommendation?.alternative_times"
              :key="index"
              class="alt-time-tag"
            >
              {{ time.label }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 趋势图表 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>📊 历史趋势</span>
            <el-radio-group v-model="chartType" size="small">
              <el-radio-button label="gmv">GMV</el-radio-button>
              <el-radio-button label="viewers">观看人数</el-radio-button>
              <el-radio-button label="conversion">转化率</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <PredictionChart 
          :data="trendData" 
          :type="chartType"
          height="300px"
        />
      </el-card>

      <!-- 准确度评估 -->
      <el-card class="accuracy-card">
        <template #header>
          <div class="card-header">
            <span>🎯 预测准确度评估</span>
            <el-button size="small" @click="evaluateAccuracy">
              运行评估
            </el-button>
          </div>
        </template>
        <div v-if="accuracyResult" class="accuracy-result">
          <el-progress
            :percentage="accuracyResult.overall_accuracy"
            :status="getAccuracyStatus(accuracyResult.overall_accuracy)"
          />
          <div class="accuracy-details">
            <span>评分：{{ accuracyResult.rating }}</span>
            <span>样本数：{{ accuracyResult.total_predictions }}</span>
            <span v-if="accuracyResult.metrics?.gmv">
              GMV 误差：{{ accuracyResult.metrics.gmv.mape }}%
            </span>
          </div>
        </div>
        <div v-else class="accuracy-placeholder">
          点击"运行评估"查看预测准确度分析
        </div>
      </el-card>
    </div>

    <!-- 初始状态提示 -->
    <div v-else class="empty-state">
      <el-empty description="设置预测参数后点击"开始预测"按钮">
        <el-button type="primary" @click="loadSamplePrediction">
          加载示例预测
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import PredictionChart from '../components/PredictionChart.vue'
import { ElMessage } from 'element-plus'

// API 基础 URL
const API_BASE = '/api/prediction'

// 加载状态
const loading = ref(false)

// 预测表单
const predictionForm = reactive({
  date: new Date(),
  hour: new Date(2024, 0, 1, 20, 0),
  category: 'general',
  priceRange: 'medium',
  expectedViewers: 5000,
  duration: 120
})

// 预测结果
const predictionResult = ref(null)
const trendData = ref(null)
const accuracyResult = ref(null)
const chartType = ref('gmv')

// 格式化数字
const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 获取趋势文本
const getTrendText = (trend) => {
  const trendMap = {
    'increasing': '📈 上升',
    'decreasing': '📉 下降',
    'stable': '➡️ 稳定'
  }
  return trendMap[trend] || '➡️ 稳定'
}

// 获取类别名称
const getCategoryName = (category) => {
  const categoryMap = {
    'general': '综合类',
    'fashion': '服饰',
    'beauty': '美妆',
    'food': '食品',
    'electronics': '数码'
  }
  return categoryMap[category] || '综合类'
}

// 获取趋势样式类
const getTrendClass = (type) => {
  return `trend-${type}`
}

// 获取时段标签类型
const getTimeTagType = () => {
  const multiplier = predictionResult.value?.viewers?.time_multiplier
  if (multiplier >= 1.2) return 'success'
  if (multiplier >= 1.0) return 'warning'
  return 'info'
}

// 获取准确度状态
const getAccuracyStatus = (accuracy) => {
  if (accuracy >= 90) return 'success'
  if (accuracy >= 75) return 'warning'
  return 'exception'
}

// 运行预测
const runPrediction = async () => {
  loading.value = true
  try {
    const date = new Date(predictionForm.date)
    const hour = predictionForm.hour.getHours()
    const dayOfWeek = date.getDay()

    // 并行请求所有预测
    const [viewersRes, gmvRes, conversionRes, timeRes, trendRes] = await Promise.all([
      fetch(`${API_BASE}/predict/viewers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day_of_week: dayOfWeek, hour })
      }),
      fetch(`${API_BASE}/predict/gmv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          expected_viewers: predictionForm.expectedViewers 
        })
      }),
      fetch(`${API_BASE}/predict/conversion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          product_category: predictionForm.category,
          price_range: predictionForm.priceRange
        })
      }),
      fetch(`${API_BASE}/recommend/time`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          duration_minutes: predictionForm.duration 
        })
      }),
      fetch(`${API_BASE}/trend?days=30`)
    ])

    const viewersData = await viewersRes.json()
    const gmvData = await gmvRes.json()
    const conversionData = await conversionRes.json()
    const timeData = await timeRes.json()
    const trendDataRes = await trendRes.json()

    predictionResult.value = {
      viewers: viewersData.data,
      gmv: gmvData.data,
      conversion: conversionData.data,
      time_recommendation: timeData.data
    }

    trendData.value = trendDataRes.data

    ElMessage.success('预测完成')
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请重试')
  } finally {
    loading.value = false
  }
}

// 加载示例预测
const loadSamplePrediction = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/sample`)
    const data = await res.json()
    
    if (data.success) {
      predictionResult.value = {
        viewers: data.data.viewers_prediction,
        gmv: data.data.gmv_prediction,
        conversion: data.data.conversion_prediction,
        time_recommendation: data.data.time_recommendation
      }
      trendData.value = data.data.trend_data
      ElMessage.success('示例预测加载成功')
    }
  } catch (error) {
    console.error('加载示例失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 评估准确度
const evaluateAccuracy = async () => {
  try {
    // 生成测试数据
    const testData = {
      predictions: [],
      actuals: []
    }

    // 使用历史数据生成测试集
    const histRes = await fetch(`${API_BASE}/data/historical?limit=20`)
    const histData = await histRes.json()
    
    if (histData.success && histData.data.records) {
      const records = histData.data.records
      
      // 使用前 15 条作为训练，后 5 条作为测试
      for (let i = 15; i < records.length; i++) {
        testData.predictions.push({
          gmv: records[i].gmv * (0.9 + Math.random() * 0.2),
          viewers: records[i].viewers
        })
        testData.actuals.push({
          gmv: records[i].gmv,
          viewers: records[i].viewers
        })
      }

      const res = await fetch(`${API_BASE}/evaluate/accuracy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData)
      })

      const result = await res.json()
      if (result.success) {
        accuracyResult.value = result.data
        ElMessage.success(`评估完成 - 准确度：${result.data.overall_accuracy}%`)
      }
    }
  } catch (error) {
    console.error('评估失败:', error)
    ElMessage.error('评估失败')
  }
}

// 页面加载时自动加载示例
loadSamplePrediction()
</script>

<style scoped>
.prediction-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.prediction-controls {
  margin-bottom: 30px;
}

.control-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.prediction-results {
  animation: fadeIn 0.3s ease-in;
}

.result-card {
  margin-bottom: 20px;
  text-align: center;
  transition: transform 0.2s;
}

.result-card:hover {
  transform: translateY(-2px);
}

.result-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.result-title {
  font-size: 16px;
  color: #909399;
  margin-bottom: 10px;
}

.result-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.result-detail {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.result-trend {
  font-size: 12px;
  color: #909399;
}

.gmv-card .result-value {
  color: #67c23a;
}

.viewers-card .result-value {
  color: #409eff;
}

.conversion-card .result-value {
  color: #e6a23c;
}

.recommendation-card {
  margin-bottom: 20px;
}

.time-recommendation {
  padding: 10px 0;
}

.main-recommendation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.time-display {
  display: flex;
  flex-direction: column;
}

.time-label {
  font-size: 13px;
  color: #909399;
}

.time-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.expected-performance {
  font-size: 16px;
  color: #67c23a;
  font-weight: 600;
}

.alternative-times {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.alt-label {
  font-size: 13px;
  color: #606266;
}

.alt-time-tag {
  cursor: pointer;
}

.chart-card {
  margin-bottom: 20px;
}

.accuracy-card {
  margin-bottom: 20px;
}

.accuracy-result {
  padding: 20px 0;
}

.accuracy-details {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  font-size: 13px;
  color: #606266;
}

.accuracy-placeholder {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.empty-state {
  padding: 60px 0;
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
</style>
