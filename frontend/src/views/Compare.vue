<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CompareChart from '../components/CompareChart.vue'
import JSZip from 'jszip'

interface LiveRoomMetrics {
  room_id: string
  room_name: string
  total_viewers: number
  avg_duration: number
  engagement_rate: number
  conversion_rate: number
  emotion_avg: number
  emotion_peak: number
  interaction_count: number
  speech_quality: number
  content_quality: number
  rhythm_control: number
  retention_rate: number
}

interface EmotionDataPoint {
  time: string
  value: number
}

interface CompareData {
  timestamp: string
  rooms: LiveRoomMetrics[]
  metrics_comparison: Record<string, any[]>
  radar_data: Record<string, number[]>
  emotion_curves: Record<string, EmotionDataPoint[]>
  ai_analysis: {
    summary: string
    best_performer: {
      room_name: string
      strengths: string[]
    }
    needs_improvement: {
      room_name: string
      weaknesses: string[]
    }
    key_differences: string[]
    details: any[]
  }
  recommendations: string[]
}

// API 基础 URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 状态
const loading = ref(false)
const roomIdsInput = ref('room_001, room_002, room_003')
const compareData = ref<CompareData | null>(null)
const activeChart = ref<'metrics' | 'emotion' | 'radar'>('metrics')

// 计算属性
const hasData = computed(() => compareData.value !== null)

const chartHeight = computed(() => {
  return window.innerWidth < 768 ? '300px' : '400px'
})

// 方法
const parseRoomIds = (): string[] => {
  return roomIdsInput.value
    .split(',')
    .map(id => id.trim())
    .filter(id => id.length > 0)
}

const fetchCompareData = async () => {
  const roomIds = parseRoomIds()
  
  if (roomIds.length < 2) {
    ElMessage.warning('请至少输入两个直播间 ID，用逗号分隔')
    return
  }
  
  loading.value = true
  
  try {
    const response = await fetch(`${API_BASE}/api/compare/?room_ids=${roomIds.join(',')}`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      compareData.value = result.data
      ElMessage.success(`成功对比${result.data.rooms.length}个直播间，耗时${result.elapsed_time}秒`)
    } else {
      throw new Error(result.message || '对比失败')
    }
  } catch (error: any) {
    console.error('对比分析失败:', error)
    ElMessage.error(`对比分析失败：${error.message}`)
    
    // 使用模拟数据演示
    compareData.value = generateMockData(roomIds)
    ElMessage.info('已加载模拟数据用于演示')
  } finally {
    loading.value = false
  }
}

const generateMockData = (roomIds: string[]): CompareData => {
  const rooms: LiveRoomMetrics[] = roomIds.map((id, index) => ({
    room_id: id,
    room_name: `直播间${id.slice(-4)}`,
    total_viewers: 10000 + index * 5000,
    avg_duration: 45 + index * 5,
    engagement_rate: 75 + index * 5,
    conversion_rate: 3 + index * 1.5,
    emotion_avg: 65 + index * 8,
    emotion_peak: 85 + index * 5,
    interaction_count: 2000 + index * 1500,
    speech_quality: 80 + index * 5,
    content_quality: 75 + index * 6,
    rhythm_control: 72 + index * 7,
    retention_rate: 68 + index * 8
  }))
  
  const emotionCurves: Record<string, EmotionDataPoint[]> = {}
  roomIds.forEach((id, index) => {
    const roomName = `直播间${id.slice(-4)}`
    const baseEmotion = 60 + index * 10
    emotionCurves[roomName] = Array.from({ length: 10 }, (_, i) => ({
      time: `${(i * 5).toString().padStart(2, '0')}:00`,
      value: Math.min(100, Math.max(0, baseEmotion + Math.random() * 30 - 15 + (i === 3 || i === 7 ? 15 : 0)))
    }))
  })
  
  const radarData: Record<string, number[]> = {}
  rooms.forEach(room => {
    radarData[room.room_name] = [
      room.content_quality,
      room.engagement_rate,
      room.rhythm_control,
      room.speech_quality,
      room.retention_rate
    ]
  })
  
  return {
    timestamp: new Date().toISOString(),
    rooms,
    metrics_comparison: {
      conversion_rate: rooms.map(r => ({ room_id: r.room_id, room_name: r.room_name, value: r.conversion_rate })),
      engagement_rate: rooms.map(r => ({ room_id: r.room_id, room_name: r.room_name, value: r.engagement_rate })),
      emotion_avg: rooms.map(r => ({ room_id: r.room_id, room_name: r.room_name, value: r.emotion_avg })),
      retention_rate: rooms.map(r => ({ room_id: r.room_id, room_name: r.room_name, value: r.retention_rate }))
    },
    radar_data: radarData,
    emotion_curves: emotionCurves,
    ai_analysis: {
      summary: `共对比${rooms.length}个直播间，${rooms[rooms.length - 1].room_name}表现最佳`,
      best_performer: {
        room_name: rooms[rooms.length - 1].room_name,
        strengths: [
          '转化率领先平均水平',
          '互动率高，观众参与度高',
          '情绪值稳定在高位'
        ]
      },
      needs_improvement: {
        room_name: rooms[0].room_name,
        weaknesses: [
          '转化率有待提升',
          '互动环节较少',
          '观众留存率需优化'
        ]
      },
      key_differences: [
        `转化率差距：${(rooms[rooms.length - 1].conversion_rate - rooms[0].conversion_rate).toFixed(1)}%`,
        `互动率差距：${(rooms[rooms.length - 1].engagement_rate - rooms[0].engagement_rate).toFixed(1)}%`
      ],
      details: rooms.map(room => ({
        room_name: room.room_name,
        performance: room.engagement_rate > 80 ? '优秀' : '待提升',
        highlights: [
          `转化率：${room.conversion_rate.toFixed(1)}%`,
          `互动率：${room.engagement_rate.toFixed(1)}%`,
          `情绪值：${room.emotion_avg.toFixed(1)}`,
          `留存率：${room.retention_rate.toFixed(1)}%`
        ]
      }))
    },
    recommendations: [
      '建议学习表现最佳直播间的话术结构',
      '增加互动环节如抽奖、问答提升参与度',
      '优化开场内容，前 5 分钟设置爆点',
      '调整直播节奏，增加高潮环节'
    ]
  }
}

