import { useEffect, useMemo, useState } from 'react'
import { announce } from '../a11y/announcer'
import { useAnnounce } from '../a11y/announcer-provider'
import { createExplorePreview } from '../game/explore'
import type { Preferences } from '../a11y/preferences'
import { useSettings } from './settings-context'

const SEEDS: Array<{ id: string; label: string; description: string }> = [
  { id: 'NAV-1', label: 'Pathfinder 1', description: 'Prioritise steady pacing and safe shortcuts.' },
  { id: 'NAV-2', label: 'Pathfinder 2', description: 'Favour bold routes with tight timing.' },
  { id: 'NAV-3', label: 'Pathfinder 3', description: 'Balanced tempo with room for reflection.' },
]

type OnboardingStep = 'screenReader' | 'seed' | 'summary'

interface OnboardingProps {
  onComplete: () => void
}

export function Onboarding({ onComplete }: OnboardingProps) {
  const {
    preferences: { screenReaderUser, seed },
    updatePreferences,
  } = useSettings()
  const announceFn = useAnnounce()
  const [step, setStep] = useState<OnboardingStep>('screenReader')
  const [localSeed, setLocalSeed] = useState<string | null>(seed)

  useEffect(() => {
    announceFn('Welcome to KeyQuest setup. Answer a quick question to continue.', 'status')
  }, [announceFn])

  useEffect(() => {
    if (step === 'screenReader') {
      announceFn('Do you use a screen reader? Choose yes or no.', 'status')
    }
    if (step === 'seed') {
      announceFn('Select a pathfinder seed. Options one, two, or three.', 'status')
    }
    if (step === 'summary' && localSeed) {
      announceFn('Seed captured. Review the mission summary and continue.', 'status')
    }
  }, [announceFn, localSeed, step])

  const preview = useMemo(() => {
    if (!localSeed) {
      return null
    }
    return createExplorePreview(localSeed)
  }, [localSeed])

  const handleScreenReaderChoice = (usesScreenReader: boolean) => {
    const nextPrefs: Partial<Preferences> = {
      screenReaderUser: usesScreenReader,
      ttsEnabled: usesScreenReader ? false : true,
    }
    updatePreferences(nextPrefs)
    announce(`Screen reader preference set to ${usesScreenReader ? 'enabled' : 'disabled'}.`, 'status')
    setStep('seed')
  }

  const handleSeedChoice = (value: string) => {
    setLocalSeed(value)
    updatePreferences({ seed: value })
    announce(`Seed ${value} selected.`, 'status')
    setStep('summary')
  }

  const handleFinish = () => {
    announce('Setup complete. Ready to explore.', 'alerts')
    onComplete()
  }

  return (
    <section aria-labelledby="onboarding-title" className="panel" role="region">
      <header>
        <h2 id="onboarding-title">First-time setup</h2>
        <p>Answer these steps once to tune accessibility.</p>
      </header>

      {step === 'screenReader' && (
        <div role="group" aria-labelledby="screen-reader-prompt">
          <p id="screen-reader-prompt">Do you use a screen reader while playing?</p>
          <div className="button-grid">
            <button type="button" onClick={() => handleScreenReaderChoice(true)}>
              Yes, keep speech off
            </button>
            <button type="button" onClick={() => handleScreenReaderChoice(false)}>
              No, enable training speech
            </button>
          </div>
        </div>
      )}

      {step === 'seed' && (
        <div role="group" aria-labelledby="seed-prompt">
          <p id="seed-prompt">Select a pathfinder seed (press 1, 2, or 3).</p>
          <ol className="seed-list">
            {SEEDS.map((option, index) => (
              <li key={option.id}>
                <button
                  type="button"
                  aria-pressed={localSeed === option.id}
                  onClick={() => handleSeedChoice(option.id)}
                >
                  <span className="seed-index">{index + 1}.</span> {option.label}
                  <span className="seed-description">{option.description}</span>
                </button>
              </li>
            ))}
          </ol>
        </div>
      )}

      {step === 'summary' && preview && (
        <div role="group" aria-labelledby="summary-title">
          <h3 id="summary-title">Mission preview</h3>
          <p>
            Destination: <strong>{preview.location}</strong>
          </p>
          <p>Objective: {preview.objective}</p>
          <p>{preview.drillHint}</p>
          <button type="button" onClick={handleFinish}>
            Continue to command deck
          </button>
        </div>
      )}
    </section>
  )
}
