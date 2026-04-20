<template>
  <div class="training-plan-component">
    <!-- 计划概览卡片 -->
    <div v-if="plan" class="plan-card">
      <div class="plan-card-header">
        <div class="plan-title">
          <h3>📋 培训计划</h3>
          <span class="status-badge" :class="plan.status">
            {{ statusLabel(plan.status) }}
          </span>
        </div>
        <div class="plan-progress-summary">
          <span class="progress-percentage">{{ plan.progress }}%</span>
          <span class="progress-label">完成度</span>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="progress-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: plan.progress + '%' }"
            :class="{ 'progress-complete': plan.progress === 100 }"
          ></div>
        </div>
        <div class="progress-details">
          <span>{{ plan.completed_courses.length }} / {{ plan.courses.length }} 课程</span>
          <span>📅 {{ getRemainingDays }} 天</span>
        </div>
      </div>

      <!-- 时间信息 -->
      <div class="plan-timeline">
        <div class="timeline-item">
          <span class="timeline-icon">🚀</span>
          <div class="timeline-content">
            <div class="timeline-label">开始日期</div>
            <div class="timeline-value">{{ formatDate(plan.start_date) }}</div>
          </div>
        </div>
        <div class="timeline-item">
          <span class="timeline-icon">🎯</span>
          <div class="timeline-content">
            <div class="timeline-label">目标完成</div>
            <div class="timeline-value">{{ formatDate(plan.end_date) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 里程碑列表 -->
    <div v-if="plan && plan.milestones" class="milestones-section">
      <h4>🎯 培训里程碑</h4>
      <div class="milestone-timeline">
        <div 
          v-for="(milestone, index) in plan.milestones" 
          :key="milestone.id"
          class="milestone-node"
          :class="{ 
            'completed': milestone.completed,
            'current': isCurrentMilestone(index)
          }"
        >
          <div class="milestone-connector" v-if="index < plan.milestones.length - 1"></div>
          <div class="milestone-marker">
            <span v-if="milestone.completed">✓</span>
            <span v-else-if="isCurrentMilestone(index)">●</span>
            <span v-else>○</span>
          </div>
          <div class="milestone-info">
            <div class="milestone-title">{{ milestone.name }}</div>
            <div class="milestone-date">{{ formatDate(milestone.target_date) }}</div>
            <div v-if="milestone.completed" class="milestone-status completed">
              已完成
            </div>
            <div v-else-if="isCurrentMilestone(index)" class="milestone-status current">
              进行中
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 课程列表 -->
    <div v-if="plan && courses.length > 0" class="courses-section">
      <h4>📚 培训课程</h4>
      <div class="course-list">
        <div 
          v-for="(course, index) in courses" 
          :key="course.id"
          class="course-row"
          :class="{ 
            'completed': isCourseCompleted(course.id),
            'locked': isCourseLocked(index)
          }"
        >
          <div class="course-number">{{ index + 1 }}</div>
          <div class="course-content">
            <div class="course-header">
              <h5>{{ course.title }}</h5>
              <span class="difficulty-badge" :class="course.difficulty">
                {{ difficultyLabel(course.difficulty) }}
              </span>
            </div>
            <p class="course-description">{{ course.description }}</p>
            <div class="course-meta">
              <span class="meta-item">⏱️ {{ course.duration_minutes }}分钟</span>
              <span class="meta-item">📂 {{ categoryLabel(course.category) }}</span>
            </div>
          </div>
          <div class="course-action">
            <button 
              v-if="!isCourseCompleted(course.id) && !isCourseLocked(index)"
              class="btn-complete"
              @click="$emit('complete-course', course.id)"
            >
              完成
            </button>
            <span v-else-if="isCourseCompleted(course.id)" class="check-mark">
              ✓ 已完成
            </span>
            <span v-else class="lock-icon">
              🔒
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!plan" class="empty-plan">
      <div class="empty-icon">📋</div>
      <h3>暂无培训计划</h3>
      <p>完成能力评估后，系统将为您生成个性化培训计划</p>
      <button class="btn-create-plan" @click="$emit('create-plan')">
        创建计划
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingPlanComponent',
  props: {
    plan: {
      type: Object,
      default: null
    },
    courses: {
      type: Array,
      default: () => []
    }
  },
  emits: ['complete-course', 'create-plan'],
  computed: {
    getRemainingDays() {
      if (!this.plan) return 0
      const endDate = new Date(this.plan.end_date)
      const now = new Date()
      const diff = endDate - now
      return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
    }
  },
  methods: {
    isCourseCompleted(courseId) {
      return this.plan && this.plan.completed_courses.includes(courseId)
    },
    isCourseLocked(index) {
      if (!this.plan) return true
      // 简化逻辑：按顺序解锁，前一个完成后才能进行下一个
      if (index === 0) return false
      const prevCourseId = this.plan.courses[index - 1]
      return !this.plan.completed_courses.includes(prevCourseId)
    },
    isCurrentMilestone(index) {
      if (!this.plan) return false
      // 第一个未完成的里程碑是当前里程碑
      for (let i = 0; i < this.plan.milestones.length; i++) {
        if (!this.plan.milestones[i].completed) {
          return i === index
        }
      }
      return false
    },
    statusLabel(status) {
      const labels = {
        'not_started': '未开始',
        'in_progress': '进行中',
        'completed': '已完成',
        'failed': '失败'
      }
      return labels[status] || status
    },
    difficultyLabel(difficulty) {
      const labels = {
        'beginner': '初级',
        'intermediate': '中级',
        'advanced': '高级',
        'expert': '专家'
      }
      return labels[difficulty] || difficulty
    },
    categoryLabel(category) {
      const labels = {
        'communication': '沟通能力',
        'product_knowledge': '产品知识',
        'sales_skill': '销售技巧',
        'audience_engagement': '观众互动',
        'technical_operation': '技术操作',
        'emergency_response': '应急处理'
      }
      return labels[category] || category
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', { 
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.training-plan-component {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

/* 计划卡片 */
.plan-card {
  padding: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.plan-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plan-title h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.not_started {
  background: #f5f5f5;
  color: #666;
}

.status-badge.in_progress {
  background: #e6f7ff;
  color: #1890ff;
}

.status-badge.completed {
  background: #f6ffed;
  color: #52c41a;
}

.status-badge.failed {
  background: #fff1f0;
  color: #ff4d4f;
}

.progress-summary {
  text-align: right;
}

.progress-percentage {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #52c41a;
}

.progress-label {
  font-size: 12px;
  color: #666;
}

.progress-container {
  margin-bottom: 20px;
}

.progress-bar {
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1890ff, #52c41a);
  border-radius: 6px;
  transition: width 0.5s ease;
}

.progress-fill.progress-complete {
  background: #52c41a;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

.plan-timeline {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-icon {
  font-size: 24px;
}

.timeline-content {
  display: flex;
  flex-direction: column;
}

.timeline-label {
  font-size: 12px;
  color: #999;
}

.timeline-value {
  font-weight: bold;
  color: #333;
}

/* 里程碑部分 */
.milestones-section {
  padding: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.milestones-section h4 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
}

.milestone-timeline {
  position: relative;
  padding-left: 20px;
}

.milestone-node {
  position: relative;
  display: flex;
  gap: 16px;
  padding-bottom: 24px;
}

.milestone-connector {
  position: absolute;
  left: 14px;
  top: 32px;
  width: 2px;
  height: calc(100% - 32px);
  background: #e8e8e8;
}

.milestone-node:last-child .milestone-connector {
  display: none;
}

.milestone-marker {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 1;
  flex-shrink: 0;
}

.milestone-node.completed .milestone-marker {
  background: #52c41a;
  border-color: #52c41a;
  color: white;
}

.milestone-node.current .milestone-marker {
  background: #1890ff;
  border-color: #1890ff;
  color: white;
}

.milestone-info {
  flex: 1;
}

.milestone-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.milestone-date {
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
}

.milestone-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.milestone-status.completed {
  background: #f6ffed;
  color: #52c41a;
}

.milestone-status.current {
  background: #e6f7ff;
  color: #1890ff;
}

/* 课程部分 */
.courses-section {
  padding: 24px;
}

.courses-section h4 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  transition: all 0.3s;
}

.course-row:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24,144,255,0.1);
}

.course-row.completed {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.course-row.locked {
  opacity: 0.6;
  background: #fafafa;
}

.course-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #1890ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.course-row.completed .course-number {
  background: #52c41a;
}

.course-row.locked .course-number {
  background: #d9d9d9;
}

.course-content {
  flex: 1;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.course-header h5 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.difficulty-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.difficulty-badge.beginner {
  background: #e6f7ff;
  color: #1890ff;
}

.difficulty-badge.intermediate {
  background: #fff7e6;
  color: #fa8c16;
}

.difficulty-badge.advanced {
  background: #f9f0ff;
  color: #722ed1;
}

.difficulty-badge.expert {
  background: #fff1f0;
  color: #ff4d4f;
}

.course-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.course-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.course-action {
  display: flex;
  align-items: center;
}

.btn-complete {
  padding: 8px 20px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-complete:hover {
  background: #40a9ff;
}

.check-mark {
  color: #52c41a;
  font-weight: bold;
}

.lock-icon {
  font-size: 18px;
}

/* 空状态 */
.empty-plan {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-plan h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: #333;
}

.empty-plan p {
  margin: 0 0 24px 0;
  color: #999;
  font-size: 14px;
}

.btn-create-plan {
  padding: 12px 32px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.btn-create-plan:hover {
  background: #40a9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24,144,255,0.3);
}
</style>
