import { watch, type Ref, onMounted } from 'vue'

export function useStagger(
  containerRef: Ref<HTMLElement | null>,
  options?: { delay?: number; selector?: string }
) {
  const delay = options?.delay ?? 60
  const selector = options?.selector ?? '> *'

  function apply() {
    const el = containerRef.value
    if (!el) return
    const children = el.querySelectorAll(selector)
    children.forEach((child, i) => {
      (child as HTMLElement).style.transitionDelay = `${i * delay}ms`
    })
  }

  onMounted(apply)
  watch(containerRef, apply)
}
