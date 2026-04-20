<template>
  <div class="script-timeline">
    <div class="timeline-header">
      <h3>📅 直播时间轴</h3>
      <div class="timeline-controls">
        <el-button size="small" @click="zoomIn">
          <i class="el-icon-zoom-in"></i> 放大
        </el-button>
        <el-button size="small" @click="zoomOut">
          <i class="el-icon-zoom-out"></i> 缩小
        </el-button>
        <el-button size="small" @click="resetZoom">
          <i class="el-icon-refresh"></i> 重置
        </el-button>
      </div>
    </div>

    <!-- 时间轴概览 -->
    <div class="timeline-overview">
      <div class="overview-info">
        <el-tag>{{ script.title }}</el-tag>
        <span class="duration-badge">{{ getTotalDuration() }}分钟</span>
        <span class="segments-count">共{{ script.segments?.length || 0 }}个片段</span>
      </div>
    </div>

    <!-- 可视化时间轴 -->
    <div class="timeline-visual" ref="timelineContainer">
      <div class="timeline-track">
        <div 
          v-for="(segment, idx) in script.segments" 
          :key="segment.segment_id"
          class="timeline-segment"
          :style="getSegmentStyle(segment)"
          :class="['segment-' + segment.segment_type, { 'active': activeSegment === segment.segment_id }]"
          @click="selectSegment(segment)"
        >
          <div class="segment-label">
            <span class="segment-icon">{{ getSegmentIcon(segment.segment_type) }}</span>
            <span class="segment-title">{{ segment.title }}</span>
            <span class="segment-time">{{ segment.start_time }}</span>
          </div>
        </div>
      </div>
      
      <!-- 时间刻度 -->
      <div class="timeline-scale">
        <div v-for="mark in timeMarks" :key="mark.time" class="scale-mark" :style="{ left: mark.position + '%' }">
          <span>{{ mark.time }}</span>
        </div>
      </div>
    </div>

    <!-- 片段详情 -->
    <div class="segments-detail">
      <el-collapse v-model="activeSegments" accordion>
        <el-collapse-item 
          v-for="(segment, idx) in script.segments" 
          :key="segment.segment_id"
          :name="segment.segment_id"
        >
          <template #title>
            <div class="segment-title-row">
              <el-tag :type="getSegmentTypeColor(segment.segment_type)" size="small">
                {{ getSegmentTypeLabel(segment.segment_type) }}
              </el-tag>
              <span class="segment-time-badge">
                {{ segment.start_time }} - {{ segment.end_time }}
              </span>
              <span class="segment-duration-badge">
                {{ segment.duration_minutes }}分钟
              </span>
              <span class="segment-name">{{ segment.title }}</span>
            </div>
          </template>
          
          <div class="segment-detail-content">
            <div class="detail-section">
              <h4>📝 脚本内容</h4>
              <div class="script-content" v-html="formatContent(segment.script_content)"></div>
            </div>
            
            <div v-if="segment.notes && segment.notes.length" class="detail-section">
              <h4>⚠️ 注意事项</h4>
              <ul class="notes-list">
                <li v-for="(note, nidx) in segment.notes" :key="nidx">{{ note }}</li>
              </ul>
            </div>
            
            <div v-if="segment.products && segment.products.length" class="detail-section">
              <h4>📦 相关产品</h4>
              <el-table :data="segment.products" size="small" border>
                <el-table-column prop="product_name" label="产品" width="150" />
                <el-table-column label="价格" width="120">
                  <template #default="{ row }">
                    <span style="color: #F56C6C; font-weight: bold;">¥{{ row.price }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="start_time" label="上架时间" width="100" />
                <el-table-column prop="end_time" label="下架时间" width="100" />
                <el-table-column label="卖点">
                  <template #default="{ row }">
                    {{ (row.selling_points || []).join('、') }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <div v-if="segment.interactions && segment.interactions.length" class="detail-section">
              <h4>🎮 互动环节</h4>
              <el-table :data="segment.interactions" size="small" border>
                <el-table-column prop="name" label="互动名称" width="120" />
                <el-table-column prop="duration_minutes" label="时长" width="80">
                  <template #default="{ row }">{{ row.duration_minutes }}分钟</template>
                </el-table-column>
                <el-table-column prop="description" label="描述" />
                <el-table-column label="奖品">
                  <template #default="{ row }">
                    <el-tag v-for="(prize, pidx) in (row.prizes || [])" :key="pidx" size="small" style="margin-right: 5px;">
                      {{ prize }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 统计信息 -->
    <div class="timeline-stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ script.segments?.length || 0 }}</div>
            <div class="stat-label">总片段数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ getTotalProducts() }}</div>
            <div class="stat-label">产品数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ getTotalInteractions() }}</div>
            <div class="stat-label">互动数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ script.emergency_plans?.length || 0 }}</div>
            <div class="stat-label">应急预案</div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  script: {
    type: Object,
    required: true
  }
})

const activeSegment = ref(null)
const activeSegments = ref(null)
const timelineContainer = ref(null)
const zoomLevel = ref(1)

