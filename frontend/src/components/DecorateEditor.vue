<template>
  <div class="decorate-editor">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-section">
        <button
          class="tool-btn"
          :class="{ active: tool === 'select' }"
          @click="tool = 'select'"
          title="选择工具 (V)"
        >
          <span>👆</span>
          <span class="tool-label">选择</span>
        </button>
        <button
          class="tool-btn"
          :class="{ active: tool === 'move' }"
          @click="tool = 'move'"
          title="移动工具 (M)"
        >
          <span>✋</span>
          <span class="tool-label">移动</span>
        </button>
        <button
          class="tool-btn"
          :class="{ active: tool === 'text' }"
          @click="addTextElement"
          title="文字工具 (T)"
        >
          <span>📝</span>
          <span class="tool-label">文字</span>
        </button>
        <button
          class="tool-btn"
          :class="{ active: tool === 'sticker' }"
          @click="$emit('open-sticker-library')"
          title="贴纸工具 (S)"
        >
          <span>🎭</span>
          <span class="tool-label">贴纸</span>
        </button>
      </div>

      <div class="toolbar-section">
        <button
          class="tool-btn"
          @click="undo"
          :disabled="!canUndo"
          title="撤销 (Ctrl+Z)"
        >
          <span>↩️</span>
        </button>
        <button
          class="tool-btn"
          @click="redo"
          :disabled="!canRedo"
          title="重做 (Ctrl+Y)"
        >
          <span>↪️</span>
        </button>
      </div>

      <div class="toolbar-section">
        <button
          class="tool-btn"
          @click="zoomIn"
          title="放大"
        >
          <span>🔍+</span>
        </button>
        <span class="zoom-level">{{ zoom }}%</span>
        <button
          class="tool-btn"
          @click="zoomOut"
          title="缩小"
        >
          <span>🔍-</span>
        </button>
      </div>

      <div class="toolbar-section">
        <button
          class="tool-btn danger"
          @click="deleteSelected"
          :disabled="!selectedElement"
          title="删除 (Delete)"
        >
          <span>🗑️</span>
          <span class="tool-label">删除</span>
        </button>
      </div>
    </div>

    <!-- 画布区域 -->
    <div class="canvas-container">
      <div
        ref="canvasRef"
        class="canvas"
        :style="canvasStyle"
        @mousedown="handleCanvasMouseDown"
        @mousemove="handleCanvasMouseMove"
        @mouseup="handleCanvasMouseUp"
        @mouseleave="handleCanvasMouseUp"
      >
        <!-- 背景 -->
        <div
          class="canvas-background"
          :style="backgroundStyle"
        ></div>

        <!-- 元素 -->
        <div
          v-for="elem in sortedElements"
          :key="elem.id"
          class="canvas-element"
          :class="{ selected: selectedElement?.id === elem.id }"
          :style="getElementStyle(elem)"
          @mousedown.stop="selectElement(elem, $event)"
        >
          <!-- 元素内容 -->
          <div class="element-content">
            <span v-if="elem.element_type === 'text'">{{ elem.content }}</span>
            <span v-else-if="elem.element_type === 'sticker'">🎨</span>
            <span v-else>元素</span>
          </div>

          <!-- 选中时的控制点 -->
          <div v-if="selectedElement?.id === elem.id" class="element-controls">
            <div class="control-point nw" @mousedown.stop="startResize(elem, 'nw', $event)"></div>
            <div class="control-point n" @mousedown.stop="startResize(elem, 'n', $event)"></div>
            <div class="control-point ne" @mousedown.stop="startResize(elem, 'ne', $event)"></div>
            <div class="control-point e" @mousedown.stop="startResize(elem, 'e', $event)"></div>
            <div class="control-point se" @mousedown.stop="startResize(elem, 'se', $event)"></div>
            <div class="control-point s" @mousedown.stop="startResize(elem, 's', $event)"></div>
            <div class="control-point sw" @mousedown.stop="startResize(elem, 'sw', $event)"></div>
            <div class="control-point w" @mousedown.stop="startResize(elem, 'w', $event)"></div>
            
            <!-- 旋转控制 -->
            <div class="rotate-handle" @mousedown.stop="startRotate(elem, $event)">
              <span>🔄</span>
            </div>
          </div>

          <!-- 元素信息 -->
          <div v-if="selectedElement?.id === elem.id" class="element-info">
            <span>{{ elem.name }}</span>
            <span class="element-size">{{ Math.round(elem.width) }} × {{ Math.round(elem.height) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 属性面板 -->
    <div class="properties-panel">
      <div class="panel-header">
        <h3>属性</h3>
      </div>

      <div v-if="selectedElement" class="panel-content">
        <!-- 基本信息 -->
        <div class="property-group">
          <h4>基本信息</h4>
          <div class="property-row">
            <label>名称</label>
            <input
              v-model="selectedElement.name"
              type="text"
              @change="emitUpdate"
            />
          </div>
          <div class="property-row">
            <label>类型</label>
            <span class="property-value">{{ selectedElement.element_type }}</span>
          </div>
        </div>

        <!-- 位置大小 -->
        <div class="property-group">
          <h4>位置与大小</h4>
          <div class="property-row-inline">
            <div class="property-field">
              <label>X</label>
              <input
                v-model.number="selectedElement.x"
                type="number"
                @change="emitUpdate"
              />
            </div>
            <div class="property-field">
              <label>Y</label>
              <input
                v-model.number="selectedElement.y"
                type="number"
                @change="emitUpdate"
              />
            </div>
          </div>
          <div class="property-row-inline">
            <div class="property-field">
              <label>宽度</label>
              <input
                v-model.number="selectedElement.width"
                type="number"
                @change="emitUpdate"
              />
            </div>
            <div class="property-field">
              <label>高度</label>
              <input
                v-model.number="selectedElement.height"
                type="number"
                @change="emitUpdate"
              />
            </div>
          </div>
          <div class="property-row-inline">
            <div class="property-field">
              <label>旋转</label>
              <input
                v-model.number="selectedElement.rotation"
                type="number"
                @change="emitUpdate"
              />
              <span class="unit">°</span>
            </div>
            <div class="property-field">
              <label>透明度</label>
              <input
                v-model.number="selectedElement.opacity"
                type="range"
                min="0"
                max="1"
                step="0.1"
                @change="emitUpdate"
              />
              <span class="unit">{{ Math.round(selectedElement.opacity * 100) }}%</span>
            </div>
          </div>
        </div>

        <!-- 文字属性 -->
        <div v-if="selectedElement.element_type === 'text'" class="property-group">
          <h4>文字属性</h4>
          <div class="property-row">
            <label>内容</label>
            <textarea
              v-model="selectedElement.content"
              rows="3"
              @change="emitUpdate"
            ></textarea>
          </div>
          <div class="property-row">
            <label>字体</label>
            <select
              v-model="selectedElement.font_family"
              @change="emitUpdate"
            >
              <option value="Arial">Arial</option>
              <option value="Microsoft YaHei">微软雅黑</option>
              <option value="SimHei">黑体</option>
              <option value="KaiTi">楷体</option>
              <option value="Songti SC">宋体</option>
            </select>
          </div>
          <div class="property-row-inline">
            <div class="property-field">
              <label>大小</label>
              <input
                v-model.number="selectedElement.font_size"
                type="number"
                @change="emitUpdate"
              />
            </div>
            <div class="property-field">
              <label>字重</label>
              <select
                v-model="selectedElement.font_weight"
                @change="emitUpdate"
              >
                <option value="normal">正常</option>
                <option value="bold">粗体</option>
              </select>
            </div>
          </div>
          <div class="property-row">
            <label>颜色</label>
            <div class="color-picker">
              <input
                v-model="selectedElement.color"
                type="color"
                @change="emitUpdate"
              />
              <input
                v-model="selectedElement.color"
                type="text"
                @change="emitUpdate"
              />
            </div>
          </div>
          <div class="property-row">
            <label>对齐</label>
            <div class="align-buttons">
              <button
                :class="{ active: selectedElement.text_align === 'left' }"
                @click="selectedElement.text_align = 'left'; emitUpdate()"
              >
                左
              </button>
              <button
                :class="{ active: selectedElement.text_align === 'center' }"
                @click="selectedElement.text_align = 'center'; emitUpdate()"
              >
                中
              </button>
              <button
                :class="{ active: selectedElement.text_align === 'right' }"
                @click="selectedElement.text_align = 'right'; emitUpdate()"
              >
                右
              </button>
            </div>
          </div>
        </div>

        <!-- 贴纸属性 -->
        <div v-if="selectedElement.element_type === 'sticker'" class="property-group">
          <h4>贴纸属性</h4>
          <div class="property-row">
            <label>分类</label>
            <span class="property-value">{{ selectedElement.category || 'default' }}</span>
          </div>
          <div class="property-row">
            <label>图片 URL</label>
            <input
              v-model="selectedElement.image_url"
              type="text"
              @change="emitUpdate"
              placeholder="输入图片 URL"
            />
          </div>
        </div>

        <!-- 层级控制 -->
        <div class="property-group">
          <h4>层级控制</h4>
          <div class="property-row">
            <label>Z 轴</label>
            <input
              v-model.number="selectedElement.z_index"
              type="number"
              @change="emitUpdate"
            />
          </div>
          <div class="layer-actions">
            <button class="btn-sm" @click="moveLayer(-1)">↓ 下移一层</button>
            <button class="btn-sm" @click="moveLayer(1)">↑ 上移一层</button>
            <button class="btn-sm" @click="sendToBack()">到底层</button>
            <button class="btn-sm" @click="bringToFront()">到顶层</button>
          </div>
        </div>

        <!-- 可见性与锁定 -->
        <div class="property-group">
          <h4>可见性与锁定</h4>
          <div class="property-row checkbox-row">
            <label>
              <input
                type="checkbox"
                v-model="selectedElement.visible"
                @change="emitUpdate"
              />
              可见
            </label>
          </div>
          <div class="property-row checkbox-row">
            <label>
              <input
                type="checkbox"
                v-model="selectedElement.locked"
                @change="emitUpdate"
              />
              锁定
            </label>
          </div>
        </div>
      </div>

      <div v-else class="panel-empty">
        <p>选择一个元素以编辑属性</p>
        <p class="hint">或点击画布空白处设置背景</p>
      </div>

      <!-- 背景属性（未选择元素时） -->
      <div v-if="!selectedElement && background" class="panel-content">
        <div class="property-group">
          <h4>背景设置</h4>
          <div class="property-row">
            <label>背景颜色</label>
            <div class="color-picker">
              <input
                v-model="background.color"
                type="color"
                @change="emitBackgroundUpdate"
              />
              <input
                v-model="background.color"
                type="text"
                @change="emitBackgroundUpdate"
              />
            </div>
          </div>
          <div class="property-row">
            <label>适配模式</label>
            <select
              v-model="background.fit_mode"
              @change="emitBackgroundUpdate"
            >
              <option value="cover">覆盖 (cover)</option>
              <option value="contain">包含 (contain)</option>
              <option value="fill">填充 (fill)</option>
              <option value="stretch">拉伸 (stretch)</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- 元素列表面板 -->
    <div class="elements-panel">
      <div class="panel-header">
        <h3>元素列表</h3>
        <button class="btn-icon" @click="$emit('add-element')" title="添加元素">+</button>
      </div>
      <div class="elements-list">
        <div
          v-for="(elem, index) in sortedElements"
          :key="elem.id"
          class="element-list-item"
          :class="{ selected: selectedElement?.id === elem.id }"
          @click="selectElement(elem)"
        >
          <span class="element-icon">{{ getElementIcon(elem.element_type) }}</span>
          <span class="element-name">{{ elem.name || elem.element_type }}</span>
          <div class="element-visibility">
            <button
              class="btn-icon-sm"
              @click.stop="toggleVisibility(elem)"
              :title="elem.visible ? '隐藏' : '显示'"
            >
              {{ elem.visible ? '👁️' : '👁️‍🗨️' }}
            </button>
            <button
              class="btn-icon-sm"
              @click.stop="toggleLock(elem)"
              :title="elem.locked ? '解锁' : '锁定'"
            >
              {{ elem.locked ? '🔒' : '🔓' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DecorateEditor',
  props: {
    scheme: {
      type: Object,
      required: true
    },
    background: {
      type: Object,
      default: () => ({
        color: '#FFFFFF',
        image_url: '',
        fit_mode: 'cover'
      })
    }
  },
  emits: ['update:elements', 'update:background', 'open-sticker-library', 'add-element'],
  data() {
    return {
      tool: 'select',
      zoom: 100,
      selectedElement: null,
      isDragging: false,
      isResizing: false,
      isRotating: false,
      dragOffset: { x: 0, y: 0 },
      resizeData: null,
      rotateData: null,
      history: [],
      historyIndex: -1,
      canvasRect: null
    }
  },
  computed: {
    canvasStyle() {
      return {
        transform: `scale(${this.zoom / 100})`,
        transformOrigin: 'top left'
      }
    },
    backgroundStyle() {
      const style = {
        backgroundColor: this.background?.color || '#FFFFFF',
        width: '1920px',
        height: '1080px'
      }
      if (this.background?.image_url) {
        style.backgroundImage = `url(${this.background.image_url})`
        style.backgroundSize = this.background.fit_mode || 'cover'
        style.backgroundPosition = 'center'
        style.backgroundRepeat = 'no-repeat'
      }
      return style
    },
    sortedElements() {
      return [...(this.scheme?.elements || [])].sort((a, b) => (a.z_index || 0) - (b.z_index || 0))
    },
    canUndo() {
      return this.historyIndex > 0
    },
    canRedo() {
      return this.historyIndex < this.history.length - 1
    }
  },
  mounted() {
    this.initCanvas()
    this.setupKeyboardShortcuts()
    window.addEventListener('resize', this.initCanvas)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.initCanvas)
    window.removeEventListener('keydown', this.handleKeyDown)
    window.removeEventListener('mousemove', this.handleGlobalMouseMove)
    window.removeEventListener('mouseup', this.handleGlobalMouseUp)
  },
  methods: {
    initCanvas() {
      const canvas = this.$refs.canvasRef
      if (canvas) {
        this.canvasRect = canvas.getBoundingClientRect()
      }
    },

    setupKeyboardShortcuts() {
      window.addEventListener('keydown', this.handleKeyDown)
    },

    handleKeyDown(e) {
      // 撤销/重做
      if (e.ctrlKey && e.key === 'z') {
        e.preventDefault()
        this.undo()
      }
      if (e.ctrlKey && e.key === 'y') {
        e.preventDefault()
        this.redo()
      }

      // 删除
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (this.selectedElement && document.activeElement.tagName !== 'INPUT') {
          e.preventDefault()
          this.deleteSelected()
        }
      }

      // 工具切换
      if (e.key === 'v' || e.key === 'V') this.tool = 'select'
      if (e.key === 'm' || e.key === 'M') this.tool = 'move'
      if (e.key === 't' || e.key === 'T') this.addTextElement()
      if (e.key === 's' || e.key === 'S') this.$emit('open-sticker-library')

      // 方向键微调
      if (this.selectedElement && ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        e.preventDefault()
        const step = e.shiftKey ? 10 : 1
        if (e.key === 'ArrowUp') this.selectedElement.y -= step
        if (e.key === 'ArrowDown') this.selectedElement.y += step
        if (e.key === 'ArrowLeft') this.selectedElement.x -= step
        if (e.key === 'ArrowRight') this.selectedElement.x += step
        this.emitUpdate()
      }
    },

    getElementStyle(elem) {
      if (!elem.visible) {
        return {
          display: 'none'
        }
      }

      const style = {
        left: elem.x + 'px',
        top: elem.y + 'px',
        width: elem.width + 'px',
        height: elem.height + 'px',
        transform: `rotate(${elem.rotation || 0}deg)`,
        opacity: elem.opacity || 1,
        zIndex: elem.z_index || 0,
        cursor: elem.locked ? 'not-allowed' : (this.tool === 'move' ? 'move' : 'pointer')
      }

      if (elem.element_type === 'text') {
        style.fontFamily = elem.font_family || 'Arial'
        style.fontSize = elem.font_size + 'px'
        style.fontWeight = elem.font_weight || 'normal'
        style.color = elem.color || '#000000'
        style.textAlign = elem.text_align || 'left'
        style.backgroundColor = elem.background_color || 'transparent'
      }

      return style
    },

    selectElement(elem, event) {
      if (elem.locked) return
      this.selectedElement = elem
      
      if (this.tool === 'move' || this.tool === 'select') {
        this.isDragging = true
        this.dragOffset = {
          x: event.clientX - elem.x,
          y: event.clientY - elem.y
        }
        
        window.addEventListener('mousemove', this.handleGlobalMouseMove)
        window.addEventListener('mouseup', this.handleGlobalMouseUp)
      }
    },

    handleCanvasMouseDown(e) {
      if (e.target === this.$refs.canvasRef || e.target.classList.contains('canvas-background')) {
        this.selectedElement = null
      }
    },

    handleCanvasMouseMove(e) {
      // 可以在这里添加画布级别的鼠标移动处理
    },

    handleCanvasMouseUp(e) {
      // 画布级别的鼠标释放处理
    },

    handleGlobalMouseMove(e) {
      if (this.isDragging && this.selectedElement) {
        this.selectedElement.x = e.clientX - this.dragOffset.x
        this.selectedElement.y = e.clientY - this.dragOffset.y
      } else if (this.isResizing && this.resizeData) {
        this.handleResize(e)
      } else if (this.isRotating && this.rotateData) {
        this.handleRotate(e)
      }
    },

    handleGlobalMouseUp(e) {
      if (this.isDragging || this.isResizing || this.isRotating) {
        this.saveToHistory()
        this.emitUpdate()
      }
      this.isDragging = false
      this.isResizing = false
      this.isRotating = false
      this.resizeData = null
      this.rotateData = null
      
      window.removeEventListener('mousemove', this.handleGlobalMouseMove)
      window.removeEventListener('mouseup', this.handleGlobalMouseUp)
    },

    startResize(elem, direction, e) {
      if (elem.locked) return
      this.isResizing = true
      this.resizeData = {
        element: elem,
        direction,
        startX: e.clientX,
        startY: e.clientY,
        startWidth: elem.width,
        startHeight: elem.height,
        startXPos: elem.x,
        startYPos: elem.y
      }
      
      window.addEventListener('mousemove', this.handleGlobalMouseMove)
      window.addEventListener('mouseup', this.handleGlobalMouseUp)
    },

    handleResize(e) {
      if (!this.resizeData) return
      
      const dx = e.clientX - this.resizeData.startX
      const dy = e.clientY - this.resizeData.startY
      const elem = this.resizeData.element
      const dir = this.resizeData.direction

      if (dir.includes('e')) {
        elem.width = Math.max(20, this.resizeData.startWidth + dx)
      }
      if (dir.includes('w')) {
        elem.width = Math.max(20, this.resizeData.startWidth - dx)
        elem.x = this.resizeData.startXPos + dx
      }
      if (dir.includes('s')) {
        elem.height = Math.max(20, this.resizeData.startHeight + dy)
      }
      if (dir.includes('n')) {
        elem.height = Math.max(20, this.resizeData.startHeight - dy)
        elem.y = this.resizeData.startYPos + dy
      }
    },

    startRotate(elem, e) {
      if (elem.locked) return
      this.isRotating = true
      const rect = e.target.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      this.rotateData = {
        element: elem,
        centerX,
        centerY,
        startAngle: Math.atan2(e.clientY - centerY, e.clientX - centerX) * 180 / Math.PI,
        startRotation: elem.rotation || 0
      }
      
      window.addEventListener('mousemove', this.handleGlobalMouseMove)
      window.addEventListener('mouseup', this.handleGlobalMouseUp)
    },

    handleRotate(e) {
      if (!this.rotateData) return
      
      const angle = Math.atan2(e.clientY - this.rotateData.centerY, e.clientX - this.rotateData.centerX) * 180 / Math.PI
      this.rotateData.element.rotation = this.rotateData.startRotation + (angle - this.rotateData.startAngle)
    },

    addTextElement() {
      const newElement = {
        id: 'text_' + Date.now(),
        element_type: 'text',
        name: '文字',
        content: '点击编辑文字',
        x: 100 + (this.scheme?.elements?.length || 0) * 20,
        y: 100 + (this.scheme?.elements?.length || 0) * 20,
        width: 200,
        height: 50,
        font_family: 'Arial',
        font_size: 32,
        font_weight: 'normal',
        color: '#000000',
        rotation: 0,
        opacity: 1,
        z_index: this.scheme?.elements?.length || 0,
        visible: true,
        locked: false
      }
      this.$emit('add-element', newElement)
    },

    deleteSelected() {
      if (!this.selectedElement) return
      if (!confirm('确定要删除这个元素吗？')) return
      
      this.$emit('delete-element', this.selectedElement.id)
      this.selectedElement = null
      this.saveToHistory()
    },

    toggleVisibility(elem) {
      elem.visible = !elem.visible
      this.emitUpdate()
    },

    toggleLock(elem) {
      elem.locked = !elem.locked
      this.emitUpdate()
    },

    moveLayer(delta) {
      if (!this.selectedElement) return
      const index = this.scheme.elements.findIndex(e => e.id === this.selectedElement.id)
      if (index === -1) return
      
      const newIndex = index + delta
      if (newIndex < 0 || newIndex >= this.scheme.elements.length) return
      
      const temp = this.scheme.elements[index].z_index
      this.scheme.elements[index].z_index = this.scheme.elements[newIndex].z_index
      this.scheme.elements[newIndex].z_index = temp
      
      this.emitUpdate()
    },

    sendToBack() {
      if (!this.selectedElement) return
      const minZ = Math.min(...this.scheme.elements.map(e => e.z_index || 0))
      this.selectedElement.z_index = minZ - 1
      this.emitUpdate()
    },

    bringToFront() {
      if (!this.selectedElement) return
      const maxZ = Math.max(...this.scheme.elements.map(e => e.z_index || 0))
      this.selectedElement.z_index = maxZ + 1
      this.emitUpdate()
    },

    emitUpdate() {
      this.$emit('update:elements', this.scheme.elements)
    },

    emitBackgroundUpdate() {
      this.$emit('update:background', this.background)
    },

    saveToHistory() {
      // 简化版历史记录
      const state = JSON.stringify(this.scheme.elements)
      this.history = this.history.slice(0, this.historyIndex + 1)
      this.history.push(state)
      this.historyIndex = this.history.length - 1
      
      // 限制历史记录长度
      if (this.history.length > 50) {
        this.history.shift()
        this.historyIndex--
      }
    },

    undo() {
      if (!this.canUndo) return
      this.historyIndex--
      const state = JSON.parse(this.history[this.historyIndex])
      this.$emit('update:elements', state)
    },

    redo() {
      if (!this.canRedo) return
      this.historyIndex++
      const state = JSON.parse(this.history[this.historyIndex])
      this.$emit('update:elements', state)
    },

    zoomIn() {
      this.zoom = Math.min(200, this.zoom + 10)
    },

    zoomOut() {
      this.zoom = Math.max(50, this.zoom - 10)
    },

    getElementIcon(type) {
      const icons = {
        'text': '📝',
        'sticker': '🎭',
        'image': '🖼️',
        'background': '🖼️'
      }
      return icons[type] || '🎨'
    }
  }
}
</script>

<style scoped>
.decorate-editor {
  display: flex;
  height: 100%;
  background: #f3f4f6;
}

/* 工具栏 */
.toolbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0 15px;
  gap: 15px;
  z-index: 100;
}

