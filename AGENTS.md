# Repository Guidelines

## Project Structure & Module Organization
- Root keeps `index.html`, `DESIGN.md`, and CI config; the TypeScript app lives in `app/`.
- `app/src` houses React modules: `a11y/` for accessibility helpers, `game/` for core logic, `input/` for keyboard handling, `tts/` for speech, and `ui/` for composite views.
- `app/public` stores PWA assets (icons, `manifest.webmanifest`); build artifacts emit to `app/dist`.
- Automation lives in `.github/workflows`; align changes with `DESIGN.md` for feature context.

## Build, Test, and Development Commands
Run commands from `app/`:
- `npm install` - install or refresh dependencies.
- `npm run dev` - start the Vite dev server with hot reloading.
- `npm run build` - type-check, then emit production assets to `dist`.
- `npm run preview` - serve the built bundle locally.
- `npm run lint`, `npm run lint:fix`, `npm run typecheck` - enforce ESLint and TypeScript rules; `lint:fix` applies safe fixes.
- `npm run test`, `npm run test:watch` - execute Vitest suites once or in watch mode.

## Coding Style & Naming Conventions
- `.editorconfig` enforces LF endings, UTF-8, and two-space indentation; avoid committing trailing whitespace.
- Prettier config (`.prettierrc.json`) sets single quotes, no semicolons, 90 character width, and trailing commas; run `npm run lint:fix` before pushing.
- React components and hooks stay in PascalCase (see `app/src/ui/Onboarding.tsx`); utilities use camelCase or kebab-case modules (for example `app/src/a11y/focus-trap.tsx`).
- Keep accessibility and TTS helpers with their contexts; prefer named exports for shared utilities.

## Testing Guidelines
- Vitest with Testing Library drives unit and UI tests; colocate specs as `*.test.ts[x]` near the module or under `src/__tests__/`.
- Mock browser-only APIs such as `idb-keyval` and `speechSynthesis` to keep runs deterministic.
- Target meaningful coverage on new logic, especially inside `src/game/` and `src/a11y/`; confirm `npm run lint` and `npm run test` pass.

## Commit & Pull Request Guidelines
- Use Conventional Commit prefixes (`ci:`, `docs:`, `chore:`) as in history; keep subjects imperative and under 72 characters.
- Reference issues in footers when relevant (`Refs #123`) and describe behavioral impact in the PR body.
- Attach screenshots or recordings for UI changes and note accessibility or keyboard considerations.
- Confirm CI status locally (`npm run build`, `npm run test`) and record the executed commands in the PR checklist.

## Accessibility & TTS Notes
- Review `DESIGN.md` before altering interaction flows; verify screen reader announcements via `app/src/a11y/announcer-provider.tsx`.
- Gate audio cues through the TTS context so Silent Mode remains respected, and document new preferences in `app/src/a11y/preferences.ts`.
