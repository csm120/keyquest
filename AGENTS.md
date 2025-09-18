# Repository Guidelines

## Project Structure & Module Organization
The root directory holds `index.html`, `DESIGN.md`, `AGENTS.md`, and CI configuration inside `.github/`. The production app lives in `app/`, with React source in `app/src`. Within `app/src`, `a11y/` hosts accessibility helpers, `game/` manages core state and rules, `input/` normalizes keyboard events, `tts/` wraps speech output, and `ui/` assembles screens. Public assets ship from `app/public`, while build artifacts land in `app/dist`. Place new tests beside their modules or inside `app/src/__tests__/`.

## Build, Test, and Development Commands
Run all scripts from the `app/` directory. Use `npm install` to sync dependencies. Start local development with `npm run dev`. Run the type-checked production build via `npm run build`; preview it with `npm run preview`. Quality gates include `npm run lint`, `npm run lint:fix`, and `npm run typecheck`. Execute `npm run test` for the Vitest suite or `npm run test:watch` when iterating.

## Coding Style & Naming Conventions
The project follows `.editorconfig` (UTF-8, LF, two spaces). Prettier (`.prettierrc.json`) enforces single quotes, trailing commas, and a 90-character width; run `npm run lint:fix` before commits. Components, hooks, and contexts use PascalCase, utilities use camelCase or kebab-case filenames, and prefer named exports. Keep accessibility and TTS utilities within their respective folders to preserve ownership.

## Testing Guidelines
Vitest with Testing Library powers unit and UI tests. Name specs `*.test.ts` or `*.test.tsx`, colocated with the implementation. Mock browser-only APIs (`speechSynthesis`, `idb-keyval`) to keep runs deterministic. Treat `npm run lint` and `npm run test` as required before any PR.

## Commit & Pull Request Expectations
Follow Conventional Commit prefixes such as `docs:`, `feat:`, or `chore:` with imperative subjects under 72 characters. Reference tracked work in a footer (`Refs #123`). PRs should summarize behavior, call out keyboard or screen-reader impact, and include screenshots for UI changes. Document which local checks you ran.

## Cloud-Only PR Workflow
Operate directly on GitHub rather than the local filesystem. Create branch `codex/<short-task-slug>` for each change, then apply edits via GitHub UI, Codespaces, or API. Before asking for approval, share the plan and a unified diff of pending changes. Open a PR with the steps executed; wait for approval before merging. After approval, squash-merge, delete the branch, and report the resulting commit hash plus the latest GitHub Actions run URL. If any push or merge fails, surface the exact error and the next command to run.

## Accessibility & TTS Notes
Review `DESIGN.md` before altering interaction flows. Announce user-facing changes through `app/src/a11y/announcer-provider.tsx`. Route all audio cues through the TTS context to respect Silent Mode, and record new preferences in `app/src/a11y/preferences.ts`.