<template>
  <div class="lazy-image-container" :style="containerStyle">
    <img
      ref="imgRef"
      :src="currentSrc"
      :alt="alt"
      :class="['lazy-image', imageClass]"
      :style="imageStyle"
      loading="lazy"
      @load="handleLoad"
      @error="handleError"
    />
    <div v-if="showPlaceholder && !isLoaded" class="lazy-placeholder">
      <slot name="placeholder">
        <div class="default-placeholder">
          <span class="placeholder-icon">🖼️</span>
        </div>
      </slot>
    </div>
    <div v-if="isLoading && showLoading" class="lazy-loading">
      <slot name="loading">
        <div class="default-loading">
          <div class="loading-spinner"></div>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  src: string
  alt?: string
  width?: string | number
  height?: string | number
  placeholder?: string
  showPlaceholder?: boolean
  showLoading?: boolean
  imageClass?: string
  threshold?: number
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  showPlaceholder: true,
  showLoading: true,
  threshold: 0.1,
})

const imgRef = ref<HTMLImageElement | null>(null)
const isLoaded = ref(false)
const isLoading = ref(false)
const currentSrc = ref(props.placeholder || '')

const containerStyle = computed(() => ({
  width: props.width ? (typeof props.width === 'number' ? `${props.width}px` : props.width) : '100%',
  height: props.height ? (typeof props.height === 'number' ? `${props.height}px` : props.height) : 'auto',
}))

const imageStyle = computed(() => ({
  opacity: isLoaded.value ? 1 : 0,
}))

let observer: IntersectionObserver | null = null

const handleLoad = () => {
  isLoaded.value = true
  isLoading.value = false
}

const handleError = () => {
  isLoading.value = false
  currentSrc.value = props.placeholder || ''
}

const loadImage = () => {
  if (isLoading.value || isLoaded.value) return
  
  isLoading.value = true
  currentSrc.value = props.src
}

onMounted(() => {
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage()
            if (observer && imgRef.value) {
              observer.unobserve(imgRef.value)
            }
          }
        })
      },
      {
        rootMargin: '50px',
        threshold: props.threshold,
      }
    )
    
    if (imgRef.value) {
      observer.observe(imgRef.value)
    } else {
      // 如果没有 imgRef，直接加载
      loadImage()
    }
  } else {
    // 不支持 IntersectionObserver，直接加载
    loadImage()
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.lazy-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.lazy-placeholder,
.lazy-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-light);
}

.default-placeholder,
.default-loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 2rem;
  opacity: 0.5;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--el-fill-color);
  border-top-color: var(--el-color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
