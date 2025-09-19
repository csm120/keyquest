import {
  useCallback,
  useEffect,
  useRef,
  type PropsWithChildren,
  type RefObject,
} from 'react'

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'area[href]',
  'button:not([disabled])',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

interface FocusTrapProps extends PropsWithChildren {
  active: boolean
  returnFocus?: boolean
  initialFocusRef?: RefObject<HTMLElement>
  onEscape?: () => void
}

export function FocusTrap({
  active,
  returnFocus = true,
  initialFocusRef,
  onEscape,
  children,
}: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const previousFocus = useRef<HTMLElement | null>(null)

  const moveFocus = useCallback(() => {
    const root = containerRef.current
    if (!root) {
      return
    }
    const focusTarget =
      initialFocusRef?.current ??
      (root.querySelector(FOCUSABLE_SELECTOR) as HTMLElement | null)
    focusTarget?.focus()
  }, [initialFocusRef])

  useEffect(() => {
    if (!active) {
      return
    }
    if (typeof window === 'undefined') {
      return
    }
    previousFocus.current = document.activeElement as HTMLElement | null
    moveFocus()

    const handleKeyDown = (event: KeyboardEvent) => {
      if (!containerRef.current) {
        return
      }
      if (event.key === 'Escape') {
        event.stopPropagation()
        event.preventDefault()
        onEscape?.()
        return
      }
      if (event.key !== 'Tab') {
        return
      }

      const focusable = Array.from(
        containerRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
      ).filter(
        (element) => element.offsetParent !== null || element === document.activeElement,
      )

      if (focusable.length === 0) {
        event.preventDefault()
        containerRef.current.focus()
        return
      }

      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      const current = document.activeElement as HTMLElement | null
      if (event.shiftKey) {
        if (current === first || current === containerRef.current) {
          event.preventDefault()
          last.focus()
        }
        return
      }
      if (current === last) {
        event.preventDefault()
        first.focus()
      }
    }

    const node = containerRef.current
    node?.addEventListener('keydown', handleKeyDown, true)

    return () => {
      node?.removeEventListener('keydown', handleKeyDown, true)
      if (returnFocus && previousFocus.current) {
        previousFocus.current.focus()
      }
    }
  }, [active, moveFocus, onEscape, returnFocus])

  return (
    <div ref={containerRef} tabIndex={-1}>
      {children}
    </div>
  )
}
