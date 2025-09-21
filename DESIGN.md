# KeyQuest  Design Specification

An accessible, screen-reader-first, turn-based typing adventure game.

## Accessibility Foundations
- **Primary audience:** Blind and visually impaired users, but also usable by sighted players.
- **WCAG compliance:** Target WCAG 2.1 AA.
- **Screen Reader First:** If a user is already running JAWS/NVDA/VoiceOver, rely on ARIA live regions only (no extra speech).
- **Fallback Speech:** If no screen reader is detected, use Web Speech Synthesis for TTS (toggleable).
- **High Contrast by default:** Toggle available (`Ctrl+V`). Provide visible focus outlines and sufficient color contrast.
- **ARIA live regions:**
  - `#alerts`: role=alert, aria-live=assertive, aria-atomic=true (urgent/important).
  - `#status`: role=status, aria-live=polite, aria-atomic=true (non-urgent status).
- **Announce helper:** `announce(text, channel)` updates the correct live region (clear  set so SR re-reads) and, when TTS mode is ON, uses Web Speech (cancel before speak).
- **Focus management:** Dialogs are focus-trapped and restore focus on close; logical focus order across app.
- **Keyboard only:** All interactions possible by keyboard alone.

## Hotkeys
_All hotkeys are disabled during typing drills._
- `Ctrl+M`  Toggle TTS on/off  alert Speech muted/unmuted
- `Ctrl+R`  Repeat last alert (alerts channel)
- `Ctrl+T`  Status summary (status channel)
- `Ctrl+V`  Toggle theme (High Contrast  Standard)  alert Theme set to 
- `Ctrl+Shift+M`  Open TTS Settings modal
- `Ctrl+Shift+V`  Cycle voices  status Voice i of N: <name>
- `Ctrl+Shift+=` / `Ctrl+Shift+-`  Increase/decrease rate (0.701.50, step 0.05)  status Rate X.XX
- `F1`  Context help; `Esc`  Close/back/pause

## TTS Settings Modal
- **Dialog:** role=dialog, aria-modal=true; focus is trapped; return focus on close.
- **Voices:** role=listbox + role=option items; keyboard navigation Up/Down/Home/End; `aria-activedescendant`.
- **Rate:** `<input type="range">` 0.701.50 step 0.05 with `aria-valuetext="Rate X.XX"`.
- **Buttons:** Test (speaks sample), Save (persist), Cancel (revert).
- **Announcements:** Open/close/save  alerts; selection/adjustment  status.
- **Persistence:** IndexedDB with localStorage fallback.

## Game Flow
- **Turn-based exploration** (no real-time pressure for choices).
- **Typing drills** are timed/graded; story choices are untimed.
- **Onboarding Q&A** (1/2/3 options) builds a deterministic seed string.
- **Procedural content:** Use a deterministic PRNG (e.g., Mulberry32) with the seed.
- **Stub story turn:** MVP includes one explore turn that would lead into a drill (placeholder only).
- **Progress tracking:** Store SR/TTS settings, theme, seed, and progress in IndexedDB/localStorage; cookie optional for a profile key.
- **Certification:** On proficiency (30 WPM and 90100% accuracy), allow printable/emailable certificate.

## Technical Stack
- React + TypeScript + Vite in `/app`.
- PWA (vite-plugin-pwa, manifest, service worker; offline-ready).
- ESLint, Prettier, EditorConfig.
- GitHub Actions CI: install, typecheck (if added), build, placeholder Playwright a11y test.

## WCAG References
- 1.3.1 Info and Relationships; 1.4.3 Contrast (Minimum); 1.4.11 Non-text Contrast
- 2.1.1 Keyboard; 2.1.2 No Keyboard Trap; 2.2.2 Pause, Stop, Hide
- 2.4.3 Focus Order; 2.4.6 Headings and Labels; 2.4.7 Focus Visible
- 3.3.1 Error Identification; 3.3.3 Error Suggestion
- 4.1.2 Name, Role, Value