const exportReport = async (format: 'pdf' | 'json' = 'pdf') => {
  if (!compareData.value) {
    ElMessage.warning('请先生成对比数据')
    return
  }
  
  try {
    const roomIds = parseRoomIds()
    const response = await fetch(`${API_BASE}/api/compare/export/${format === 'pdf' ? 'pdf' : ''}/${roomIds.join(',')}`, {
      method: 'GET'
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `compare_report_${new Date().getTime()}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('报告导出成功')
    } else {
      const result = await response.json()
      if (result.file_path) {
        ElMessage.success(`报告已生成：${result.file_path}`)
      } else {
        throw new Error(result.message || '导出失败')
      }
    }
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(`导出失败：${error.message}`)
  }
}

const copyRecommendations = async () => {
  if (!compareData.value) return
  
  const text = compareData.value.recommendations.join('\n')
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('建议已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

onMounted(() => {
  // 自动加载一次示例数据
  fetchCompareData()
})
</script>

<template>
  <div class="compare-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📊 多直播间对比分析</h1>
      <p class="subtitle">对比不同直播间效果，发现优化空间</p>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>🎯 选择直播间</span>
          </div>
        </template>
        
        <div class="input-row">
          <el-input
            v-model="roomIdsInput"
            placeholder="请输入直播间 ID，用逗号分隔（例如：room_001, room_002, room_003）"
            clearable
            @keyup.enter="fetchCompareData"
          >
            <template #prefix>
              <span>🏠</span>
            </template>
          </el-input>
          
          <el-button
            type="primary"
            :loading="loading"
            @click="fetchCompareData"
          >
            🚀 开始对比
          </el-button>
        </div>
        
        <div class="input-tips">
          💡 提示：至少需要两个直播间才能进行对比分析
        </div>
      </el-card>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-section">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 结果区域 -->
    <div v-else-if="hasData" class="results-section">
      <!-- 直播间概览表 -->
      <el-card class="overview-card">
        <template #header>
          <div class="card-header">
            <span>📋 直播间概览</span>
          </div>
        </template>
        
        <el-table :data="compareData!.rooms" stripe style="width: 100%">
          <el-table-column prop="room_name" label="直播间" width="150" />
          <el-table-column prop="total_viewers" label="观众数" width="100">
            <template #default="{ row }">
              {{ row.total_viewers.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="engagement_rate" label="互动率" width="100">
            <template #default="{ row }">
              {{ row.engagement_rate.toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="conversion_rate" label="转化率" width="100">
            <template #default="{ row }">
              {{ row.conversion_rate.toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="emotion_avg" label="情绪值" width="100">
            <template #default="{ row }">
              {{ row.emotion_avg.toFixed(1) }}
            </template>
          </el-table-column>
          <el-table-column prop="retention_rate" label="留存率" width="100">
            <template #default="{ row }">
              {{ row.retention_rate.toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="avg_duration" label="平均时长 (分钟)" width="120">
            <template #default="{ row }">
              {{ row.avg_duration.toFixed(1) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 图表切换 -->
      <div class="chart-tabs">
        <el-button-group>
          <el-button
            :type="activeChart === 'metrics' ? 'primary' : ''"
            @click="activeChart = 'metrics'"
          >
            📊 指标对比
          </el-button>
          <el-button
            :type="activeChart === 'emotion' ? 'primary' : ''"
            @click="activeChart = 'emotion'"
          >
            📈 情绪曲线
          </el-button>
          <el-button
            :type="activeChart === 'radar' ? 'primary' : ''"
            @click="activeChart = 'radar'"
          >
            🎯 五维评分
          </el-button>
        </el-button-group>
      </div>

      <!-- 对比图表 -->
      <el-card class="chart-card">
        <CompareChart
          :emotion-data="compareData!.emotion_curves"
          :metrics-data="compareData!.metrics_comparison"
          :radar-data="compareData!.radar_data"
          :height="chartHeight"
          :chart-type="activeChart"
        />
      </el-card>

      <!-- AI 分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>🤖 AI 差异分析</span>
          </div>
        </template>
        
        <div class="analysis-content">
          <div class="analysis-summary">
            <el-alert
              :title="compareData!.ai_analysis.summary"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
          
          <div class="analysis-grid">
            <div class="analysis-item best">
              <h4>🏆 表现最佳：{{ compareData!.ai_analysis.best_performer.room_name }}</h4>
              <ul>
                <li v-for="(strength, index) in compareData!.ai_analysis.best_performer.strengths" :key="index">
                  {{ strength }}
                </li>
              </ul>
            </div>
            
            <div class="analysis-item improvement">
              <h4>📈 待提升：{{ compareData!.ai_analysis.needs_improvement.room_name }}</h4>
              <ul>
                <li v-for="(weakness, index) in compareData!.ai_analysis.needs_improvement.weaknesses" :key="index">
                  {{ weakness }}
                </li>
              </ul>
            </div>
          </div>
          
          <div class="key-differences">
            <h4>📊 关键差异:</h4>
            <ul>
              <li v-for="(diff, index) in compareData!.ai_analysis.key_differences" :key="index">
                {{ diff }}
              </li>
            </ul>
          </div>
        </div>
      </el-card>

      <!-- 优化建议 -->
      <el-card class="recommendations-card">
        <template #header>
          <div class="card-header">
            <span>💡 优化建议</span>
            <el-button size="small" @click="copyRecommendations">
              📋 复制
            </el-button>
          </div>
        </template>
        
        <div class="recommendations-list">
          <div
            v-for="(rec, index) in compareData!.recommendations"
            :key="index"
            class="recommendation-item"
          >
            <span class="rec-number">{{ index + 1 }}</span>
            <span class="rec-text">{{ rec }}</span>
          </div>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button type="primary" @click="exportReport('pdf')">
          📥 导出 PDF 报告
        </el-button>
        <el-button @click="exportReport('json')">
          📥 导出 JSON
        </el-button>
        <el-button @click="fetchCompareData">
          🔄 重新对比
        </el-button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="请输入直播间 ID 开始对比分析" />
    </div>
  </div>
</template>

<style scoped>
.compare-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 10px 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.input-section {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.input-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.input-row .el-input {
  flex: 1;
}

.input-tips {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.loading-section {
  margin-bottom: 30px;
}

.results-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview-card {
  margin-bottom: 20px;
}

.chart-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.chart-card {
  margin-bottom: 20px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-summary {
  margin-bottom: 10px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.analysis-item {
  padding: 20px;
  border-radius: 8px;
  background: #f5f7fa;
}

.analysis-item.best {
  border-left: 4px solid #67C23A;
}

.analysis-item.improvement {
  border-left: 4px solid #E6A23C;
}

.analysis-item h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.analysis-item ul {
  margin: 0;
  padding-left: 20px;
}

.analysis-item li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.6;
}

.key-differences {
  padding: 15px;
  background: #f0f9eb;
  border-radius: 8px;
}

.key-differences h4 {
  margin: 0 0 10px 0;
  color: #67C23A;
}

.key-differences ul {
  margin: 0;
  padding-left: 20px;
}

.key-differences li {
  margin-bottom: 5px;
  color: #606266;
}

.recommendations-card {
  margin-bottom: 20px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.rec-number {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409EFF;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.rec-text {
  flex: 1;
  color: #606266;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 20px 0;
}

.empty-state {
  padding: 60px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .compare-page {
    padding: 15px;
  }

  .page-header h1 {
    font-size: 22px;
  }

  .input-row {
    flex-direction: column;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
