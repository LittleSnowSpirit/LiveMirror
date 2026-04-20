<template>
  <div class="playback-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📺 直播回放</h1>
      <div class="header-actions">
        <button @click="showUploadModal = true" class="btn btn-primary">
          📤 上传录像
        </button>
        <button @click="refreshData" class="btn btn-secondary">
          🔄 刷新
        </button>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_recordings }}</div>
        <div class="stat-label">总录像数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_duration_hours }}h</div>
        <div class="stat-label">总时长</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_views }}</div>
        <div class="stat-label">总观看次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_clips }}</div>
        <div class="stat-label">片段数</div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索标题、描述..."
          @input="debouncedSearch"
          class="search-input"
        />
        <span class="search-icon">🔍</span>
      </div>
      
      <div class="filter-controls">
        <select v-model="filterStreamer" @change="applyFilters" class="filter-select">
          <option value="">所有主播</option>
          <option v-for="streamer in uniqueStreamers" :key="streamer" :value="streamer">
            {{ streamer }}
          </option>
        </select>
        
        <select v-model="filterCategory" @change="applyFilters" class="filter-select">
          <option value="">所有分类</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        
        <div class="tag-filters">
          <button
            v-for="tag in visibleTags"
            :key="tag"
            @click="toggleTag(tag)"
            :class="['tag-btn', { active: selectedTags.includes(tag) }]"
          >
            {{ tag }}
          </button>
          <button v-if="tags.length > visibleTags.length" @click="showAllTags = !showAllTags" class="tag-btn more-tags">
            {{ showAllTags ? '收起' : `+${tags.length - visibleTags.length}` }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 录像列表 -->
    <div class="recordings-grid">
      <div
        v-for="recording in filteredRecordings"
        :key="recording.id"
        class="recording-card"
        @click="selectRecording(recording)"
      >
        <div class="recording-thumbnail">
          <img
            v-if="recording.thumbnail_path"
            :src="recording.thumbnail_path"
            :alt="recording.title"
            class="thumbnail-img"
          />
          <div v-else class="thumbnail-placeholder">
            <span>📹</span>
          </div>
          <div class="duration-badge">{{ formatDuration(recording.duration) }}</div>
          <button
            @click.stop="deleteRecording(recording.id)"
            class="delete-btn"
            title="删除"
          >
            🗑️
          </button>
        </div>
        <div class="recording-info">
          <h3 class="recording-title">{{ recording.title }}</h3>
          <div class="recording-meta">
            <span class="streamer-name">👤 {{ recording.streamer }}</span>
            <span class="view-count">👁 {{ recording.view_count }}</span>
          </div>
          <div class="recording-tags">
            <span
              v-for="tag in recording.tags.slice(0, 3)"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
          <div class="recording-date">
            {{ formatDate(recording.created_at) }}
          </div>
        </div>
      </div>
      
      <div v-if="filteredRecordings.length === 0" class="empty-state">
        <div class="empty-icon">📼</div>
        <div class="empty-text">暂无录像</div>
        <button @click="showUploadModal = true" class="btn btn-primary">
          上传第一个录像
        </button>
      </div>
    </div>
    
    <!-- 播放详情模态框 -->
    <div v-if="selectedRecording" class="modal-overlay" @click.self="closePlayer">
      <div class="player-modal">
        <div class="modal-header">
          <h2>{{ selectedRecording.title }}</h2>
          <button @click="closePlayer" class="close-btn">✕</button>
        </div>
        
        <div class="modal-content">
          <!-- 视频播放器 -->
          <VideoPlayer
            ref="playerRef"
            :video-src="getVideoUrl(selectedRecording.id)"
            :poster="selectedRecording.thumbnail_path || ''"
            :show-clip-tools="true"
            @clip-create="onClipCreate"
          />
          
          <!-- 录像信息 -->
          <div class="recording-details">
            <div class="detail-section">
              <h3>描述</h3>
              <p>{{ selectedRecording.description || '暂无描述' }}</p>
            </div>
            
            <div class="detail-section">
              <h3>分类</h3>
              <div class="tags-row">
                <span
                  v-for="cat in selectedRecording.categories"
                  :key="cat"
                  class="tag tag-category"
                >
                  {{ cat }}
                </span>
              </div>
            </div>
            
            <div class="detail-section">
              <h3>标签</h3>
              <div class="tags-row">
                <span
                  v-for="tag in selectedRecording.tags"
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            
            <div class="detail-section">
              <h3>统计</h3>
              <div class="stats-row">
                <span>👁 {{ selectedRecording.view_count }} 次观看</span>
                <span>⏱ {{ formatDuration(selectedRecording.duration) }}</span>
                <span>📅 {{ formatDate(selectedRecording.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button @click="shareRecording" class="btn btn-secondary">
              🔗 分享
            </button>
            <button @click="editRecording" class="btn btn-secondary">
              ✏️ 编辑
            </button>
            <button @click="downloadRecording" class="btn btn-secondary">
              ⬇️ 下载
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 上传模态框 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="upload-modal">
        <div class="modal-header">
          <h2>上传录像</h2>
          <button @click="showUploadModal = false" class="close-btn">✕</button>
        </div>
        
        <div class="modal-content">
          <form @submit.prevent="handleUpload" class="upload-form">
            <div class="form-group">
              <label>视频文件 *</label>
              <input
                type="file"
                ref="fileInput"
                accept="video/*"
                @change="onFileSelect"
                required
                class="file-input"
              />
              <div v-if="uploadFile" class="file-info">
                ✓ {{ uploadFile.name }} ({{ formatFileSize(uploadFile.size) }})
              </div>
            </div>
            
            <div class="form-group">
              <label>标题 *</label>
              <input
                v-model="uploadForm.title"
                type="text"
                required
                placeholder="输入录像标题"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label>主播 *</label>
              <input
                v-model="uploadForm.streamer"
                type="text"
                required
                placeholder="输入主播名称"
                class="form-input"
              />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>时长 (秒) *</label>
                <input
                  v-model.number="uploadForm.duration"
                  type="number"
                  required
                  min="1"
                  placeholder="例如：3600"
                  class="form-input"
                />
              </div>
              
              <div class="form-group">
                <label>缩略图</label>
                <input
                  type="file"
                  @change="onThumbnailSelect"
                  accept="image/*"
                  class="file-input"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label>分类</label>
              <div class="tag-input-container">
                <input
                  v-model="newCategory"
                  type="text"
                  placeholder="输入分类后按回车"
                  @keyup.enter="addCategory"
                  class="form-input"
                />
                <div class="selected-tags">
                  <span
                    v-for="cat in uploadForm.categories"
                    :key="cat"
                    class="tag tag-removable"
                  >
                    {{ cat }}
                    <button @click="removeCategory(cat)" type="button">✕</button>
                  </span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label>标签</label>
              <div class="tag-input-container">
                <input
                  v-model="newTag"
                  type="text"
                  placeholder="输入标签后按回车"
                  @keyup.enter="addTag"
                  class="form-input"
                />
                <div class="selected-tags">
                  <span
                    v-for="tag in uploadForm.tags"
                    :key="tag"
                    class="tag tag-removable"
                  >
                    {{ tag }}
                    <button @click="removeTag(tag)" type="button">✕</button>
                  </span>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label>描述</label>
              <textarea
                v-model="uploadForm.description"
                placeholder="输入录像描述（可选）"
                rows="3"
                class="form-input form-textarea"
              ></textarea>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="showUploadModal = false" class="btn btn-secondary">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="isUploading">
                {{ isUploading ? '上传中...' : '上传' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 分享模态框 -->
    <div v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
      <div class="share-modal">
        <div class="modal-header">
          <h2>分享录像</h2>
          <button @click="showShareModal = false" class="close-btn">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="share-info">
            <p>分享链接将在 {{ shareExpireHours }} 小时后过期</p>
          </div>
          
          <div v-if="shareLink" class="share-link-box">
            <input
              type="text"
              :value="shareLink"
              readonly
              class="share-link-input"
            />
            <button @click="copyShareLink" class="btn btn-secondary">
              {{ copied ? '✓ 已复制' : '📋 复制' }}
            </button>
          </div>
          
          <div class="share-actions">
            <button @click="generateShareLink" class="btn btn-primary" :disabled="isGeneratingShare">
              {{ isGeneratingShare ? '生成中...' : '生成分享链接' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VideoPlayer from '../components/VideoPlayer.vue'

// API 基础 URL（根据实际部署配置）
const API_BASE = '/api'

// 状态
const stats = ref({
  total_recordings: 0,
  total_duration_hours: 0,
  total_views: 0,
  total_clips: 0
})

const recordings = ref([])
const categories = ref([])
const tags = ref([])
const searchQuery = ref('')
const filterStreamer = ref('')
const filterCategory = ref('')
const selectedTags = ref([])
const showAllTags = ref(false)

const selectedRecording = ref(null)
const showUploadModal = ref(false)
const showShareModal = ref(false)

const uploadFile = ref(null)
const thumbnailFile = ref(null)
const isUploading = ref(false)
const isGeneratingShare = ref(false)

const uploadForm = ref({
  title: '',
  streamer: '',
  duration: 0,
  categories: [],
  tags: [],
  description: ''
})

const newCategory = ref('')
const newTag = ref('')

const shareLink = ref('')
const shareExpireHours = ref(24)
const copied = ref(false)

// 计算属性
const uniqueStreamers = computed(() => {
  const streamers = new Set(recordings.value.map(r => r.streamer))
  return Array.from(streamers).sort()
})

const visibleTags = computed(() => {
  if (showAllTags.value) return tags.value
  return tags.value.slice(0, 10)
})

const filteredRecordings = computed(() => {
  let result = recordings.value
  
  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(r =>
      r.title.toLowerCase().includes(query) ||
      r.description.toLowerCase().includes(query)
    )
  }
  
  // 主播筛选
  if (filterStreamer.value) {
    result = result.filter(r => r.streamer === filterStreamer.value)
  }
  
  // 分类筛选
  if (filterCategory.value) {
    result = result.filter(r => r.categories.includes(filterCategory.value))
  }
  
  // 标签筛选
  if (selectedTags.value.length > 0) {
    result = result.filter(r =>
      selectedTags.value.some(tag => r.tags.includes(tag))
    )
  }
  
  return result
})

// 生命周期
onMounted(() => {
  loadStatistics()
  loadRecordings()
  loadCategories()
  loadTags()
})

// 方法
const loadStatistics = async () => {
  try {
    const res = await fetch(`${API_BASE}/playback/statistics`)
    const data = await res.json()
    if (data.success) {
      stats.value = data.data
    }
  } catch (err) {
    console.error('加载统计失败:', err)
  }
}

const loadRecordings = async () => {
  try {
    const res = await fetch(`${API_BASE}/playback/recordings?limit=100`)
    const data = await res.json()
    if (data.success) {
      recordings.value = data.data
    }
  } catch (err) {
    console.error('加载录像失败:', err)
  }
}

const loadCategories = async () => {
  try {
    const res = await fetch(`${API_BASE}/playback/categories`)
    const data = await res.json()
    if (data.success) {
      categories.value = data.data
    }
  } catch (err) {
    console.error('加载分类失败:', err)
  }
}

const loadTags = async () => {
  try {
    const res = await fetch(`${API_BASE}/playback/tags`)
    const data = await res.json()
    if (data.success) {
      tags.value = data.data
    }
  } catch (err) {
    console.error('加载标签失败:', err)
  }
}

const refreshData = () => {
  loadStatistics()
  loadRecordings()
  loadCategories()
  loadTags()
}

// 搜索和筛选
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // 可以在这里调用 API 进行搜索
    console.log('搜索:', searchQuery.value)
  }, 300)
}

const applyFilters = () => {
  console.log('应用筛选:', {
    streamer: filterStreamer.value,
    category: filterCategory.value,
    tags: selectedTags.value
  })
}

const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tag)
  }
  applyFilters()
}

// 录像操作
const selectRecording = (recording) => {
  selectedRecording.value = recording
}

const closePlayer = () => {
  selectedRecording.value = null
  shareLink.value = ''
  copied.value = false
}

const deleteRecording = async (id) => {
  if (!confirm('确定要删除这个录像吗？此操作不可恢复。')) {
    return
  }
  
  try {
    const res = await fetch(`${API_BASE}/playback/recordings/${id}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      recordings.value = recordings.value.filter(r => r.id !== id)
      loadStatistics()
    } else {
      alert('删除失败：' + (data.message || '未知错误'))
    }
  } catch (err) {
    console.error('删除失败:', err)
    alert('删除失败，请检查网络连接')
  }
}

const getVideoUrl = (recordingId) => {
  return `${API_BASE}/playback/recordings/${recordingId}/stream`
}

// 上传操作
const onFileSelect = (event) => {
  uploadFile.value = event.target.files[0]
}

const onThumbnailSelect = (event) => {
  thumbnailFile.value = event.target.files[0]
}

const addCategory = () => {
  const cat = newCategory.value.trim()
  if (cat && !uploadForm.value.categories.includes(cat)) {
    uploadForm.value.categories.push(cat)
    newCategory.value = ''
  }
}

const removeCategory = (cat) => {
  uploadForm.value.categories = uploadForm.value.categories.filter(c => c !== cat)
}

const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !uploadForm.value.tags.includes(tag)) {
    uploadForm.value.tags.push(tag)
    newTag.value = ''
  }
}

const removeTag = (tag) => {
  uploadForm.value.tags = uploadForm.value.tags.filter(t => t !== tag)
}

const handleUpload = async () => {
  if (!uploadFile.value) {
    alert('请选择视频文件')
    return
  }
  
  isUploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    formData.append('title', uploadForm.value.title)
    formData.append('streamer', uploadForm.value.streamer)
    formData.append('duration', uploadForm.value.duration.toString())
    formData.append('categories', uploadForm.value.categories.join(','))
    formData.append('tags', uploadForm.value.tags.join(','))
    formData.append('description', uploadForm.value.description)
    
    if (thumbnailFile.value) {
      formData.append('thumbnail', thumbnailFile.value)
    }
    
    const res = await fetch(`${API_BASE}/playback/recordings`, {
      method: 'POST',
      body: formData
    })
    
    const data = await res.json()
    if (data.success) {
      alert('上传成功！')
      showUploadModal.value = false
      resetUploadForm()
      refreshData()
    } else {
      alert('上传失败：' + (data.message || '未知错误'))
    }
  } catch (err) {
    console.error('上传失败:', err)
    alert('上传失败，请检查网络连接')
  } finally {
    isUploading.value = false
  }
}

const resetUploadForm = () => {
  uploadForm.value = {
    title: '',
    streamer: '',
    duration: 0,
    categories: [],
    tags: [],
    description: ''
  }
  uploadFile.value = null
  thumbnailFile.value = null
  newCategory.value = ''
  newTag.value = ''
}

// 片段剪辑
const onClipCreate = async ({ startTime, endTime, duration }) => {
  if (!selectedRecording.value) return
  
  const title = prompt('输入片段标题:', `片段 - ${formatTime(startTime)} ~ ${formatTime(endTime)}`)
  if (!title) return
  
  const description = prompt('输入片段描述（可选）:') || ''
  
  try {
    const res = await fetch(`${API_BASE}/playback/clips`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recording_id: selectedRecording.value.id,
        start_time: startTime,
        end_time: endTime,
        title: title,
        description: description
      })
    })
    
    const data = await res.json()
    if (data.success) {
      alert('片段创建成功！')
      console.log('片段:', data.data)
    } else {
      alert('创建失败：' + (data.message || '未知错误'))
    }
  } catch (err) {
    console.error('创建片段失败:', err)
    alert('创建失败，请检查网络连接')
  }
}

// 分享功能
const shareRecording = () => {
  showShareModal.value = true
  shareLink.value = ''
  copied.value = false
}

const generateShareLink = async () => {
  if (!selectedRecording.value) return
  
  isGeneratingShare.value = true
  
  try {
    const res = await fetch(`${API_BASE}/playback/share`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recording_id: selectedRecording.value.id,
        expire_hours: shareExpireHours.value
      })
    })
    
    const data = await res.json()
    if (data.success) {
      // 构建完整 URL
      const baseUrl = window.location.origin
      shareLink.value = `${baseUrl}${data.data.share_url}`
    } else {
      alert('生成失败：' + (data.message || '未知错误'))
    }
  } catch (err) {
    console.error('生成分享链接失败:', err)
    alert('生成失败，请检查网络连接')
  } finally {
    isGeneratingShare.value = false
  }
}

const copyShareLink = () => {
  navigator.clipboard.writeText(shareLink.value)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

const editRecording = () => {
  alert('编辑功能开发中...')
}

const downloadRecording = () => {
  if (!selectedRecording.value) return
  
  const link = document.createElement('a')
  link.href = getVideoUrl(selectedRecording.value.id)
  link.download = `${selectedRecording.value.title}.mp4`
  link.click()
}

// 工具函数
const formatDuration = (seconds) => {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (isoString) => {
  const date = new Date(isoString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}
</script>

<style scoped>
.playback-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 按钮 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #4CAF50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 搜索筛选 */
.search-filter-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.search-box {
  position: relative;
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
}

.filter-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.tag-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-btn {
  padding: 6px 12px;
  background: #f0f0f0;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-btn:hover {
  background: #e0e0e0;
}

.tag-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.tag-btn.more-tags {
  background: transparent;
  border: none;
  color: #666;
}

/* 录像网格 */
.recordings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.recording-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.recording-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.recording-thumbnail {
  position: relative;
  aspect-ratio: 16/9;
  background: #000;
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.recording-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(255, 0, 0, 0.8);
}

.recording-info {
  padding: 12px;
}

.recording-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recording-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.recording-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.tag {
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 12px;
  font-size: 11px;
  color: #666;
}

.tag-category {
  background: #e3f2fd;
  color: #1976d2;
}

.recording-date {
  font-size: 12px;
  color: #999;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: #666;
  margin-bottom: 24px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.player-modal,
.upload-modal,
.share-modal {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.upload-modal {
  max-width: 600px;
}

.share-modal {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1a1a1a;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f0f0f0;
}

.modal-content {
  padding: 24px;
}

/* 录像详情 */
.recording-details {
  margin-top: 20px;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section h3 {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin: 0 0 8px 0;
}

.detail-section p {
  font-size: 14px;
  color: #333;
  margin: 0;
  line-height: 1.6;
}

.tags-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stats-row {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

/* 上传表单 */
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.file-input {
  padding: 8px 0;
}

.file-info {
  font-size: 13px;
  color: #4CAF50;
}

.tag-input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selected-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-removable {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 12px;
}

.tag-removable button {
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  line-height: 1;
}

.tag-removable button:hover {
  color: #d32f2f;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

/* 分享 */
.share-info {
  margin-bottom: 16px;
  color: #666;
  font-size: 14px;
}

.share-link-box {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.share-link-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: #f5f5f5;
  color: #333;
}

.share-actions {
  display: flex;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .recordings-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
