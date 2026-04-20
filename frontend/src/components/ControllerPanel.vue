<template>
  <div class="controller-panel">
    <!-- 快速操作区 -->
    <div class="quick-actions">
      <h4 class="section-title">⚡ 快速操作</h4>
      <div class="action-grid">
        <button 
          @click="handleAction('mute_all')" 
          class="action-btn warning"
          title="全员禁言"
        >
          🔇 全员禁言
        </button>
        <button 
          @click="handleAction('unmute_all')" 
          class="action-btn success"
          title="解除禁言"
        >
          🔊 解除禁言
        </button>
        <button 
          @click="handleAction('clear_danmaku')" 
          class="action-btn danger"
          title="清空弹幕"
        >
          🗑️ 清空弹幕
        </button>
        <button 
          @click="handleAction('pin_message')" 
          class="action-btn info"
          title="置顶消息"
        >
          📌 置顶消息
        </button>
      </div>
    </div>

    <!-- 自动回复配置 -->
    <div class="config-section">
      <h4 class="section-title">🤖 自动回复配置</h4>
      <div class="config-item">
        <label class="toggle-label">
          <span>启用自动回复</span>
          <input 
            type="checkbox" 
            v-model="autoReplyEnabled"
            @change="updateAutoReplyConfig"
          />
          <span class="toggle-slider"></span>
        </label>
      </div>
      
      <div v-if="autoReplyEnabled" class="faq-editor">
        <h5>常见问题库</h5>
        <div class="faq-list">
          <div 
            v-for="(response, question, index) in faqResponses" 
            :key="index"
            class="faq-item"
          >
            <div class="faq-question">{{ question }}</div>
            <div class="faq-response">{{ response }}</div>
            <button @click="removeFaq(question)" class="btn-remove">×</button>
          </div>
        </div>
        <div class="add-faq">
          <input 
            v-model="newFaqQuestion" 
            placeholder="问题关键词（支持正则）"
            class="input-faq"
          />
          <input 
            v-model="newFaqResponse" 
            placeholder="自动回复内容"
            class="input-faq"
          />
          <button @click="addFaq" class="btn-add">添加</button>
        </div>
      </div>
    </div>

    <!-- 违规词库配置 -->
    <div class="config-section">
      <h4 class="section-title">🚫 违规词库配置</h4>
      <div class="violation-tabs">
        <button 
          v-for="(keywords, type) in violationTypes" 
          :key="type"
          :class="['tab-btn', { active: currentViolationType === type }]"
          @click="currentViolationType = type"
        >
          {{ getViolationTypeName(type) }}
        </button>
      </div>
      
      <div class="keywords-editor">
        <div class="keywords-list">
          <span 
            v-for="(keyword, index) in currentKeywords" 
            :key="index"
            class="keyword-tag"
          >
            {{ keyword }}
            <button @click="removeKeyword(keyword)" class="tag-remove">×</button>
          </span>
        </div>
        <div class="add-keyword">
          <input 
            v-model="newKeyword" 
            placeholder="输入违规词"
            class="input-keyword"
            @keyup.enter="addKeyword"
          />
          <button @click="addKeyword" class="btn-add">添加</button>
        </div>
      </div>
    </div>

    <!-- 实时监控设置 -->
    <div class="config-section">
      <h4 class="section-title">📈 监控设置</h4>
      <div class="config-grid">
        <div class="config-item">
          <label>
            <span>弹幕监控</span>
            <input 
              type="checkbox" 
              v-model="monitoring.danmaku"
              @change="updateMonitoringConfig"
            />
          </label>
        </div>
        <div class="config-item">
          <label>
            <span>情绪分析</span>
            <input 
              type="checkbox" 
              v-model="monitoring.emotion"
              @change="updateMonitoringConfig"
            />
          </label>
        </div>
        <div class="config-item">
          <label>
            <span>节奏建议</span>
            <input 
              type="checkbox" 
              v-model="monitoring.rhythm"
              @change="updateMonitoringConfig"
            />
          </label>
        </div>
        <div class="config-item">
          <label>
            <span>违规检测</span>
            <input 
              type="checkbox" 
              v-model="monitoring.violation"
              @change="updateMonitoringConfig"
            />
          </label>
        </div>
      </div>
    </div>

    <!-- 数据统计 -->
    <div class="stats-section">
      <h4 class="section-title">📊 本场统计</h4>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_danmaku }}</div>
          <div class="stat-label">弹幕总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.auto_replies }}</div>
          <div class="stat-label">自动回复</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.violations_handled }}</div>
          <div class="stat-label">违规处理</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.alerts_triggered }}</div>
          <div class="stat-label">预警触发</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ControllerPanel',
  props: {
    isLive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['action', 'config-update'],
  setup(props, { emit }) {
    // 自动回复配置
    const autoReplyEnabled = ref(true)
    const faqResponses = ref({
      '直播什么时候结束': '直播预计持续到晚上 10 点哦～',
      '有优惠吗|便宜点|打折': '当前直播间有专属优惠券，点击直播间下方链接领取！',
      '怎么购买|在哪里买': '点击直播间下方购物车图标就可以购买啦～',
    })
    const newFaqQuestion = ref('')
    const newFaqResponse = ref('')
    
    // 违规词库
    const violationTypes = ref({
      'spam': ['哈哈哈', '666', '!!!'],
      'abuse': ['傻逼', '垃圾', '废物'],
      'advertisement': ['加微信', 'QQ', '私聊'],
      'sensitive': ['政治', '敏感']
    })
    const currentViolationType = ref('spam')
    const newKeyword = ref('')
    
    // 监控设置
    const monitoring = ref({
      danmaku: true,
      emotion: true,
      rhythm: true,
      violation: true
    })
    
    // 统计
    const stats = ref({
      total_danmaku: 0,
      auto_replies: 0,
      violations_handled: 0,
      alerts_triggered: 0
    })
    
    // 计算属性
    const currentKeywords = computed(() => {
      return violationTypes.value[currentViolationType.value] || []
    })
    
    // 方法
    const handleAction = (action) => {
      if (!props.isLive) {
        alert('请先开始直播')
        return
      }
      
      const confirmMsg = {
        'mute_all': '确定要全员禁言吗？',
        'unmute_all': '确定要解除全员禁言吗？',
        'clear_danmaku': '确定要清空弹幕吗？',
        'pin_message': '请输入要置顶的消息内容'
      }
      
      if (action === 'pin_message') {
        const message = prompt(confirmMsg[action])
        if (message) {
          emit('action', { action, message })
        }
      } else if (confirm(confirmMsg[action])) {
        emit('action', { action })
      }
    }
    
    const updateAutoReplyConfig = async () => {
      try {
        await fetch('/api/controller/config/auto-reply', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            enabled: autoReplyEnabled.value,
            custom_responses: {}
          })
        })
        emit('config-update', { type: 'auto_reply', enabled: autoReplyEnabled.value })
      } catch (error) {
        console.error('更新配置失败:', error)
        autoReplyEnabled.value = !autoReplyEnabled.value
      }
    }
    
    const addFaq = () => {
      if (!newFaqQuestion.value || !newFaqResponse.value) {
        alert('请填写完整信息')
        return
      }
      
      faqResponses.value[newFaqQuestion.value] = newFaqResponse.value
      newFaqQuestion.value = ''
      newFaqResponse.value = ''
    }
    
    const removeFaq = (question) => {
      delete faqResponses.value[question]
    }
    
    const addKeyword = () => {
      if (!newKeyword.value) {
        return
      }
      
      if (!violationTypes.value[currentViolationType.value]) {
        violationTypes.value[currentViolationType.value] = []
      }
      
      violationTypes.value[currentViolationType.value].push(newKeyword.value)
      newKeyword.value = ''
    }
    
    const removeKeyword = (keyword) => {
      const index = violationTypes.value[currentViolationType.value].indexOf(keyword)
      if (index > -1) {
        violationTypes.value[currentViolationType.value].splice(index, 1)
      }
    }
    
    const updateMonitoringConfig = async () => {
      emit('config-update', { type: 'monitoring', config: monitoring.value })
    }
    
    const getViolationTypeName = (type) => {
      const map = {
        'spam': '刷屏',
        'abuse': '辱骂',
        'advertisement': '广告',
        'sensitive': '敏感内容'
      }
      return map[type] || type
    }
    
    // 生命周期
    onMounted(() => {
      // 可以在这里加载配置
    })
    
    return {
      autoReplyEnabled,
      faqResponses,
      newFaqQuestion,
      newFaqResponse,
      violationTypes,
      currentViolationType,
      currentKeywords,
      newKeyword,
      monitoring,
      stats,
      handleAction,
      updateAutoReplyConfig,
      addFaq,
      removeFaq,
      addKeyword,
      removeKeyword,
      updateMonitoringConfig,
      getViolationTypeName
    }
  }
}
</script>

