# KeyQuest

An accessible, screen-reader-first, turn-based typing adventure.

- High-contrast by default  
- Screen Reader mode vs in-app TTS (toggle)  
- ARIA live regions for status and alerts  
- Global hotkeys (disabled during drills)  
- Seeded procedural progression (deterministic)

## Setup
1. Install Node.js 20 (ships with npm).
2. From `app/`, run `npm install` to pull dependencies.
3. Copy `.env.example` to `.env` if you introduce environment-specific flags.

## Local Development
- `npm run dev` — launch Vite with hot reload.
- `npm run lint` / `npm run lint:fix` — enforce the shared ESLint + Prettier rules.
- `npm run typecheck` — run the TypeScript project references build without emitting files.
- `npm run test` — execute Vitest suites; add `--watch` while iterating.
- `npm run build` — type-check and emit production assets to `app/dist`.

All commands run from the `app/` directory.

## Continuous Integration
GitHub Actions (see `.github/workflows/ci.yml`) runs on pushes and pull requests targeting `main`. The workflow:
- spins a matrix across `ubuntu-latest` and `windows-latest` for Node 18 and 20;
- installs dependencies with `npm ci` using built-in npm caching;
- builds the production bundle and runs `npm test -- --passWithNoTests` so Vitest passes even when suites are pending;
- fails fast if linting, type-checking, or tests surface TypeScript errors.

Record the commands you run in PR checklists so reviewers can mirror the setup.