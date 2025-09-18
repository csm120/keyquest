import { useEffect } from 'react'
import { announce } from '../a11y/announcer'
import { useAnnouncer } from '../a11y/announcer-provider'
import { useTts } from '../tts/tts-context'

export interface HotkeyOptions {
  disabled?: boolean
  onToggleTheme: () => void
  onOpenTtsModal: () => void
  onClose?: () => void
  onOpenHelp: () => void
  getStatusSummary: () => string
}

const EDITABLE_TAGS = new Set(['INPUT', 'TEXTAREA'])

export function useGlobalHotkeys({
  disabled,
  onToggleTheme,
  onOpenTtsModal,
  onClose,
  onOpenHelp,
  getStatusSummary,
}: HotkeyOptions) {
  const { repeat } = useAnnouncer()
  const { enabled, toggle, supportsSpeech, cycleVoice, adjustRate } = useTts()

  useEffect(() => {
    if (disabled) {
      return
    }

    const handler = (event: KeyboardEvent) => {
      if (event.repeat) {
        return
      }
      const target = event.target as HTMLElement | null
      if (target) {
        const tagName = target.tagName
        const isEditable =
          EDITABLE_TAGS.has(tagName) ||
          target.isContentEditable ||
          (tagName === 'DIV' && target.getAttribute('role') === 'textbox')
        if (isEditable) {
          return
        }
      }

      if (event.key === 'F1') {
        event.preventDefault()
        onOpenHelp()
        return
      }

      if (event.key === 'Escape') {
        if (onClose) {
          event.preventDefault()
          onClose()
        }
        return
      }

      const ctrl = event.ctrlKey || event.metaKey
      const shift = event.shiftKey

      if (!ctrl) {
        return
      }

      switch (event.key) {
        case 'M':
        case 'm': {
          if (shift) {
            event.preventDefault()
            if (!supportsSpeech) {
              announce('Text to speech is not available in this browser.', 'status')
              return
            }
            onOpenTtsModal()
          } else {
            event.preventDefault()
            if (!supportsSpeech) {
              announce('Text to speech is not available.', 'status')
              return
            }
            toggle()
            announce(`Text to speech ${enabled ? 'disabled' : 'enabled'}.`, 'status')
          }
          return
        }
        case 'R':
        case 'r': {
          event.preventDefault()
          repeat('alerts')
          return
        }
        case 'T':
        case 't': {
          event.preventDefault()
          const summary = getStatusSummary()
          announce(summary, 'status')
          return
        }
        case 'V':
        case 'v': {
          event.preventDefault()
          if (shift) {
            if (!supportsSpeech) {
              announce('No alternate voice available.', 'status')
              return
            }
            cycleVoice()
          } else {
            onToggleTheme()
          }
          return
        }
        case '=':
        case '+': {
          if (shift && supportsSpeech) {
            event.preventDefault()
            adjustRate(0.1)
          }
          return
        }
        case '-':
        case '_': {
          if (shift && supportsSpeech) {
            event.preventDefault()
            adjustRate(-0.1)
          }
          return
        }
      }
    }

    window.addEventListener('keydown', handler)
    return () => {
      window.removeEventListener('keydown', handler)
    }
  }, [
    disabled,
    onOpenHelp,
    onClose,
    onOpenTtsModal,
    onToggleTheme,
    getStatusSummary,
    repeat,
    supportsSpeech,
    toggle,
    enabled,
    cycleVoice,
    adjustRate,
  ])
}