.toolbar-section {
  display: flex;
  gap: 5px;
  align-items: center;
  padding-right: 15px;
  border-right: 1px solid #e5e7eb;
}

.toolbar-section:last-child {
  border-right: none;
}

.tool-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 18px;
}

.tool-btn:hover {
  background: #f3f4f6;
}

.tool-btn.active {
  background: #e0e7ff;
  border-color: #4f46e5;
  color: #4f46e5;
}

.tool-btn.danger:hover {
  background: #fee2e2;
  color: #dc2626;
}

.tool-label {
  font-size: 10px;
  margin-top: 2px;
  color: #6b7280;
}

.zoom-level {
  font-size: 13px;
  color: #374151;
  min-width: 45px;
  text-align: center;
}

/* 画布区域 */
.canvas-container {
  flex: 1;
  overflow: auto;
  padding: 60px 20px 20px 20px;
  display: flex;
  justify-content: center;
}

.canvas {
  position: relative;
  width: 1920px;
  height: 1080px;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: transform 0.2s;
}

.canvas-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.canvas-element {
  position: absolute;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.canvas-element.selected {
  border-color: #4f46e5;
}

.element-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  user-select: none;
}

/* 控制点 */
.element-controls {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  pointer-events: none;
}

.control-point {
  position: absolute;
  width: 10px;
  height: 10px;
  background: white;
  border: 2px solid #4f46e5;
  border-radius: 50%;
  pointer-events: all;
  cursor: pointer;
}

