import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PropsWithChildren,
} from 'react'
import { announce } from '../a11y/announcer'
import type { AnnounceChannel } from '../a11y/announcer'
import type { Preferences } from '../a11y/preferences'
import { useSettings } from '../ui/settings-context'

interface TtsContextValue {
  supportsSpeech: boolean
  enabled: boolean
  toggle: () => void
  setEnabled: (value: boolean) => void
  speakIfAllowed: (text: string, channel?: AnnounceChannel) => void
  stop: () => void
  voices: SpeechSynthesisVoice[]
  selectedVoice: SpeechSynthesisVoice | null
  selectVoice: (voiceURI: string | null) => void
  cycleVoice: (direction?: 1 | -1) => void
  rate: number
  setRate: (value: number) => void
  adjustRate: (delta: number) => void
  testVoice: (text?: string) => void
  lastUtterance: string | null
}

const TtsContext = createContext<TtsContextValue | undefined>(undefined)

const MIN_RATE = 0.5
const MAX_RATE = 2
const RATE_STEP = 0.1
const DEFAULT_TEST_UTTERANCE = 'Testing voice output.'

export function TtsProvider({ children }: PropsWithChildren) {
  const {
    preferences: { ttsEnabled, voiceURI, rate, screenReaderUser },
    updatePreferences,
  } = useSettings()

  const supportsSpeech = useMemo(
    () => typeof window !== 'undefined' && 'speechSynthesis' in window,
    [],
  )

  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [lastUtterance, setLastUtterance] = useState<string | null>(null)
  const resolvedVoice = useMemo(() => {
    if (!supportsSpeech) {
      return null
    }
    if (voiceURI) {
      return voices.find((voice) => voice.voiceURI === voiceURI) ?? null
    }
    return voices[0] ?? null
  }, [supportsSpeech, voiceURI, voices])

  useEffect(() => {
    if (!supportsSpeech) {
      return
    }
    const synthesis = window.speechSynthesis

    const syncVoices = () => {
      const current = synthesis.getVoices()
      setVoices(current)
    }

    syncVoices()

    synthesis.addEventListener('voiceschanged', syncVoices)

    if (synthesis.getVoices().length === 0) {
      window.setTimeout(syncVoices, 300)
    }

    return () => {
      synthesis.removeEventListener('voiceschanged', syncVoices)
    }
  }, [supportsSpeech])

  const enabled = supportsSpeech && !!ttsEnabled && screenReaderUser !== true

  const setEnabled = useCallback<TtsContextValue['setEnabled']>(
    (next) => {
      updatePreferences({ ttsEnabled: next })
    },
    [updatePreferences],
  )

  const toggle = useCallback(() => {
    setEnabled(!enabled)
  }, [enabled, setEnabled])

  const speakWithVoice = useCallback(
    (utteranceText: string) => {
      if (!supportsSpeech) {
        return
      }
      const synthesis = window.speechSynthesis
      synthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(utteranceText)
      utterance.rate = rate
      const voice = resolvedVoice
      if (voice) {
        utterance.voice = voice
        utterance.lang = voice.lang
      }
      setLastUtterance(utteranceText)
      synthesis.speak(utterance)
    },
    [resolvedVoice, rate, supportsSpeech],
  )

  const speakIfAllowed = useCallback<TtsContextValue['speakIfAllowed']>(
    (text, channel = 'alerts') => {
      if (!enabled) {
        return
      }
      if (!text.trim()) {
        return
      }
      // Alerts should interrupt, statuses can be queued softly.
      if (channel === 'alerts') {
        speakWithVoice(text.trim())
      } else {
        if (!supportsSpeech) {
          return
        }
        const synthesis = window.speechSynthesis
        const utterance = new SpeechSynthesisUtterance(text.trim())
        utterance.rate = rate
        const voice = resolvedVoice
        if (voice) {
          utterance.voice = voice
          utterance.lang = voice.lang
        }
        setLastUtterance(text.trim())
        synthesis.speak(utterance)
      }
    },
    [enabled, rate, resolvedVoice, speakWithVoice, supportsSpeech],
  )

  const stop = useCallback(() => {
    if (!supportsSpeech) {
      return
    }
    window.speechSynthesis.cancel()
  }, [supportsSpeech])

  const selectVoice = useCallback<TtsContextValue['selectVoice']>(
    (nextVoiceURI) => {
      updatePreferences({ voiceURI: nextVoiceURI })
      if (nextVoiceURI) {
        announce(`Voice set to ${nextVoiceURI}`, 'status')
      }
    },
    [updatePreferences],
  )

  const cycleVoice = useCallback<TtsContextValue['cycleVoice']>(
    (direction = 1) => {
      if (!voices.length) {
        announce('No alternate voice available.', 'status')
        return
      }
      const currentIndex = voices.findIndex((voice) => voice.voiceURI === resolvedVoice?.voiceURI)
      const nextIndex = currentIndex === -1 ? 0 : (currentIndex + direction + voices.length) % voices.length
      const nextVoice = voices[nextIndex]
      selectVoice(nextVoice?.voiceURI ?? null)
    },
    [voices, resolvedVoice, selectVoice],
  )

  const setRateValue = useCallback<TtsContextValue['setRate']>(
    (value) => {
      const clamped = Number.isFinite(value) ? Math.min(MAX_RATE, Math.max(MIN_RATE, value)) : 1
      updatePreferences({ rate: Number(clamped.toFixed(2)) as Preferences['rate'] })
      announce(`Speech rate set to ${clamped.toFixed(1)}`, 'status')
    },
    [updatePreferences],
  )

  const adjustRate = useCallback<TtsContextValue['adjustRate']>(
    (delta) => {
      setRateValue(rate + delta)
    },
    [rate, setRateValue],
  )

  const testVoice = useCallback<TtsContextValue['testVoice']>(
    (message = DEFAULT_TEST_UTTERANCE) => {
      if (!enabled) {
        announce('Enable text to speech to test the voice.', 'status')
        return
      }
      speakWithVoice(message)
    },
    [enabled, speakWithVoice],
  )

  const value = useMemo<TtsContextValue>(
    () => ({
      supportsSpeech,
      enabled,
      toggle,
      setEnabled,
      speakIfAllowed,
      stop,
      voices,
      selectedVoice: resolvedVoice,
      selectVoice,
      cycleVoice,
      rate,
      setRate: setRateValue,
      adjustRate,
      testVoice,
      lastUtterance,
    }),
    [
      supportsSpeech,
      enabled,
      toggle,
      setEnabled,
      speakIfAllowed,
      stop,
      voices,
      resolvedVoice,
      selectVoice,
      cycleVoice,
      rate,
      setRateValue,
      adjustRate,
      testVoice,
      lastUtterance,
    ],
  )

  return <TtsContext.Provider value={value}>{children}</TtsContext.Provider>
}

export function useTts() {
  const context = useContext(TtsContext)
  if (!context) {
    throw new Error('useTts must be used inside TtsProvider')
  }
  return context
}