<style scoped>
.controller-panel {
  background: #16213e;
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #0f3460;
  max-width: 800px;
  margin: 0 auto;
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #fff;
  border-bottom: 1px solid #0f3460;
  padding-bottom: 10px;
}

/* 快速操作 */
.quick-actions {
  margin-bottom: 25px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.action-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.action-btn.warning {
  background: linear-gradient(135deg, #ffa502, #ff7f50);
}

.action-btn.success {
  background: linear-gradient(135deg, #2ed573, #7bed9f);
}

.action-btn.danger {
  background: linear-gradient(135deg, #ff4757, #ff6b81);
}

.action-btn.info {
  background: linear-gradient(135deg, #70a1ff, #1e90ff);
}

/* 配置区域 */
.config-section {
  margin-bottom: 25px;
  padding-bottom: 25px;
  border-bottom: 1px solid #0f3460;
}

.config-section:last-child {
  border-bottom: none;
}

.config-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.config-item label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #ccc;
}

.config-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* 开关样式 */
.toggle-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.toggle-label input {
  display: none;
}

.toggle-slider {
  width: 50px;
  height: 26px;
  background: #0f3460;
  border-radius: 13px;
  position: relative;
  transition: background 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.toggle-label input:checked + .toggle-slider {
  background: #2ed573;
}

.toggle-label input:checked + .toggle-slider::before {
  transform: translateX(24px);
}

/* FAQ 编辑器 */
.faq-editor h5 {
  margin: 10px 0;
  font-size: 14px;
  color: #aaa;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 15px;
}

.faq-item {
  background: #0f3460;
  border-radius: 8px;
  padding: 12px;
  position: relative;
}

.faq-question {
  font-weight: bold;
  color: #70a1ff;
  font-size: 13px;
  margin-bottom: 5px;
}

.faq-response {
  color: #ccc;
  font-size: 13px;
}

.btn-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff4757;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.add-faq {
  display: flex;
  gap: 10px;
}

.input-faq {
  flex: 1;
  padding: 10px;
  background: #0f3460;
  border: 1px solid #1a5f9e;
  border-radius: 5px;
  color: #fff;
  font-size: 13px;
}

.input-faq:focus {
  outline: none;
  border-color: #70a1ff;
}

.btn-add {
  padding: 10px 20px;
  background: #2ed573;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.btn-add:hover {
  background: #26af61;
}

/* 违规词库 */
.violation-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.tab-btn {
  padding: 8px 16px;
  background: #0f3460;
  border: 1px solid #1a5f9e;
  border-radius: 5px;
  color: #aaa;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: #1a5f9e;
}

.tab-btn.active {
  background: #70a1ff;
  color: white;
  border-color: #70a1ff;
}

.keywords-editor {
  background: #0f3460;
  border-radius: 8px;
  padding: 15px;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
  min-height: 60px;
}

.keyword-tag {
  background: #16213e;
  color: #fff;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-remove {
  background: #ff4757;
  color: white;
  border: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-keyword {
  display: flex;
  gap: 10px;
}

.input-keyword {
  flex: 1;
  padding: 10px;
  background: #16213e;
  border: 1px solid #1a5f9e;
  border-radius: 5px;
  color: #fff;
  font-size: 13px;
}

.input-keyword:focus {
  outline: none;
  border-color: #70a1ff;
}

/* 监控设置 */
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

/* 统计 */
.stats-section {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.stat-card {
  background: #0f3460;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #70a1ff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #aaa;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #0f3460;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #1a5f9e;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #247cc4;
}
</style>
