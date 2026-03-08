# New in Key Quest

## Saturday March 7th 2026

Version 1.1.1

This patch republishes the lesson and speech improvements below after fixing release validation checks.

This release makes lesson navigation and spoken guidance clearer.

- Lessons and Free Practice now end with clearer choice menus that use Up and Down arrows.
- The title now comes first, followed right away by the navigation instructions, so new screen reader users hear how to move through the choices sooner.
- The post-session wording now uses simpler continue and back wording.
- `Home` and `End` jump to the first and last items in menus, lesson lists, options, and results menus.
- Startup speech and menu speech are more reliable again on Windows.

Typing lesson speech is clearer.

- If you make a mistake in a lesson, KeyQuest now repeats only what is left to type instead of starting the whole prompt over.
- `Control+Space` in lessons now repeats only the remaining part of the target.
- Repeated-letter drills are spoken more clearly, so patterns like `aass` and `asas` are read as letter sequences instead of sounding like made-up words.
- Early lessons now introduce a new key with simpler repeated drills first before mixing it into longer patterns.

## Friday March 6th 2026 at 11:52PM

Version 1.0.4

This release fixes the Windows release build.

- The release build now uses a `cytolk` version that matches what KeyQuest already uses locally, so GitHub can publish the installer and portable downloads again.

## Friday March 6th 2026 at 11:49PM

Release update

This release fixes the update pipeline itself.

- GitHub release publishing was repaired so shipped updates can build and publish the installer and portable downloads correctly again.
- The release process now has a clearer split between a plain GitHub push and a full shipped update.

## Friday March 6th 2026 at 11:21PM

Release update

Keyboard command practice is clearer.

- Windows, NVDA, and JAWS command topics were cleaned up so the wording feels more practical and less technical.
- Several command lines now read more naturally while still teaching the same shortcuts.

The guide and blog wording are easier to follow.

- Download links now use cleaner names like `Installer.exe` and `Portable.zip`.
- The public guide, changelog, and blog wording were smoothed out to be clearer for new users, AT instructors, and educators.

## Friday March 6th 2026 at 5:07PM

Release update

The screen is easier to follow while you type and move through menus.

- Long sentences no longer try to stay on one line. They break across lines so they are easier to read.
- Your typed text can also continue onto the next line instead of getting cramped.
- Long menus are easier to follow because the current item stays in view more clearly.
- More screens now show when there are more items above or below the part you are looking at, including menus, options, shop lists, pet lists, and sound lists.
- There is now a Focus Assist option that adds stronger panels and emphasis around the part of the screen you should pay attention to.
- Several typing, setup, and results screens use stronger spacing and grouping so the active area is easier to find.
- Font Size now also includes larger 175% and 200% options for people who need bigger text.
- The guide and What's New page are being kept more current so it is easier to see what changed.

Typing reminders are clearer.

- Speed Test and Sentence Practice now remind you to use capital letters and punctuation before you begin.
- If you make a sentence mistake, KeyQuest gives a simpler spoken hint about what to type next.
- Quit now stays at the very end of the Main Menu.

KeyQuest now has a clearer help and update experience.

- There is now a Main Menu item for the online guide.
- There is now a Main Menu item for this What's New page.
- You can now check for updates from inside KeyQuest, whether you installed it or are using the portable version.
- When KeyQuest updates, your progress stays with you.
- If you added your own sentence files, KeyQuest keeps them during updates and also brings in new built-in sentences.

## Wednesday February 25th 2026

Release update

Reading and visual support are better.

- Text can now be made larger with the Font Size option.
- Key presses can show a brief visual flash as well as playing sounds.
- If your computer is already using Windows High Contrast, KeyQuest follows that automatically when the theme is set to Auto.
- A small on-screen Escape counter appears while you are exiting active modes.

## Thursday February 19th 2026

Version 1.0

KeyQuest 1.0 was released.

- The About screen was added to the Main Menu.
- The first Windows installer was added.
- The guide was expanded and made easier to read in a web browser.
