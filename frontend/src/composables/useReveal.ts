import { onUnmounted } from 'vue'

let observer: IntersectionObserver | null = null
const elements = new WeakMap<HTMLElement, boolean>()

function getObserver(rootMargin: string): IntersectionObserver {
  if (observer) return observer

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          const once = elements.get(entry.target as HTMLElement)
          if (once) {
            observer!.unobserve(entry.target)
            elements.delete(entry.target as HTMLElement)
          }
        }
      })
    },
    { rootMargin }
  )

  return observer
}

export function useReveal(options?: { rootMargin?: string; once?: boolean }) {
  const rootMargin = options?.rootMargin ?? '0px 0px -40px 0px'
  const once = options?.once ?? true

  function observe(el: HTMLElement) {
    if (!el) return
    // If IntersectionObserver not available (test env), mark visible immediately
    if (typeof IntersectionObserver === 'undefined') {
      el.classList.add('is-visible')
      return
    }
    const obs = getObserver(rootMargin)
    elements.set(el, once)
    obs.observe(el)
  }

  function unobserve(el: HTMLElement) {
    if (!el || !observer) return
    observer.unobserve(el)
    elements.delete(el)
  }

  onUnmounted(() => {
    // Note: we don't disconnect the shared observer on each component unmount
    // It lives for the app lifetime
  })

  return { observe, unobserve }
}