.control-point.nw { top: 0; left: 0; cursor: nw-resize; }
.control-point.n { top: 0; left: 50%; transform: translateX(-50%); cursor: n-resize; }
.control-point.ne { top: 0; right: 0; cursor: ne-resize; }
.control-point.e { top: 50%; right: 0; transform: translateY(-50%); cursor: e-resize; }
.control-point.se { bottom: 0; right: 0; cursor: se-resize; }
.control-point.s { bottom: 0; left: 50%; transform: translateX(-50%); cursor: s-resize; }
.control-point.sw { bottom: 0; left: 0; cursor: sw-resize; }
.control-point.w { top: 50%; left: 0; transform: translateY(-50%); cursor: w-resize; }

.rotate-handle {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border: 2px solid #4f46e5;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  pointer-events: all;
  font-size: 12px;
}

.rotate-handle:active {
  cursor: grabbing;
}

.element-info {
  position: absolute;
  bottom: -25px;
  left: 0;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
}

.element-size {
  margin-left: 8px;
  opacity: 0.7;
}

/* 属性面板 */
.properties-panel {
  width: 280px;
  background: white;
  border-left: 1px solid #e5e7eb;
  overflow-y: auto;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h3 {
  font-size: 15px;
  color: #1a1a1a;
  margin: 0;
}

.panel-content {
  padding: 15px;
}

.panel-empty {
  padding: 30px 15px;
  text-align: center;
  color: #9ca3af;
}

.panel-empty .hint {
  font-size: 12px;
  margin-top: 10px;
  opacity: 0.7;
}

.property-group {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.property-group:last-child {
  border-bottom: none;
}

.property-group h4 {
  font-size: 13px;
  color: #374151;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.property-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 12px;
}

.property-row label {
  font-size: 12px;
  color: #6b7280;
}

.property-row input[type="text"],
.property-row input[type="number"],
.property-row select,
.property-row textarea {
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
}

.property-row-inline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}

.property-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.property-field label {
  font-size: 12px;
  color: #6b7280;
}

.property-field input {
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
}

.property-field input[type="range"] {
  padding: 0;
}

.property-field .unit {
  font-size: 11px;
  color: #9ca3af;
  margin-left: 5px;
}

.property-value {
  font-size: 13px;
  color: #1a1a1a;
  padding: 8px;
  background: #f9fafb;
  border-radius: 6px;
}

.color-picker {
  display: flex;
  gap: 8px;
  align-items: center;
}

.color-picker input[type="color"] {
  width: 40px;
  height: 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
}

.color-picker input[type="text"] {
  flex: 1;
}

.align-buttons {
  display: flex;
  gap: 5px;
}

.align-buttons button {
  flex: 1;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 12px;
}

.align-buttons button.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

.checkbox-row label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-row input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

.layer-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.btn-sm {
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.btn-sm:hover {
  background: #f3f4f6;
}

/* 元素列表面板 */
.elements-panel {
  width: 220px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.elements-panel .panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.elements-panel .panel-header h3 {
  font-size: 14px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f3f4f6;
}

.elements-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.element-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.element-list-item:hover {
  background: #f3f4f6;
}

.element-list-item.selected {
  background: #e0e7ff;
}

.element-icon {
  font-size: 16px;
}

.element-name {
  flex: 1;
  font-size: 13px;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.element-visibility {
  display: flex;
  gap: 4px;
}

.btn-icon-sm {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  padding: 2px;
  opacity: 0.6;
}

.btn-icon-sm:hover {
  opacity: 1;
}
</style>
