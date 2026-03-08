# KeyQuest Screen Reader Smoke Tests

Last updated: 2026-03-06

## Purpose

This is a lightweight manual check for the current KeyQuest accessibility model.

It is not meant to prove formal compliance. It is meant to answer a simpler question:

"Does KeyQuest still basically work with a screen reader in the way the product is designed to work?"

For KeyQuest, a smoke test means a short, repeatable check of the most important speech and keyboard flows after meaningful changes.

## Why This Matters

KeyQuest uses a custom Pygame interface, not standard desktop widgets.

That means the most important regression risks are usually:

- focused items stop being announced
- speech timing becomes confusing
- keyboard navigation stops matching speech
- important mode changes are no longer spoken
- dialogs, setup screens, or game menus become unclear

A smoke test is a fast way to catch those problems early.

## Recommended Readers

Use whichever of these are available:

- NVDA
- JAWS
- Narrator

NVDA is the best default smoke-test reader because it is common and easy to run regularly.

## Smoke Test Scope

The goal is not to test every feature in depth.

The goal is to confirm that the main experience still feels understandable and controllable.

## Basic Smoke Test

### 1. Startup

Check:

- Launch KeyQuest.
- Confirm the app opens without speech conflicts.
- Confirm the first menu item is understandable when focus lands.

Pass if:

- startup speech is present and not confusing
- the initial focused item is clear

### 2. Main Menu Navigation

Check:

- Use Up and Down arrows through several main menu items.
- Confirm each item is announced clearly.
- Confirm spoken focus matches the visible selection.

Pass if:

- every move announces the newly selected item
- there are no stale or repeated announcements that make navigation confusing

### 3. Open and Exit a Menu

Check:

- Open one menu such as Options, Learn Sounds, or About.
- Move through a few items.
- Escape back out.

Pass if:

- entering the screen is announced clearly
- item navigation is understandable
- returning to the previous screen is understandable

### 4. Start a Typing Flow

Check:

- Start Speed Test or Sentence Practice.
- Listen to the opening instructions.
- Use `Ctrl+Space` to repeat the prompt.

Pass if:

- the user is told what to type
- instructions are understandable
- repeat works

### 5. Make an Error

Check:

- Intentionally type something wrong in a sentence flow.

Pass if:

- the correction message makes sense
- the user can tell what to type next

### 6. Escape Out of an Active Mode

Check:

- While in an active typing or game mode, use Escape as instructed.

Pass if:

- the remaining escape count is understandable
- returning to the menu is announced clearly

### 7. Results or Information Screen

Check:

- Complete a short flow that shows results or open a help/info screen.

Pass if:

- the content appears
- it is readable with the screen reader
- it can be closed predictably

## What To Write Down

If something feels wrong, note:

- screen reader used
- exact screen or mode
- exact keys pressed
- what was expected
- what was spoken instead
- whether the visible focus matched the spoken focus

## Current Accessibility Intent

This smoke test is based on the current product intent:

- keyboard-first interaction
- strong spoken guidance
- strong screen reader friendliness through routed speech
- visual accessibility improving alongside that model

It is not based on the assumption that every screen is a native Windows widget tree.

## When to Re-run These Tests

Re-run the smoke tests after any change to the following files:

- `modules/speech_manager.py` — core speech routing
- `modules/dialog_manager.py` — accessible results/info dialogs
- `modules/notifications.py` — badge, level-up, and quest announcements
- `modules/lesson_mode.py` — lesson prompts and mismatch feedback
- `modules/test_modes.py` — speed test speech
- `ui/render_menus.py`, `ui/render_lesson.py`, or any other `ui/render_*.py` — layout changes can affect what is visually focused and thus what gets announced

A quick smoke run after these changes catches regressions before users do.
