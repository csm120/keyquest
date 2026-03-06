# KeyQuest Desktop Accessibility Research

Last updated: 2026-03-06

## Purpose

This note captures current research on how to keep KeyQuest stable while improving accessibility.

Current constraint:

- KeyQuest is a custom Pygame application.
- Earlier heavier `wxPython` usage caused conflicts with the main interface and screen reader behavior.
- We are not changing code yet.
- The immediate goal is to preserve the current keyboard-first, speech-friendly experience and make future changes safer.

## Bottom Line

For KeyQuest, the safest near-term direction is:

1. Keep the main interactive experience in Pygame.
2. Keep screen reader and TTS output as a first-class feature.
3. Avoid reintroducing a large hybrid `wxPython` UI layer into core navigation.
4. Improve documentation, manual testing, and small bounded accessibility improvements before attempting a deeper UI rewrite.

This also means the current speech-driven accessibility model should be treated as a strength, not as something to replace casually. The main improvement area is visual accessibility and visual clarity, not abandoning the current speech-first interaction design.

Research strongly suggests that custom-rendered game or engine UIs rarely expose usable screen reader semantics automatically. In practice, projects like this usually choose one of two paths:

- native OS controls with real accessibility APIs
- custom self-voicing or screen-reader-routed output for a custom UI

KeyQuest already follows the second path. That is a valid path, as long as it is treated as an intentional product model and tested that way.

## KeyQuest Accessibility Model

KeyQuest is not trying to behave like a typical business UI made of standard desktop widgets.

Instead, the intended model is:

- custom Pygame presentation
- full keyboard operation
- full spoken guidance and status feedback
- support for active screen reader users through routed speech
- visual support that should continue improving so sighted and low-vision users get an equally usable experience

That distinction matters. Standard advice about replacing everything with native controls does not automatically fit this kind of application. For KeyQuest, the core question is not "how do we become a normal widget app?" The core question is "how do we keep the current speech support strong while making the visuals clearer and easier to follow?"

## What The Research Says

### 1. Screen readers work best with native accessibility APIs

Microsoft's Windows accessibility guidance says interactive elements should be keyboard accessible and exposed through an accessibility API such as UI Automation.

Implication for KeyQuest:

- A Pygame surface does not automatically become a rich UI Automation tree.
- Simply speaking focused text is helpful, but it is not the same thing as exposing true Name, Role, State, and Value information to NVDA, JAWS, Narrator, or braille displays.

This means a full "standard Windows accessible app" path would require much more than speech output.

### 2. Custom-rendered game UIs usually need a workaround

Game accessibility guidance and long-standing game accessibility writing both describe the same problem: most game engines and custom-rendered UIs draw pixels, not native controls, so screen readers cannot automatically inspect them.

Common workarounds in games include:

- self-voicing
- routing focused text to an active screen reader with a library like Tolk
- keeping menus and text-heavy parts highly structured and keyboard driven

Implication for KeyQuest:

- The current Tolk plus TTS approach is not a hack to throw away immediately.
- It is a normal approach for a custom game-style interface on Windows.
- The main risk is not that the idea is wrong. The risk is assuming it gives the same coverage as native desktop accessibility.

### 3. Blind-accessible tools often favor predictable text and keyboard structure over visual complexity

Developer and player discussions in blind-accessibility communities repeatedly point in the same direction:

- text-based and command-line workflows tend to be easier with screen readers
- split panes, complex graphical layouts, and unusual focus models create friction
- custom focus behavior can easily work against accessibility

Implication for KeyQuest:

- predictable arrow key navigation is good
- repeated spoken confirmation of the focused item is good
- avoiding surprise focus jumps is good
- large visual overlays, hidden state changes, or mixed event-loop UI layers should be treated carefully

This aligns with the concern about earlier `wxPython` conflicts.

### 4. For visually accessible game UI, contrast and text presentation still matter even with speech

Microsoft game accessibility guidance recommends:

- strong contrast for text and important UI
- non-color-only cues
- configurable text and UI presentation where possible
- checking the lowest-contrast state, not just the best-looking one

Implication for KeyQuest:

- speech support does not remove the need for readable text
- long sentence prompts and fixed-size layouts still need visual review
- high contrast support should be treated as more than just detecting the system setting

### 5. Real testing matters more than assumptions

Microsoft recommends tools such as Accessibility Insights for Windows, Inspect, and keyboard-only testing. Their testing guidance also stresses that keyboard flow, focus, and visible text contrast should be verified directly.

