import { ref, watch, type Ref } from 'vue'

export function useCountUp(
  target: Ref<number>,
  options?: { duration?: number; decimals?: number }
) {
  const duration = options?.duration ?? 800
  const decimals = options?.decimals ?? 0
  const display = ref('0')

  let animFrame: number | null = null

  function animate(from: number, to: number) {
    if (animFrame) cancelAnimationFrame(animFrame)

    const startTime = performance.now()
    const diff = to - from

    function tick(now: number) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      // ease-out-expo
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      const current = from + diff * eased
      display.value = current.toFixed(decimals)

      if (progress < 1) {
        animFrame = requestAnimationFrame(tick)
      } else {
        display.value = to.toFixed(decimals)
        animFrame = null
      }
    }

    animFrame = requestAnimationFrame(tick)
  }

  watch(
    target,
    (newVal, oldVal) => {
      const from = oldVal ?? 0
      animate(from, newVal)
    },
    { immediate: true }
  )

  return display
}
