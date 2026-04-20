<script setup lang="ts">
interface TimelineEvent {
  time: string
  type: 'highlight' | 'issue'
  title: string
  description?: string
}

interface TimelineEventsProps {
  events?: TimelineEvent[]
  title?: string
  height?: string
}

const props = withDefaults(defineProps<TimelineEventsProps>(), {
  events: () => [],
  title: '爆点/翻车时间轴',
  height: '300px'
})

// 模拟数据（用于演示）
const mockEvents: TimelineEvent[] = [
  { time: '00:05', type: 'highlight', title: '开场爆点', description: '抽奖活动吸引大量观众' },
  { time: '00:15', type: 'highlight', title: '产品亮点展示', description: '特色功能演示引发热议' },
  { time: '00:28', type: 'issue', title: '网络卡顿', description: '直播画面短暂卡顿' },
  { time: '00:35', type: 'highlight', title: '互动高潮', description: '弹幕互动达到峰值' },
  { time: '00:42', type: 'issue', title: '口误翻车', description: '主播说错产品信息' },
  { time: '00:50', type: 'highlight', title: '促销爆发', description: '限时优惠引发抢购' }
]

const events = props.events.length > 0 ? props.events : mockEvents

const getEventClass = (type: string) => {
  return type === 'highlight' ? 'event-highlight' : 'event-issue'
}

const getEventIcon = (type: string) => {
  return type === 'highlight' ? '🔥' : '⚠️'
}

const getEventColor = (type: string) => {
  return type === 'highlight' ? '#67C23A' : '#F56C6C'
}
</script>

<template>
  <div class="timeline-events" :style="{ height: props.height }">
    <div class="timeline-header">
      <h3>{{ props.title }}</h3>
    </div>
    <div class="timeline-body">
      <div class="timeline-line"></div>
      <div 
        v-for="(event, index) in events" 
        :key="index" 
        class="timeline-item"
        :class="getEventClass(event.type)"
      >
        <div class="timeline-dot" :style="{ backgroundColor: getEventColor(event.type) }">
          {{ getEventIcon(event.type) }}
        </div>
        <div class="timeline-content">
          <div class="timeline-time">{{ event.time }}</div>
          <div class="timeline-title">{{ event.title }}</div>
          <div v-if="event.description" class="timeline-desc">{{ event.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-events {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 10px;
}

.timeline-header {
  text-align: center;
  margin-bottom: 15px;
}

.timeline-header h3 {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
}

.timeline-body {
  position: relative;
  padding: 10px 0;
}

.timeline-line {
  position: absolute;
  left: 25px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #409EFF, #909399);
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  position: relative;
  z-index: 1;
}

.timeline-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-size: 20px;
  flex-shrink: 0;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.timeline-content {
  flex: 1;
  background: #fff;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid;
}

.event-highlight .timeline-content {
  border-left-color: #67C23A;
}

.event-issue .timeline-content {
  border-left-color: #F56C6C;
}

.timeline-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.timeline-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.timeline-desc {
  font-size: 12px;
  color: #606266;
}

@media (max-width: 768px) {
  .timeline-dot {
    width: 35px;
    height: 35px;
    font-size: 16px;
  }
  
  .timeline-content {
    padding: 8px 12px;
  }
  
  .timeline-title {
    font-size: 13px;
  }
}
</style>
