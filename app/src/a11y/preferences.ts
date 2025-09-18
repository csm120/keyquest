export type ThemeChoice = 'high-contrast' | 'standard'

export interface Preferences {
  screenReaderUser: boolean | null
  ttsEnabled: boolean
  theme: ThemeChoice
  voiceURI: string | null
  rate: number
  seed: string | null
}

export const PREFERENCE_VERSION = 1

export const DEFAULT_PREFERENCES: Preferences = {
  screenReaderUser: null,
  ttsEnabled: false,
  theme: 'high-contrast',
  voiceURI: null,
  rate: 1,
  seed: null,
}
