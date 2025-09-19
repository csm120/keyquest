import { hashSeed, mulberry32 } from './prng'

export interface ExplorePreview {
  location: string
  objective: string
  drillHint: string
}

const LOCATIONS = ['Signal Archive', 'Crystal Vault', 'Echo Library']
const OBJECTIVES = [
  'map the safe paths',
  'catalogue the guard rotations',
  'decode the gate glyphs',
]
const HINTS = [
  'A precision typing drill will follow in the next session.',
  'Prepare for a rhythm drill soon.',
  'Expect a focus drill once exploration continues.',
]

export function createExplorePreview(seed: string): ExplorePreview {
  const rng = mulberry32(hashSeed(seed))
  const pick = <T>(items: T[]): T => items[Math.floor(rng() * items.length)]

  return {
    location: pick(LOCATIONS),
    objective: pick(OBJECTIVES),
    drillHint: pick(HINTS),
  }
}
