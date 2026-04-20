<template>
  <div class="training-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>🎓 主播培训系统</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showAssessmentModal = true">
          + 能力评估
        </button>
        <button class="btn btn-secondary" @click="showStreamModal = true">
          🎬 模拟直播
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- 选项卡导航 -->
    <div class="tab-navigation">
      <button 
        :class="['tab-btn', { active: activeTab === 'plan' }]" 
        @click="activeTab = 'plan'"
      >
        📋 培训计划
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'courses' }]" 
        @click="activeTab = 'courses'"
      >
        📚 课程库
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'growth' }]" 
        @click="activeTab = 'growth'"
      >
        📈 成长曲线
      </button>
    </div>

    <!-- 培训计划 -->
    <div v-if="activeTab === 'plan'" class="tab-content">
      <div v-if="currentPlan" class="plan-detail">
        <div class="plan-header">
          <h2>当前培训计划</h2>
          <span class="badge" :class="currentPlan.status">
            {{ statusLabel(currentPlan.status) }}
          </span>
        </div>

        <div class="plan-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: currentPlan.progress + '%' }"></div>
          </div>
          <div class="progress-text">{{ currentPlan.progress }}% 完成</div>
        </div>

        <div class="plan-info">
          <div class="info-item">
            <span class="label">开始日期:</span>
            <span class="value">{{ formatDate(currentPlan.start_date) }}</span>
          </div>
          <div class="info-item">
            <span class="label">结束日期:</span>
            <span class="value">{{ formatDate(currentPlan.end_date) }}</span>
          </div>
          <div class="info-item">
            <span class="label">周期:</span>
            <span class="value">{{ currentPlan.duration_days }} 天</span>
          </div>
        </div>

        <!-- 里程碑 -->
        <div class="milestones">
          <h3>🎯 培训里程碑</h3>
          <div class="milestone-list">
            <div 
              v-for="milestone in currentPlan.milestones" 
              :key="milestone.id"
              :class="['milestone-item', { completed: milestone.completed }]"
            >
              <div class="milestone-icon">
                <span v-if="milestone.completed">✅</span>
                <span v-else>⏳</span>
              </div>
              <div class="milestone-content">
                <div class="milestone-name">{{ milestone.name }}</div>
                <div class="milestone-date">目标：{{ formatDate(milestone.target_date) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 课程列表 -->
        <div class="plan-courses">
          <h3>📖 培训课程</h3>
          <div class="course-list">
            <div 
              v-for="course in planCourses" 
              :key="course.id"
              :class="['course-item', { completed: currentPlan.completed_courses.includes(course.id) }]"
            >
              <div class="course-info">
                <div class="course-title">{{ course.title }}</div>
                <div class="course-meta">
                  <span class="badge">{{ course.difficulty }}</span>
                  <span>{{ course.duration_minutes }}分钟</span>
                </div>
              </div>
              <button 
                v-if="!currentPlan.completed_courses.includes(course.id)"
                class="btn btn-sm btn-primary"
                @click="completeCourse(course.id)"
              >
                标记完成
              </button>
              <span v-else class="completed-badge">✅ 已完成</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>暂无活跃的培训计划</p>
        <button class="btn btn-primary" @click="createPlan">
          创建培训计划
        </button>
      </div>
    </div>

    <!-- 课程库 -->
    <div v-if="activeTab === 'courses'" class="tab-content">
      <div class="filter-toolbar">
        <div class="filter-group">
          <label>类别:</label>
          <select v-model="courseFilters.category">
            <option value="">全部</option>
            <option value="communication">沟通能力</option>
            <option value="product_knowledge">产品知识</option>
            <option value="sales_skill">销售技巧</option>
            <option value="audience_engagement">观众互动</option>
            <option value="technical_operation">技术操作</option>
            <option value="emergency_response">应急处理</option>
          </select>
        </div>

        <div class="filter-group">
          <label>难度:</label>
          <select v-model="courseFilters.difficulty">
            <option value="">全部</option>
            <option value="beginner">初级</option>
            <option value="intermediate">中级</option>
            <option value="advanced">高级</option>
            <option value="expert">专家</option>
          </select>
        </div>

        <button class="btn btn-secondary" @click="loadCourses">刷新</button>
      </div>

      <div class="course-grid">
        <div v-for="course in filteredCourses" :key="course.id" class="course-card">
          <div class="course-card-header">
            <h3>{{ course.title }}</h3>
            <span class="badge" :class="course.difficulty">{{ difficultyLabel(course.difficulty) }}</span>
          </div>
          <p class="course-description">{{ course.description }}</p>
          <div class="course-card-meta">
            <span>⏱️ {{ course.duration_minutes }}分钟</span>
            <span>📂 {{ categoryLabel(course.category) }}</span>
          </div>
          <div class="course-card-stats">
            <span>👥 {{ course.enrolled_count }}人已学</span>
            <span v-if="course.average_rating > 0">⭐ {{ course.average_rating.toFixed(1) }}分</span>
          </div>
          <button class="btn btn-primary btn-block" @click="viewCourse(course)">
            开始学习
          </button>
        </div>
      </div>
    </div>

    <!-- 成长曲线 -->
    <div v-if="activeTab === 'growth'" class="tab-content">
      <div class="growth-chart">
        <h3>📊 能力成长趋势</h3>
        <div v-if="growthRecords.length > 0" class="chart-container">
          <div class="chart-legend">
            <span class="legend-item">
              <span class="legend-dot" style="background: #4CAF50;"></span>
              评估分数
            </span>
            <span class="legend-item">
              <span class="legend-dot" style="background: #2196F3;"></span>
              完成课程
            </span>
            <span class="legend-item">
              <span class="legend-dot" style="background: #FF9800;"></span>
              模拟直播
            </span>
          </div>
          
          <div class="chart-bars">
            <div v-for="(record, index) in growthRecords" :key="index" class="bar-group">
              <div class="bars">
                <div 
                  class="bar assessment-bar" 
                  :style="{ height: (record.assessment_score / 100 * 200) + 'px' }"
                  :title="'评估分数：' + record.assessment_score"
                ></div>
                <div 
                  class="bar courses-bar" 
                  :style="{ height: (Math.min(record.completed_courses, 10) / 10 * 200) + 'px' }"
                  :title="'完成课程：' + record.completed_courses"
                ></div>
                <div 
                  class="bar streams-bar" 
                  :style="{ height: (Math.min(record.simulated_streams, 10) / 10 * 200) + 'px' }"
                  :title="'模拟直播：' + record.simulated_streams"
                ></div>
              </div>
              <div class="bar-label">{{ formatDateShort(record.date) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无成长数据</p>
        </div>
      </div>

      <div class="growth-history">
        <h3>📜 成长记录</h3>
        <div class="history-list">
          <div v-for="(record, index) in growthRecords" :key="index" class="history-item">
            <div class="history-date">{{ formatDate(record.date) }}</div>
            <div class="history-stats">
              <span class="stat">评估：{{ record.assessment_score }}分</span>
              <span class="stat">课程：{{ record.completed_courses }}门</span>
              <span class="stat">模拟：{{ record.simulated_streams }}次</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 能力评估弹窗 -->
    <div v-if="showAssessmentModal" class="modal-overlay" @click.self="showAssessmentModal = false">
      <div class="modal">
        <h2>能力评估</h2>
        <form @submit.prevent="createAssessment">
          <div class="form-group">
            <label>主播 ID *</label>
            <input v-model="newAssessment.anchor_id" type="text" required />
          </div>

          <div class="form-group">
            <label>评估人 ID *</label>
            <input v-model="newAssessment.assessor_id" type="text" required />
          </div>

          <div class="form-group">
            <label>评估项目</label>
            <div v-for="(cat, index) in assessmentCategories" :key="cat.value" class="category-score">
              <span class="category-name">{{ cat.label }}</span>
              <input 
                type="range" 
                v-model="newAssessment.scores[cat.value]" 
                min="0" 
                max="100"
                @input="updateScoreDisplay(cat.value)"
              />
              <span class="score-display">{{ newAssessment.scores[cat.value] }}分</span>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showAssessmentModal = false">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? '创建中...' : '创建评估' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 模拟直播弹窗 -->
    <div v-if="showStreamModal" class="modal-overlay" @click.self="showStreamModal = false">
      <div class="modal">
        <h2>模拟直播练习</h2>
        <form @submit.prevent="createSimulatedStream">
          <div class="form-group">
            <label>主播 ID *</label>
            <input v-model="newStream.anchor_id" type="text" required />
          </div>

          <div class="form-group">
            <label>模拟场景 *</label>
            <select v-model="newStream.scenario" required>
              <option value="">选择场景</option>
              <option value="product_introduction">产品介绍</option>
              <option value="sales_pitch">销售话术</option>
              <option value="audience_interaction">观众互动</option>
              <option value="emergency_handling">应急处理</option>
              <option value="technical_issues">技术问题</option>
            </select>
          </div>

          <div class="form-group">
            <label>时长 (分钟)</label>
            <input v-model.number="newStream.duration_minutes" type="number" min="10" max="120" value="30" />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showStreamModal = false">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? '创建中...' : '开始练习' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrainingPage',
  data() {
    return {
      activeTab: 'plan',
      stats: [],
      currentPlan: null,
      planCourses: [],
      courses: [],
      courseFilters: {
        category: '',
        difficulty: ''
      },
      growthRecords: [],
      showAssessmentModal: false,
      showStreamModal: false,
      creating: false,
      newAssessment: {
        anchor_id: '',
        assessor_id: '',
        scores: {
          communication: 50,
          product_knowledge: 50,
          sales_skill: 50,
          audience_engagement: 50,
          technical_operation: 50,
          emergency_response: 50
        }
      },
      newStream: {
        anchor_id: '',
        scenario: '',
        duration_minutes: 30
      },
      assessmentCategories: [
        { value: 'communication', label: '沟通能力' },
        { value: 'product_knowledge', label: '产品知识' },
        { value: 'sales_skill', label: '销售技巧' },
        { value: 'audience_engagement', label: '观众互动' },
        { value: 'technical_operation', label: '技术操作' },
        { value: 'emergency_response', label: '应急处理' }
      ]
    }
  },
  computed: {
    filteredCourses() {
      return this.courses.filter(course => {
        if (this.courseFilters.category && course.category !== this.courseFilters.category) {
          return false
        }
        if (this.courseFilters.difficulty && course.difficulty !== this.courseFilters.difficulty) {
          return false
        }
        return true
      })
    }
  },
  mounted() {
    this.loadStatistics()
    this.loadActivePlan()
    this.loadCourses()
    this.loadGrowthCurve()
  },
  methods: {
    async loadStatistics() {
      try {
        const response = await fetch('/api/training/statistics')
        const data = await response.json()
        this.stats = [
          { label: '总评估数', value: data.total_assessments },
          { label: '培训计划', value: data.total_plans },
          { label: '完成计划', value: data.completed_plans },
          { label: '模拟直播', value: data.completed_streams },
          { label: '平均分数', value: data.average_stream_score },
          { label: '课程总数', value: data.total_courses }
        ]
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },
    async loadActivePlan() {
      try {
        const response = await fetch('/api/training/anchors/anchor001/plan')
        const data = await response.json()
        if (data) {
          this.currentPlan = data
          await this.loadPlanCourses()
        }
      } catch (error) {
        console.error('加载培训计划失败:', error)
      }
    },
    async loadPlanCourses() {
      if (!this.currentPlan || !this.currentPlan.courses) return
      
      try {
        const coursePromises = this.currentPlan.courses.map(id => 
          fetch(`/api/training/courses/${id}`).then(r => r.json())
        )
        this.planCourses = await Promise.all(coursePromises)
      } catch (error) {
        console.error('加载课程失败:', error)
      }
    },
    async loadCourses() {
      try {
        let url = '/api/training/courses'
        const params = new URLSearchParams()
        if (this.courseFilters.category) params.append('category', this.courseFilters.category)
        if (this.courseFilters.difficulty) params.append('difficulty', this.courseFilters.difficulty)
        
        if (params.toString()) {
          url += '?' + params.toString()
        }
        
        const response = await fetch(url)
        this.courses = await response.json()
      } catch (error) {
        console.error('加载课程失败:', error)
      }
    },
    async loadGrowthCurve() {
      try {
        const response = await fetch('/api/training/anchors/anchor001/growth')
        const data = await response.json()
        this.growthRecords = data.records || []
      } catch (error) {
        console.error('加载成长曲线失败:', error)
      }
    },
    async createAssessment() {
      this.creating = true
      try {
        const categories = this.assessmentCategories.map(cat => ({
          category: cat.value,
          score: this.newAssessment.scores[cat.value]
        }))
        
        const response = await fetch('/api/training/assessments', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            anchor_id: this.newAssessment.anchor_id,
            assessor_id: this.newAssessment.assessor_id,
            categories
          })
        })
        
        if (response.ok) {
          alert('评估创建成功！')
          this.showAssessmentModal = false
          this.loadActivePlan()
        }
      } catch (error) {
        console.error('创建评估失败:', error)
        alert('创建评估失败')
      } finally {
        this.creating = false
      }
    },
    async createPlan() {
      try {
        const response = await fetch('/api/training/plans', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            anchor_id: 'anchor001',
            assessment_id: 'latest',
            duration_days: 30
          })
        })
        
        if (response.ok) {
          this.loadActivePlan()
        }
      } catch (error) {
        console.error('创建计划失败:', error)
      }
    },
    async completeCourse(courseId) {
      try {
        const response = await fetch(`/api/training/plans/${this.currentPlan.id}/complete-course`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            plan_id: this.currentPlan.id,
            course_id: courseId
          })
        })
        
        if (response.ok) {
          this.loadActivePlan()
        }
      } catch (error) {
        console.error('标记课程完成失败:', error)
      }
    },
    async createSimulatedStream() {
      this.creating = true
      try {
        const response = await fetch('/api/training/simulated-streams', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newStream)
        })
        
        if (response.ok) {
          const stream = await response.json()
          alert(`模拟直播创建成功！ID: ${stream.id}`)
          this.showStreamModal = false
        }
      } catch (error) {
        console.error('创建模拟直播失败:', error)
        alert('创建失败')
      } finally {
        this.creating = false
      }
    },
    viewCourse(course) {
      window.open(course.content_url, '_blank')
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
      return date.toLocaleDateString('zh-CN')
    },
    formatDateShort(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getMonth() + 1}/${date.getDate()}`
    },
    updateScoreDisplay(category) {
      // 用于实时更新分数显示
    }
  }
}
</script>

<style scoped>
.training-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #4CAF50;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.tab-navigation {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: #4CAF50;
}

.tab-btn.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
}

.tab-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.plan-progress {
  margin-bottom: 20px;
}

.progress-bar {
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  font-weight: bold;
  color: #4CAF50;
}

.plan-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item .label {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.info-item .value {
  font-weight: bold;
  color: #333;
}

.milestones {
  margin: 20px 0;
}

.milestone-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.milestone-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
  opacity: 0.6;
}

.milestone-item.completed {
  opacity: 1;
  background: #E8F5E9;
}

.milestone-icon {
  font-size: 24px;
}

.milestone-content {
  flex: 1;
}

.milestone-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.milestone-date {
  color: #666;
  font-size: 14px;
}

.plan-courses {
  margin-top: 20px;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.course-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.course-item.completed {
  background: #E8F5E9;
  border-color: #4CAF50;
}

.course-info {
  flex: 1;
}

.course-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.course-meta {
  display: flex;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.completed-badge {
  color: #4CAF50;
  font-weight: bold;
}

.filter-toolbar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: bold;
  color: #666;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.course-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.course-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.course-card-header h3 {
  margin: 0;
  font-size: 18px;
  flex: 1;
}

.course-description {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.5;
}

.course-card-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.course-card-stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.btn-block {
  width: 100%;
}

.growth-chart {
  margin-bottom: 30px;
}

.chart-container {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.chart-legend {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.chart-bars {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  height: 250px;
  padding: 20px 10px;
  background: white;
  border-radius: 8px;
  overflow-x: auto;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.bars {
  display: flex;
  gap: 4px;
  align-items: flex-end;
  height: 200px;
}

.bar {
  width: 12px;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.assessment-bar {
  background: #4CAF50;
}

.courses-bar {
  background: #2196F3;
}

.streams-bar {
  background: #FF9800;
}

.bar-label {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
  transform: rotate(-45deg);
  transform-origin: top center;
}

.growth-history {
  margin-top: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.history-date {
  font-weight: bold;
  color: #333;
}

.history-stats {
  display: flex;
  gap: 20px;
}

.history-stats .stat {
  padding: 5px 10px;
  background: white;
  border-radius: 4px;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.category-score {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.category-name {
  width: 120px;
  font-size: 14px;
}

.category-score input[type="range"] {
  flex: 1;
}

.score-display {
  width: 50px;
  text-align: right;
  font-weight: bold;
  color: #4CAF50;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.badge.beginner {
  background: #E3F2FD;
  color: #1976D2;
}

.badge.intermediate {
  background: #FFF3E0;
  color: #F57C00;
}

.badge.advanced {
  background: #F3E5F5;
  color: #7B1FA2;
}

.badge.expert {
  background: #FFEBEE;
  color: #C62828;
}

.badge.not_started {
  background: #ECEFF1;
  color: #546E7A;
}

.badge.in_progress {
  background: #E3F2FD;
  color: #1976D2;
}

.badge.completed {
  background: #E8F5E9;
  color: #388E3C;
}

.badge.failed {
  background: #FFEBEE;
  color: #C62828;
}
</style>