Implication for KeyQuest:

- before major accessibility architecture changes, build a reliable test routine
- before claiming stronger compliance, validate with real AT and real flows
- if KeyQuest remains a custom self-voicing UI, that needs its own explicit test contract

## Practical Recommendation For KeyQuest

### Recommended product direction for now

Treat KeyQuest as a:

- keyboard-first
- self-voicing and screen-reader-routed
- visually high-contrast
- custom game-style desktop application

That is different from a standard native Windows business app, and the docs should say so clearly.

Current practical interpretation:

- Speech and screen reader support appear to be working well for the product's intended use.
- The larger gap is visual presentation, especially readability, layout clarity, scaling, and low-vision friendliness.
- Future work should prioritize making the visuals catch up with the quality of the speech experience.

### What not to do right now

- Do not reintroduce a broad `wxPython` interface layer for primary navigation without a contained prototype.
- Do not mix two active UI systems in a way that competes for focus, key handling, or speech timing.
- Do not assume "more native widgets" is automatically better if it destabilizes the learning flow.

### Safer next steps before code changes

1. Document the accessibility model clearly.
2. Add a screen reader smoke-test plan for NVDA, JAWS, and Narrator.
3. Add a keyboard-only regression checklist for the main menu, lessons, tests, games, dialogs, and update flow.
4. Review which screens truly need native semantics versus which can remain speech-driven.
5. Audit visual layouts at larger text sizes and with long prompts.

## Visual Accessibility Priorities

If screen reader and speech behavior are already serving users well, the next accessibility gains are likely to come from visual improvements such as:

- clearer separation between "Type now" and "You typed"
- better handling of long text so prompts do not feel cramped
- stronger low-vision layout structure on text-heavy screens
- more consistent spacing and grouping across menus and active modes
- safer large-text behavior at higher font scales
- stronger support for custom high-contrast expectations, not just detection

These priorities line up especially well with WCAG ideas such as:

- Focus Appearance: make the active area obvious and hard to miss
- Non-text Contrast: make frames, panels, and indicators stand out clearly
- Reflow: make larger text and longer content stay readable without forcing visual hunting

In other words: preserve the speech model, and focus design effort on visual readability and visual guidance.

## Suggested Accessibility Contract

If KeyQuest keeps its current architecture, the practical accessibility contract should be something like this:

- Every interactive flow is usable with the keyboard only.
- Every focused item is announced clearly through screen reader routing or TTS.
- Important status changes are announced in speech and shown visually.
- Visual focus is always visible and not color-only.
- Text is readable at supported font scales without clipping critical information.
- Results, help, and setup content never disappear because of missing optional dependencies.

This is a more honest and useful contract than claiming full native desktop accessibility semantics when the UI is custom drawn.

## Open Questions For Future Research

- Should KeyQuest keep all primary UI in Pygame permanently, or only most of it?
- Which screens would benefit most from native accessible dialogs or controls without destabilizing the app?
- Is a bounded native layer for results/help screens stable enough if isolated from the main event loop?
- Would a custom UIA bridge ever be worth the engineering cost for this app?

## Sources

Official sources:

- Microsoft Learn: Accessibility design basics for Win32 apps
  - https://learn.microsoft.com/en-us/windows/win32/uxguide/inter-accessibility
- Microsoft Learn: Accessibility overview for Windows apps
  - https://learn.microsoft.com/en-us/windows/apps/design/accessibility/accessibility-overview
- Microsoft Learn: Accessibility testing for Windows apps
  - https://learn.microsoft.com/en-us/windows/apps/design/accessibility/accessibility-testing
- Microsoft Learn: Xbox Accessibility Guideline 102
  - https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102

Game accessibility references:

- Game Accessibility Guidelines: Ensure screen reader support, including menus and installers
  - https://gameaccessibilityguidelines.com/ensure-screenreader-support-including-menus-installers/
- Ian Hamilton: Screenreaders and game engines
  - https://ian-hamilton.com/screenreaders-and-game-engines/
- Audiokinetic blog: Blind accessibility and screen readers in games
  - https://www.audiokinetic.com/en/blog/blind-accessibility-step-one-get-to-know-your-players/

Community references:

- AudioGames community article feed with Python/Tolk examples
  - https://audiogames7.rssing.com/chan-63749684/all_p7.html
- Interactive Fiction community discussion on screen reader accessibility
  - https://intfiction.org/t/notes-on-screen-reader-accessibility/5660

Implementation reference:

- Tolk project
  - https://github.com/dkager/tolk
