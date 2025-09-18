import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type PropsWithChildren } from 'react'
import { DEFAULT_PREFERENCES, PREFERENCE_VERSION, type Preferences } from '../a11y/preferences'
import { loadPreferences, savePreferences } from '../a11y/storage'

interface SettingsContextValue {
  ready: boolean
  preferences: Preferences
  updatePreferences: (updater: Partial<Preferences> | ((current: Preferences) => Partial<Preferences>)) => void
}

const SettingsContext = createContext<SettingsContextValue | undefined>(undefined)

const SAVE_DEBOUNCE_MS = 200

export function SettingsProvider({ children }: PropsWithChildren) {
  const [ready, setReady] = useState(false)
  const [preferences, setPreferences] = useState<Preferences>(DEFAULT_PREFERENCES)
  const saveTimer = useRef<number | null>(null)

  useEffect(() => {
    let active = true
    loadPreferences().then((stored) => {
      if (!active) {
        return
      }
      const { version: _version, ...rest } = stored
      setPreferences(rest)
      setReady(true)
    })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!ready) {
      return
    }
    if (typeof window === 'undefined') {
      return
    }

    if (saveTimer.current) {
      window.clearTimeout(saveTimer.current)
    }

    saveTimer.current = window.setTimeout(() => {
      void savePreferences({ ...preferences, version: PREFERENCE_VERSION })
    }, SAVE_DEBOUNCE_MS)

    return () => {
      if (saveTimer.current) {
        window.clearTimeout(saveTimer.current)
      }
    }
  }, [preferences, ready])

  const updatePreferences = useCallback<SettingsContextValue['updatePreferences']>((updater) => {
    setPreferences((current) => {
      const update = typeof updater === 'function' ? updater(current) : updater
      return { ...current, ...update }
    })
  }, [])

  const value = useMemo<SettingsContextValue>(
    () => ({ ready, preferences, updatePreferences }),
    [ready, preferences, updatePreferences],
  )

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error('useSettings must be used within SettingsProvider')
  }
  return context
}
