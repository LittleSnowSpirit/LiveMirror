<template>
  <div class="decorator-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>🎨 直播间装修</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showCreateModal = true">
          + 新建方案
        </button>
        <button class="btn btn-secondary" @click="showPresets = true">
          📋 装修模板
        </button>
        <button class="btn btn-secondary" @click="showStickerLibrary = true">
          🎭 贴纸库
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_schemes }}</div>
        <div class="stat-label">装修方案</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.active_scheme ? '已应用' : '未应用' }}</div>
        <div class="stat-label">当前状态</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_elements }}</div>
        <div class="stat-label">装饰元素</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.presets_count }}</div>
        <div class="stat-label">可用模板</div>
      </div>
    </div>

    <!-- 装修方案列表 -->
    <div class="scheme-list">
      <div class="list-header">
        <h2>我的装修方案</h2>
        <div class="filter-group">
          <select v-model="filterRoom" class="filter-select">
            <option value="">全部直播间</option>
            <option v-for="room in rooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="schemes-grid">
        <div
          v-for="scheme in filteredSchemes"
          :key="scheme.id"
          class="scheme-card"
          :class="{ 'active': scheme.is_active }"
          @click="viewScheme(scheme)"
        >
          <div class="scheme-preview">
            <div class="preview-placeholder" v-if="!scheme.background">
              <span>暂无预览</span>
            </div>
            <div
              v-else
              class="preview-background"
              :style="{ backgroundColor: scheme.background.color || '#fff' }"
            >
              <div
                v-for="elem in scheme.elements.slice(0, 3)"
                :key="elem.id"
                class="preview-element"
                :style="getPreviewElementStyle(elem)"
              >
                <span v-if="elem.element_type === 'text'">{{ elem.content }}</span>
                <span v-else>🎨</span>
              </div>
            </div>
          </div>
          
          <div class="scheme-info">
            <h3>{{ scheme.name }}</h3>
            <div class="scheme-meta">
              <span class="meta-item">
                <span class="meta-label">元素</span>
                <span class="meta-value">{{ scheme.elements.length }}</span>
              </span>
              <span class="meta-item">
                <span class="meta-label">更新</span>
                <span class="meta-value">{{ formatDate(scheme.updated_at) }}</span>
              </span>
            </div>
            <div class="scheme-status" v-if="scheme.is_active">
              <span class="status-badge active">✓ 已应用</span>
            </div>
          </div>

          <div class="scheme-actions">
            <button
              class="action-btn"
              @click.stop="applyScheme(scheme.id)"
              :disabled="scheme.is_active"
              :title="scheme.is_active ? '当前已应用' : '应用此方案'"
            >
              {{ scheme.is_active ? '✓ 已应用' : '应用' }}
            </button>
            <button class="action-btn" @click.stop="editScheme(scheme)">
              ✏️
            </button>
            <button class="action-btn delete" @click.stop="deleteScheme(scheme.id)">
              🗑️
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredSchemes.length === 0" class="empty-state">
        <div class="empty-icon">🎨</div>
        <p>暂无装修方案</p>
        <button class="btn btn-primary" @click="showCreateModal = true">
          创建第一个方案
        </button>
      </div>
    </div>

    <!-- 装修模板面板 -->
    <div v-if="showPresets" class="panel-overlay">
      <div class="panel panel-wide">
        <div class="panel-header">
          <h2>📋 装修模板</h2>
          <button class="btn-close" @click="showPresets = false">×</button>
        </div>
        <div class="panel-content">
          <div class="category-filter">
            <button
              v-for="cat in presetCategories"
              :key="cat.id"
              class="category-btn"
              :class="{ active: selectedCategory === cat.id }"
              @click="selectedCategory = cat.id"
            >
              {{ cat.name }}
            </button>
          </div>

          <div class="presets-grid">
            <div
              v-for="preset in filteredPresets"
              :key="preset.id"
              class="preset-card"
              @click="selectPreset(preset)"
            >
              <div class="preset-thumbnail" :style="getPresetThumbnailStyle(preset)">
                <span class="preset-emoji">{{ getPresetEmoji(preset.category) }}</span>
              </div>
              <div class="preset-info">
                <h3>{{ preset.name }}</h3>
                <p class="preset-desc">{{ preset.description }}</p>
                <div class="preset-meta">
                  <span class="usage-count">👥 {{ preset.usage_count }}次使用</span>
                  <span class="category-tag">{{ preset.category }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 贴纸库面板 -->
    <div v-if="showStickerLibrary" class="panel-overlay">
      <div class="panel panel-wide">
        <div class="panel-header">
          <h2>🎭 贴纸库</h2>
          <button class="btn-close" @click="showStickerLibrary = false">×</button>
        </div>
        <div class="panel-content">
          <div class="sticker-search">
            <input
              v-model="stickerSearch"
              type="text"
              placeholder="搜索贴纸..."
              @keyup.enter="searchStickers"
            />
            <button class="btn btn-primary" @click="searchStickers">搜索</button>
          </div>

          <div class="category-filter">
            <button
              class="category-btn"
              :class="{ active: selectedStickerCategory === '' }"
              @click="selectedStickerCategory = ''"
            >
              全部
            </button>
            <button
              v-for="cat in stickerCategories"
              :key="cat.id"
              class="category-btn"
              :class="{ active: selectedStickerCategory === cat.id }"
              @click="selectedStickerCategory = cat.id"
            >
              {{ cat.name }} ({{ cat.count }})
            </button>
          </div>

          <div class="stickers-grid">
            <div
              v-for="sticker in filteredStickers"
              :key="sticker.id"
              class="sticker-item"
              @click="addStickerToScheme(sticker)"
            >
              <div class="sticker-preview">
                <span class="sticker-emoji">{{ getStickerEmoji(sticker.category) }}</span>
              </div>
              <div class="sticker-name">{{ sticker.name }}</div>
              <div class="sticker-tags">
                <span v-for="tag in sticker.tags.slice(0, 2)" :key="tag" class="tag">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑方案模态框 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay">
      <div class="modal modal-large">
        <div class="modal-header">
          <h2>{{ showEditModal ? '编辑装修方案' : '创建装修方案' }}</h2>
          <button class="btn-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveScheme" class="scheme-form">
            <div class="form-group">
              <label>方案名称 *</label>
              <input
                v-model="currentScheme.name"
                type="text"
                required
                placeholder="输入方案名称"
              />
            </div>

            <div class="form-group">
              <label>直播间</label>
              <select v-model="currentScheme.room_id">
                <option value="">通用方案</option>
                <option v-for="room in rooms" :key="room.id" :value="room.id">
                  {{ room.name }}
                </option>
              </select>
            </div>
          </form>

          <!-- 背景设置 -->
          <div class="section">
            <h3>🖼️ 背景设置</h3>
            <div class="background-options">
              <div class="option-card" @click="setBackgroundType('color')" :class="{ active: backgroundType === 'color' }">
                <span class="option-icon">🎨</span>
                <span>纯色背景</span>
              </div>
              <div class="option-card" @click="setBackgroundType('image')" :class="{ active: backgroundType === 'image' }">
                <span class="option-icon">🖼️</span>
                <span>图片背景</span>
              </div>
              <div class="option-card" @click="setBackgroundType('gradient')" :class="{ active: backgroundType === 'gradient' }">
                <span class="option-icon">🌈</span>
                <span>渐变背景</span>
              </div>
            </div>

            <div v-if="backgroundType === 'color'" class="background-editor">
              <label>背景颜色</label>
              <div class="color-picker">
                <input
                  v-model="currentScheme.background.color"
                  type="color"
                  class="color-input"
                />
                <input
                  v-model="currentScheme.background.color"
                  type="text"
                  class="color-text"
                />
              </div>
            </div>

            <div v-if="backgroundType === 'image'" class="background-editor">
              <label>背景图片 URL</label>
              <input
                v-model="currentScheme.background.image_url"
                type="text"
                placeholder="输入图片 URL"
              />
              <label>适配模式</label>
              <select v-model="currentScheme.background.fit_mode">
                <option value="cover">覆盖 (cover)</option>
                <option value="contain">包含 (contain)</option>
                <option value="fill">填充 (fill)</option>
                <option value="stretch">拉伸 (stretch)</option>
              </select>
            </div>
          </div>

          <!-- 元素列表 -->
          <div class="section">
            <h3>🎭 装饰元素 ({{ currentScheme.elements.length }})</h3>
            <div class="elements-list">
              <div
                v-for="(elem, index) in currentScheme.elements"
                :key="elem.id"
                class="element-item"
              >
                <span class="element-icon">{{ getElementIcon(elem.element_type) }}</span>
                <span class="element-name">{{ elem.name }}</span>
                <span class="element-type">{{ elem.element_type }}</span>
                <div class="element-actions">
                  <button class="btn-icon" @click="moveElement(index, -1)" :disabled="index === 0">↑</button>
                  <button class="btn-icon" @click="moveElement(index, 1)" :disabled="index === currentScheme.elements.length - 1">↓</button>
                  <button class="btn-icon delete" @click="removeElement(index)">🗑️</button>
                </div>
              </div>
            </div>
            <div class="elements-actions">
              <button class="btn btn-secondary" @click="showStickerLibrary = true; showEditModal = false">
                + 添加贴纸
              </button>
              <button class="btn btn-secondary" @click="addTextElement">
                + 添加文字
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">取消</button>
          <button class="btn btn-primary" @click="saveScheme">保存</button>
        </div>
      </div>
    </div>

    <!-- 方案详情面板 -->
    <div v-if="selectedScheme" class="panel-overlay">
      <div class="panel panel-wide">
        <div class="panel-header">
          <h2>{{ selectedScheme.name }}</h2>
          <button class="btn-close" @click="selectedScheme = null">×</button>
        </div>
        <div class="panel-content">
          <!-- 预览区域 -->
          <div class="preview-area">
            <div
              class="preview-canvas"
              :style="getPreviewCanvasStyle(selectedScheme)"
            >
              <div
                v-for="elem in selectedScheme.elements"
                :key="elem.id"
                class="preview-element"
                :style="getPreviewElementStyle(elem)"
              >
                <span v-if="elem.element_type === 'text'">{{ elem.content }}</span>
                <span v-else-if="elem.element_type === 'sticker'">🎨</span>
                <span v-else>元素</span>
              </div>
            </div>
          </div>

          <!-- 方案信息 -->
          <div class="detail-section">
            <h3>方案信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">创建时间</span>
                <span class="value">{{ formatDate(selectedScheme.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">更新时间</span>
                <span class="value">{{ formatDate(selectedScheme.updated_at) }}</span>
              </div>
              <div class="info-item">
                <span class="label">元素数量</span>
                <span class="value">{{ selectedScheme.elements.length }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态</span>
                <span class="value status-badge" :class="{ active: selectedScheme.is_active }">
                  {{ selectedScheme.is_active ? '已应用' : '未应用' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 元素列表 -->
          <div class="detail-section">
            <h3>装饰元素</h3>
            <div class="elements-table">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>类型</th>
                    <th>名称</th>
                    <th>位置</th>
                    <th>大小</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="elem in selectedScheme.elements" :key="elem.id">
                    <td>{{ getElementIcon(elem.element_type) }} {{ elem.element_type }}</td>
                    <td>{{ elem.name }}</td>
                    <td>({{ Math.round(elem.x) }}, {{ Math.round(elem.y) }})</td>
                    <td>{{ Math.round(elem.width) }} × {{ Math.round(elem.height) }}</td>
                    <td>
                      <button class="btn-icon" @click="editElement(elem)">✏️</button>
                      <button class="btn-icon delete" @click="deleteElementFromScheme(selectedScheme.id, elem.id)">🗑️</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="detail-actions">
            <button class="btn btn-secondary" @click="editScheme(selectedScheme)">编辑</button>
            <button
              class="btn btn-primary"
              @click="applyScheme(selectedScheme.id)"
              :disabled="selectedScheme.is_active"
            >
              {{ selectedScheme.is_active ? '✓ 已应用' : '应用此方案' }}
            </button>
            <button class="btn btn-secondary" @click="exportScheme(selectedScheme.id)">
              📥 导出
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 应用预设确认模态框 -->
    <div v-if="showPresetConfirm" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h2>应用装修模板</h2>
          <button class="btn-close" @click="showPresetConfirm = false">×</button>
        </div>
        <div class="modal-body">
          <p>确定要将 <strong>{{ selectedPreset?.name }}</strong> 应用到当前方案吗？</p>
          <p class="warning">⚠️ 这会覆盖方案现有的所有元素</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPresetConfirm = false">取消</button>
          <button class="btn btn-primary" @click="confirmApplyPreset">确认应用</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Decorator',
  data() {
    return {
      schemes: [],
      presets: [],
      stickers: [],
      stats: null,
      activeScheme: null,
      filterRoom: '',
      rooms: [
        { id: 'room_001', name: '主直播间' },
        { id: 'room_002', name: '副直播间' },
        { id: 'room_003', name: '活动直播间' }
      ],
      showPresets: false,
      showStickerLibrary: false,
      showCreateModal: false,
      showEditModal: false,
      showPresetConfirm: false,
      selectedScheme: null,
      selectedPreset: null,
      selectedCategory: '',
      selectedStickerCategory: '',
      stickerSearch: '',
      backgroundType: 'color',
      currentScheme: {
        id: '',
        name: '',
        room_id: '',
        background: {
          element_type: 'background',
          name: '背景',
          color: '#FFFFFF',
          image_url: '',
          fit_mode: 'cover'
        },
        elements: []
      }
    }
  },
  computed: {
    filteredSchemes() {
      if (!this.filterRoom) return this.schemes
      return this.schemes.filter(s => s.room_id === this.filterRoom)
    },
    filteredPresets() {
      if (!this.selectedCategory) return this.presets
      return this.presets.filter(p => p.category === this.selectedCategory)
    },
    filteredStickers() {
      let result = this.stickers
      if (this.selectedStickerCategory) {
        result = result.filter(s => s.category === this.selectedStickerCategory)
      }
      if (this.stickerSearch) {
        const keyword = this.stickerSearch.toLowerCase()
        result = result.filter(s =>
          s.name.toLowerCase().includes(keyword) ||
          s.tags.some(tag => tag.toLowerCase().includes(keyword))
        )
      }
      return result
    },
    presetCategories() {
      const categories = {
        'default': '默认',
        'minimal': '简约',
        'festival': '节日',
        'promotion': '促销',
        'gaming': '游戏'
      }
      return Object.entries(categories).map(([id, name]) => ({ id, name }))
    },
    stickerCategories() {
      const cats = {}
      this.stickers.forEach(s => {
        cats[s.category] = (cats[s.category] || 0) + 1
      })
      const names = {
        'default': '默认',
        'festival': '节日庆典',
        'promotion': '促销活动',
        'decoration': '装饰元素',
        'emoji': '表情符号',
        'gaming': '游戏直播'
      }
      return Object.entries(cats).map(([id, count]) => ({
        id,
        name: names[id] || id,
        count
      }))
    }
  },
  mounted() {
    this.loadSchemes()
    this.loadPresets()
    this.loadStickers()
    this.loadStats()
    this.loadActiveScheme()
  },
  methods: {
    // API 调用
    async loadSchemes() {
      try {
        const res = await fetch('/api/decorator/schemes')
        const data = await res.json()
        this.schemes = data.schemes
      } catch (error) {
        console.error('加载方案失败:', error)
      }
    },
    async loadPresets() {
      try {
        const res = await fetch('/api/decorator/presets')
        const data = await res.json()
        this.presets = data
      } catch (error) {
        console.error('加载模板失败:', error)
      }
    },
    async loadStickers() {
      try {
        const res = await fetch('/api/decorator/stickers')
        const data = await res.json()
        this.stickers = data
      } catch (error) {
        console.error('加载贴纸失败:', error)
      }
    },
    async loadStats() {
      try {
        const res = await fetch('/api/decorator/stats')
        const data = await res.json()
        this.stats = data
      } catch (error) {
        console.error('加载统计失败:', error)
        // 使用本地计算
        this.stats = {
          total_schemes: this.schemes.length,
          active_scheme: this.activeScheme,
          total_elements: this.schemes.reduce((sum, s) => sum + (s.elements?.length || 0), 0),
          presets_count: this.presets.length
        }
      }
    },
    async loadActiveScheme() {
      try {
        const res = await fetch('/api/decorator/schemes/active')
        const data = await res.json()
        this.activeScheme = data
      } catch (error) {
        console.error('加载活跃方案失败:', error)
      }
    },

    // 方案操作
    async createScheme() {
      try {
        const payload = {
          name: this.currentScheme.name,
          room_id: this.currentScheme.room_id
        }
        const res = await fetch('/api/decorator/schemes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (data.id) {
          this.loadSchemes()
          this.closeModal()
          this.resetCurrentScheme()
          this.editScheme(data) // 创建后直接编辑
        }
      } catch (error) {
        console.error('创建方案失败:', error)
      }
    },

    async updateScheme() {
      try {
        const payload = {
          name: this.currentScheme.name,
          background: this.currentScheme.background,
          elements: this.currentScheme.elements
        }
        const res = await fetch(`/api/decorator/schemes/${this.currentScheme.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (data.id) {
          this.loadSchemes()
          this.closeModal()
          this.resetCurrentScheme()
        }
      } catch (error) {
        console.error('更新方案失败:', error)
      }
    },

    async saveScheme() {
      if (this.showEditModal) {
        await this.updateScheme()
      } else {
        await this.createScheme()
      }
    },

    async deleteScheme(id) {
      if (!confirm('确定要删除这个装修方案吗？')) return
      try {
        await fetch(`/api/decorator/schemes/${id}`, { method: 'DELETE' })
        this.loadSchemes()
        if (this.selectedScheme?.id === id) {
          this.selectedScheme = null
        }
      } catch (error) {
        console.error('删除方案失败:', error)
      }
    },

    async applyScheme(id) {
      try {
        const res = await fetch(`/api/decorator/schemes/${id}/apply`, {
          method: 'POST'
        })
        const data = await res.json()
        if (data.id) {
          this.loadSchemes()
          this.loadActiveScheme()
          alert('装修方案已应用！')
        }
      } catch (error) {
        console.error('应用方案失败:', error)
      }
    },

    async exportScheme(id) {
      try {
        const res = await fetch(`/api/decorator/schemes/${id}/export`)
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `scheme_${id}.json`
        a.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('导出方案失败:', error)
      }
    },

    // 编辑操作
    editScheme(scheme) {
      this.currentScheme = JSON.parse(JSON.stringify(scheme))
      if (!this.currentScheme.background) {
        this.currentScheme.background = {
          element_type: 'background',
          name: '背景',
          color: '#FFFFFF',
          image_url: '',
          fit_mode: 'cover'
        }
      }
      this.backgroundType = this.currentScheme.background.image_url ? 'image' : 'color'
      this.showEditModal = true
    },

    viewScheme(scheme) {
      this.selectedScheme = scheme
    },

    closeModal() {
      this.showCreateModal = false
      this.showEditModal = false
      this.resetCurrentScheme()
    },

    resetCurrentScheme() {
      this.currentScheme = {
        id: '',
        name: '',
        room_id: '',
        background: {
          element_type: 'background',
          name: '背景',
          color: '#FFFFFF',
          image_url: '',
          fit_mode: 'cover'
        },
        elements: []
      }
    },

    // 背景设置
    setBackgroundType(type) {
      this.backgroundType = type
      if (type === 'color') {
        this.currentScheme.background.image_url = ''
      }
    },

    // 元素操作
    addTextElement() {
      this.currentScheme.elements.push({
        id: 'text_' + Date.now(),
        element_type: 'text',
        name: '文字',
        content: '点击编辑文字',
        x: 100,
        y: 100,
        width: 200,
        height: 50,
        font_size: 32,
        color: '#000000',
        rotation: 0,
        opacity: 1,
        z_index: this.currentScheme.elements.length
      })
    },

    addStickerToScheme(sticker) {
      this.currentScheme.elements.push({
        id: 'sticker_' + Date.now(),
        element_type: 'sticker',
        name: sticker.name,
        image_url: sticker.url,
        category: sticker.category,
        x: 100,
        y: 100,
        width: 100,
        height: 100,
        rotation: 0,
        opacity: 1,
        z_index: this.currentScheme.elements.length
      })
      this.showStickerLibrary = false
      if (!this.showEditModal) {
        this.showEditModal = true
      }
    },

    removeElement(index) {
      this.currentScheme.elements.splice(index, 1)
    },

    moveElement(index, direction) {
      const newIndex = index + direction
      if (newIndex < 0 || newIndex >= this.currentScheme.elements.length) return
      const temp = this.currentScheme.elements[index]
      this.currentScheme.elements[index] = this.currentScheme.elements[newIndex]
      this.currentScheme.elements[newIndex] = temp
    },

    editElement(elem) {
      // 打开元素编辑器
      alert('元素编辑功能开发中...')
    },

    async deleteElementFromScheme(schemeId, elementId) {
      try {
        const res = await fetch(`/api/decorator/schemes/${schemeId}/elements/${elementId}`, {
          method: 'DELETE'
        })
        const data = await res.json()
        if (data.id) {
          this.selectedScheme = data
        }
      } catch (error) {
        console.error('删除元素失败:', error)
      }
    },

    // 预设操作
    selectPreset(preset) {
      this.selectedPreset = preset
      this.showPresetConfirm = true
      this.showPresets = false
    },

    async confirmApplyPreset() {
      if (!this.selectedScheme || !this.selectedPreset) return
      try {
        const res = await fetch(
          `/api/decorator/schemes/${this.selectedScheme.id}/apply-preset/${this.selectedPreset.id}`,
          { method: 'POST' }
        )
        const data = await res.json()
        if (data.id) {
          this.selectedScheme = data
          this.loadSchemes()
          alert('模板已应用！')
        }
      } catch (error) {
        console.error('应用模板失败:', error)
      }
      this.showPresetConfirm = false
      this.selectedPreset = null
    },

    async searchStickers() {
      if (!this.stickerSearch) {
        this.loadStickers()
        return
      }
      try {
        const res = await fetch(`/api/decorator/stickers?keyword=${encodeURIComponent(this.stickerSearch)}`)
        const data = await res.json()
        this.stickers = data
      } catch (error) {
        console.error('搜索贴纸失败:', error)
      }
    },

    // 样式工具函数
    getPreviewCanvasStyle(scheme) {
      const style = {
        position: 'relative',
        width: '100%',
        height: '400px',
        overflow: 'hidden',
        borderRadius: '8px',
        border: '1px solid #e5e7eb'
      }
      if (scheme.background) {
        style.backgroundColor = scheme.background.color || '#FFFFFF'
        if (scheme.background.image_url) {
          style.backgroundImage = `url(${scheme.background.image_url})`
          style.backgroundSize = scheme.background.fit_mode || 'cover'
        }
      }
      return style
    },

    getPreviewElementStyle(elem) {
      return {
        position: 'absolute',
        left: elem.x + 'px',
        top: elem.y + 'px',
        width: elem.width + 'px',
        height: elem.height + 'px',
        transform: `rotate(${elem.rotation || 0}deg)`,
        opacity: elem.opacity || 1,
        zIndex: elem.z_index || 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: elem.font_size ? elem.font_size + 'px' : '14px',
        color: elem.color || '#000000',
        backgroundColor: elem.background_color || 'transparent'
      }
    },

    getPresetThumbnailStyle(preset) {
      const colors = {
        'default': '#F3F4F6',
        'minimal': '#E5E7EB',
        'festival': '#FF6B6B',
        'promotion': '#FFD93D',
        'gaming': '#1A1A2E'
      }
      return {
        backgroundColor: colors[preset.category] || '#F3F4F6'
      }
    },

    getPresetEmoji(category) {
      const emojis = {
        'default': '📋',
        'minimal': '✨',
        'festival': '🎉',
        'promotion': '🏷️',
        'gaming': '🎮'
      }
      return emojis[category] || '🎨'
    },

    getStickerEmoji(category) {
      const emojis = {
        'default': '🎨',
        'festival': '🏮',
        'promotion': '🏷️',
        'decoration': '✨',
        'emoji': '😊',
        'gaming': '🎮'
      }
      return emojis[category] || '🎨'
    },

    getElementIcon(type) {
      const icons = {
        'text': '📝',
        'sticker': '🎭',
        'image': '🖼️',
        'background': '🖼️'
      }
      return icons[type] || '🎨'
    },

    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.decorator-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #1a1a1a;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #4f46e5;
  color: white;
}

.btn-primary:hover {
  background: #4338ca;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #4f46e5;
}

.stat-label {
  color: #6b7280;
  margin-top: 5px;
}

/* 方案列表 */
.scheme-list {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h2 {
  font-size: 20px;
  color: #1a1a1a;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.schemes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.scheme-card {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.scheme-card:hover {
  border-color: #4f46e5;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.scheme-card.active {
  border-color: #059669;
  background: #f0fdf4;
}

.scheme-preview {
  height: 180px;
  background: #f9fafb;
  overflow: hidden;
}

.preview-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.preview-background {
  height: 100%;
  position: relative;
}

.preview-element {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.8);
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
}

.scheme-info {
  padding: 16px;
}

.scheme-info h3 {
  font-size: 18px;
  color: #1a1a1a;
  margin: 0 0 10px 0;
}

.scheme-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 11px;
  color: #9ca3af;
}

.meta-value {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.scheme-status {
  margin-top: 10px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d1fae5;
  color: #059669;
}

.scheme-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.action-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  background: white;
  border: 1px solid #d1d5db;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.delete {
  color: #ef4444;
  border-color: #fee2e2;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

/* 面板 */
.panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: flex-end;
  z-index: 1000;
}

.panel {
  background: white;
  width: 700px;
  max-height: 100vh;
  overflow-y: auto;
  animation: slideIn 0.3s ease;
}

.panel-wide {
  width: 900px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h2 {
  font-size: 20px;
  color: #1a1a1a;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.panel-content {
  padding: 20px;
}

/* 分类筛选 */
.category-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.category-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.category-btn:hover {
  background: #f9fafb;
}

.category-btn.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

/* 预设网格 */
.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.preset-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-card:hover {
  border-color: #4f46e5;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.preset-thumbnail {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preset-emoji {
  font-size: 48px;
}

.preset-info {
  padding: 12px;
}

.preset-info h3 {
  font-size: 15px;
  color: #1a1a1a;
  margin: 0 0 6px 0;
}

.preset-desc {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.preset-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.usage-count {
  font-size: 11px;
  color: #9ca3af;
}

.category-tag {
  font-size: 10px;
  background: #f3f4f6;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 贴纸网格 */
.sticker-search {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.sticker-search input {
  flex: 1;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.stickers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.sticker-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.sticker-item:hover {
  border-color: #4f46e5;
  background: #f5f3ff;
}

.sticker-preview {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.sticker-emoji {
  font-size: 36px;
}

.sticker-name {
  font-size: 12px;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.sticker-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.sticker-tags .tag {
  font-size: 9px;
  background: #f3f4f6;
  color: #6b7280;
  padding: 2px 6px;
  border-radius: 8px;
}

/* 模态框 */
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
  border-radius: 12px;
  width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 20px;
  color: #1a1a1a;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

/* 表单 */
.scheme-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.form-group input,
.form-group select {
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

/* 背景选项 */
.background-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 15px;
}

.option-card {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.option-card:hover {
  border-color: #4f46e5;
}

.option-card.active {
  border-color: #4f46e5;
  background: #f5f3ff;
}

.option-icon {
  font-size: 24px;
  display: block;
  margin-bottom: 8px;
}

.background-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
}

.background-editor label {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.color-picker {
  display: flex;
  gap: 10px;
  align-items: center;
}

.color-input {
  width: 50px;
  height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
}

.color-text {
  flex: 1;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

/* 元素列表 */
.section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.section h3 {
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 15px;
}

.elements-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.element-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f9fafb;
  border-radius: 6px;
}

.element-icon {
  font-size: 18px;
}

.element-name {
  flex: 1;
  font-size: 14px;
  color: #1a1a1a;
}

.element-type {
  font-size: 11px;
  background: #e0e7ff;
  color: #4f46e5;
  padding: 2px 8px;
  border-radius: 10px;
}

.element-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  background: none;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}

.btn-icon:hover {
  background: #e5e7eb;
}

.btn-icon.delete:hover {
  background: #fee2e2;
}

.elements-actions {
  display: flex;
  gap: 10px;
}

/* 预览区域 */
.preview-area {
  margin-bottom: 20px;
}

.preview-canvas {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

/* 详情 */
.detail-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h3 {
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item .label {
  font-size: 12px;
  color: #9ca3af;
}

.info-item .value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

.elements-table {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
}

.data-table td {
  color: #1a1a1a;
  font-size: 14px;
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.warning {
  color: #dc2626;
  font-size: 13px;
  margin-top: 10px;
}
</style>
