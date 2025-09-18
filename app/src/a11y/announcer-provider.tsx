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
import { announce as externalAnnounce, setAnnouncer, type AnnounceChannel } from './announcer'
import { useTts } from '../tts/tts-context'

interface AnnouncerContextValue {
  announce: (text: string, channel?: AnnounceChannel) => void
  repeat: (channel: AnnounceChannel) => void
  lastMessages: Record<AnnounceChannel, string>
}

const AnnouncerContext = createContext<AnnouncerContextValue | undefined>(undefined)

const LIVE_REGION_IDS: Record<AnnounceChannel, string> = {
  alerts: 'alerts',
  status: 'status',
}

const ANNOUNCE_DELAY_MS = 90

export function AnnouncerProvider({ children }: PropsWithChildren) {
  const { speakIfAllowed } = useTts()
  const [lastMessages, setLastMessages] = useState<Record<AnnounceChannel, string>>({
    alerts: '',
    status: '',
  })

  const timers = useRef<Record<AnnounceChannel, number | null>>({
    alerts: null,
    status: null,
  })

  const writeToLiveRegion = useCallback((channel: AnnounceChannel, message: string) => {
    if (typeof window === 'undefined') {
      return
    }
    const region = document.getElementById(LIVE_REGION_IDS[channel])
    if (!region) {
      return
    }
    region.textContent = ''
    window.setTimeout(() => {
      region.textContent = message
    }, 10)
  }, [])

  const handleAnnounce = useCallback(
    (rawText: string, channel: AnnounceChannel = 'status') => {
      const text = rawText?.trim()
      if (!text) {
        return
      }

      setLastMessages((current) => ({ ...current, [channel]: text }))

      if (timers.current[channel]) {
        window.clearTimeout(timers.current[channel] ?? undefined)
      }

      timers.current[channel] = window.setTimeout(() => {
        writeToLiveRegion(channel, text)
        speakIfAllowed(text, channel)
      }, ANNOUNCE_DELAY_MS)
    },
    [speakIfAllowed, writeToLiveRegion],
  )

  useEffect(() => {
    setAnnouncer((text, channel = 'status') => {
      handleAnnounce(text, channel)
    })
  }, [handleAnnounce])

  useEffect(() => {
    return () => {
      (Object.keys(timers.current) as AnnounceChannel[]).forEach((channel) => {
        if (timers.current[channel]) {
          window.clearTimeout(timers.current[channel] ?? undefined)
        }
      })
    }
  }, [])

  const repeat = useCallback<AnnouncerContextValue['repeat']>(
    (channel) => {
      const message = lastMessages[channel]
      if (!message) {
        externalAnnounce('No message to repeat yet.', 'status')
        return
      }
      handleAnnounce(message, channel)
    },
    [handleAnnounce, lastMessages],
  )

  const value = useMemo<AnnouncerContextValue>(
    () => ({ announce: handleAnnounce, repeat, lastMessages }),
    [handleAnnounce, repeat, lastMessages],
  )

  return <AnnouncerContext.Provider value={value}>{children}</AnnouncerContext.Provider>
}

export function useAnnouncer() {
  const context = useContext(AnnouncerContext)
  if (!context) {
    throw new Error('useAnnouncer must be used within AnnouncerProvider')
  }
  return context
}

export function useLastAnnouncement(channel: AnnounceChannel) {
  const { lastMessages } = useAnnouncer()
  return lastMessages[channel]
}

export function useRepeatAnnouncement() {
  const { repeat } = useAnnouncer()
  return repeat
}

export function useAnnounce() {
  const { announce: announceFn } = useAnnouncer()
  return announceFn
}
