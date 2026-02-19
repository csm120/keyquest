# Progress File Migration Strategy (`progress.json`)

KeyQuest stores user progress in `progress.json` in the app folder (next to `keyquest.pyw` / the `.exe`). This file is user data and should remain backward-compatible across releases.

## Current Strategy

- **Additive changes only**: prefer adding new fields rather than renaming/removing existing ones.
- **Default on missing**: when loading, use `data.get("field", default)` for every field.
- **Type-safe conversion**: if a field needs coercion (e.g., numeric strings), explicitly cast it.
- **Ignore unknown fields**: loaders should not fail if extra keys exist.

## Schema Version

- `modules/state_manager.py` writes `schema_version` (currently `1`) into `progress.json`.
- Loaders treat missing `schema_version` as `0` (older files).

At the moment, the loader does not branch on `schema_version`; it is recorded so future migrations can be explicit.

## When You Need a Migration

Do a migration when you must:

- rename a field,
- change a field’s type or shape (e.g., list → dict),
- split/merge fields,
- or fix previously-buggy saved data.

Recommended approach:

1. Read raw JSON.
2. If `schema_version` is older, transform the dict in-memory.
3. Apply the normal `data.get(...)` assignments from the transformed dict.
4. Save back out (optional) with the latest `schema_version`.

## Notes

- Keep `progress.sample.json` as a tiny example only; the app does not read it.
- If you add new complex structures (dicts/sets), store JSON-friendly forms (lists and dicts) and convert in code.

