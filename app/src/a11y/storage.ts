import { DEFAULT_PREFERENCES, PREFERENCE_VERSION, type Preferences } from './preferences'

const STORAGE_KEY = 'keyquest.preferences.v1'

type StoredPreferences = Preferences & { version: number }

const isBrowser = typeof window !== 'undefined'

export async function loadPreferences(): Promise<StoredPreferences> {
  if (!isBrowser) {
    return withVersion(DEFAULT_PREFERENCES)
  }

  const local = readFromLocalStorage()

  if ('indexedDB' in window) {
    try {
      const { get } = await import('idb-keyval')
      const fromIdb = (await get<StoredPreferences | undefined>(STORAGE_KEY)) ?? undefined
      if (fromIdb) {
        return normalise(fromIdb)
      }
    } catch (error) {
      console.warn(
        'KeyQuest preferences: IndexedDB read failed, falling back to localStorage.',
        error,
      )
    }
  }

  if (local) {
    return normalise(local)
  }

  return withVersion(DEFAULT_PREFERENCES)
}

export async function savePreferences(prefs: StoredPreferences): Promise<void> {
  if (!isBrowser) {
    return
  }

  const serialised = JSON.stringify(normalise(prefs))

  try {
    window.localStorage.setItem(STORAGE_KEY, serialised)
  } catch (error) {
    console.warn('KeyQuest preferences: localStorage write failed.', error)
  }

  if ('indexedDB' in window) {
    try {
      const { set } = await import('idb-keyval')
      await set(STORAGE_KEY, normalise(prefs))
    } catch (error) {
      console.warn('KeyQuest preferences: IndexedDB write failed.', error)
    }
  }
}

export function getDefaultPreferences(): StoredPreferences {
  return withVersion(DEFAULT_PREFERENCES)
}

function withVersion(prefs: Preferences): StoredPreferences {
  return { ...prefs, version: PREFERENCE_VERSION }
}

function readFromLocalStorage(): StoredPreferences | null {
  try {
    if (!isBrowser) {
      return null
    }
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return null
    }
    return JSON.parse(raw) as StoredPreferences
  } catch (error) {
    console.warn('KeyQuest preferences: localStorage read failed.', error)
    return null
  }
}

function normalise(input: StoredPreferences): StoredPreferences {
  return {
    ...withVersion(DEFAULT_PREFERENCES),
    ...input,
    version: PREFERENCE_VERSION,
  }
}