// 时间刻度
const timeMarks = computed(() => {
  const duration = getTotalDuration()
  const marks = []
  const interval = duration <= 60 ? 10 : duration <= 120 ? 20 : 30
  
  for (let i = 0; i <= duration; i += interval) {
    const hours = Math.floor(i / 60)
    const mins = i % 60
    const time = `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`
    const position = (i / duration) * 100
    marks.push({ time, position })
  }
  
  return marks
})

// 工具函数
const getTotalDuration = () => {
  if (!props.script || !props.script.segments) return 0
  const lastSegment = props.script.segments[props.script.segments.length - 1]
  if (!lastSegment) return 0
  
  const [hours, mins] = lastSegment.end_time.split(':').map(Number)
  return hours * 60 + mins
}

const getTotalProducts = () => {
  return (props.script.products || []).length
}

const getTotalInteractions = () => {
  return (props.script.interactions || []).length
}

const getSegmentIcon = (type) => {
  const icons = {
    'opening': '🎤',
    'product_intro': '📦',
    'interaction': '🎮',
    'promotion': '🔥',
    'break': '☕',
    'closing': '👋'
  }
  return icons[type] || '📌'
}

const getSegmentTypeLabel = (type) => {
  const map = {
    'opening': '开场',
    'product_intro': '产品介绍',
    'interaction': '互动',
    'promotion': '促销',
    'break': '休息',
    'closing': '结尾'
  }
  return map[type] || type
}

const getSegmentTypeColor = (type) => {
  const map = {
    'opening': 'success',
    'product_intro': 'primary',
    'interaction': 'warning',
    'promotion': 'danger',
    'break': 'info',
    'closing': 'success'
  }
  return map[type] || 'info'
}

const getSegmentStyle = (segment) => {
  const duration = getTotalDuration()
  if (duration === 0) return {}
  
  const [startHours, startMins] = segment.start_time.split(':').map(Number)
  const startMinutes = startHours * 60 + startMins
  
  const [endHours, endMins] = segment.end_time.split(':').map(Number)
  const endMinutes = endHours * 60 + endMins
  
  const left = (startMinutes / duration) * 100
  const width = ((endMinutes - startMinutes) / duration) * 100
  
  return {
    left: `${left}%`,
    width: `${Math.max(width, 8)}%`, // 最小宽度保证可见
    '--segment-color': getSegmentColor(segment.segment_type)
  }
}

const getSegmentColor = (type) => {
  const colors = {
    'opening': '#67C23A',
    'product_intro': '#409EFF',
    'interaction': '#E6A23C',
    'promotion': '#F56C6C',
    'break': '#909399',
    'closing': '#67C23A'
  }
  return colors[type] || '#909399'
}

const formatContent = (content) => {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

// 交互
const selectSegment = (segment) => {
  activeSegment.value = segment.segment_id
  activeSegments.value = segment.segment_id
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 0.2, 2)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 0.2, 0.6)
}

const resetZoom = () => {
  zoomLevel.value = 1
}
</script>

<style scoped>
.script-timeline {
  padding: 20px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.timeline-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.timeline-controls {
  display: flex;
  gap: 10px;
}

.timeline-overview {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 5px;
}

.overview-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.duration-badge,
.segments-count {
  color: #606266;
  font-size: 14px;
  margin-left: 10px;
}

.timeline-visual {
  position: relative;
  margin-bottom: 30px;
  padding: 20px 0;
  background: #fafafa;
  border-radius: 5px;
  overflow-x: auto;
}

.timeline-track {
  position: relative;
  height: 80px;
  margin-bottom: 30px;
}

.timeline-segment {
  position: absolute;
  height: 60px;
  background: var(--segment-color, #409EFF);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  top: 10px;
}

.timeline-segment:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.timeline-segment.active {
  outline: 3px solid #fff;
  outline-offset: 2px;
}

.segment-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 5px;
  color: white;
  font-size: 12px;
  overflow: hidden;
}

.segment-icon {
  font-size: 18px;
  margin-bottom: 3px;
}

.segment-title {
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  text-align: center;
}

.segment-time {
  font-size: 11px;
  opacity: 0.9;
  margin-top: 2px;
}

.timeline-scale {
  position: relative;
  height: 30px;
  border-top: 2px solid #e4e7ed;
}

.scale-mark {
  position: absolute;
  transform: translateX(-50%);
  font-size: 12px;
  color: #909399;
}

.scale-mark::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  width: 2px;
  height: 5px;
  background: #e4e7ed;
}

.segments-detail {
  margin-bottom: 30px;
}

.segment-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.segment-time-badge,
.segment-duration-badge {
  color: #606266;
  font-size: 13px;
  padding: 2px 8px;
  background: #f5f7fa;
  border-radius: 3px;
}

.segment-name {
  color: #303133;
  font-weight: bold;
  flex: 1;
}

.segment-detail-content {
  padding: 15px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.script-content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #606266;
  background: #fafafa;
  padding: 15px;
  border-radius: 5px;
  border-left: 3px solid #409EFF;
}

.notes-list {
  margin: 0;
  padding-left: 20px;
}

.notes-list li {
  margin: 5px 0;
  color: #F56C6C;
}

.timeline-stats {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 5px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

/* 响应式 */
@media (max-width: 768px) {
  .timeline-segment {
    min-width: 60px;
  }
  
  .segment-title {
    font-size: 10px;
  }
  
  .segment-title-row {
    flex-wrap: wrap;
  }
}
</style>
