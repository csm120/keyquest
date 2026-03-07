# Keyboard Command Audit

Started: March 7, 2026

Purpose:
Review the public keyboard-command sentence files against primary vendor documentation only.

Files in scope:
- `Sentences/Windows Commands.txt`
- `Sentences/JAWS Commands.txt`
- `Sentences/NVDA Commands.txt`

Primary sources:
- Microsoft Windows keyboard shortcuts:
  - https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec
- NVDA User Guide:
  - https://download.nvaccess.org/documentation/userGuide.html
- Freedom Scientific JAWS hotkeys:
  - https://www.freedomscientific.com/training/jaws/hotkeys/

Rules:
- Prefer official vendor docs over memory.
- Treat commands as version-specific unless the vendor docs present them as stable defaults.
- Flag commands that are app-specific, context-specific, deprecated, or no longer useful for most learners.
- Keep public-facing sentence wording plain and practical.
- Prefer the commands that are most useful to the majority of learners, not edge-case or specialist commands.
- Do not use `+` or `plus` as shortcut notation in learner-facing text. Prefer plain forms like `Windows N`, `Insert T`, or `Control Shift Escape`. When the actual key name is `Plus`, spell that out as `the Plus key`.

## Confirmed findings

### NVDA

1. `NVDA+F1` was incorrect and not useful for most learners.
   - Previous text: `Press NVDA plus F1 to open user guide.`
   - Official meaning: opens the log viewer and displays developer information about the current navigator object.
   - Action taken: removed from `Sentences/NVDA Commands.txt` and from the public blog post.

2. `NVDA+T` is correct for reporting the active window title.
   - Status: confirmed against official NVDA documentation.

3. `NVDA+F12` is correct for reporting time/date.
   - Official behavior: press once for time, press twice for date.
   - Current sentence wording is acceptable but may be refined later for clarity.

4. The previous NVDA sentence file mixed several problems:
   - wrong commands
   - desktop/laptop layout confusion
   - review-cursor-only commands without context
   - browse-mode quick keys presented as if they worked everywhere
   - developer or niche commands that are not useful for most learners
   - Action taken:
     - replaced the file with a smaller, practical, verified set
     - added `In browse mode` wording to single-letter web navigation commands
     - removed ambiguous review and synth-setting lines for now

5. `NVDA+B` and `NVDA+End` were previously confused.
   - `NVDA+B` is for reading the active window.
   - status bar reporting should not have been described under `NVDA+B`.

## Suspected issues to verify next

### JAWS

1. The previous JAWS sentence file mixed practical commands with inaccurate or unclear lines.
   - `Insert+Tab` had been described too narrowly as a status-bar command.
   - `Insert+F1` had been described too loosely as generic help.
   - several quick-navigation keys were presented as if they worked everywhere, instead of specifically on web pages
   - some command descriptions were likely wrong or too niche for most learners

2. Action taken:
   - replaced the file with a smaller, practical, learner-facing set
   - rewrote `Insert+Tab` as progress-bar status in dialog context
   - rewrote `Insert+F1` as context-sensitive help
   - rewrote `Insert+V` as Quick Settings
   - removed `Insert+F2` because the earlier wording was inaccurate and the command is not especially useful for most learners
   - clarified `Insert+3` as the number-row command for passing the next key through
   - rewrote web quick-navigation commands as `On web pages...`

### Windows

1. The Windows file includes a mix of stable shortcuts and outdated older wording.

2. Action taken in the first pass:
   - rewrote `Windows+A` to version-neutral `Quick Settings or Action Center`
   - removed `Windows+C` because its meaning varies too much across Windows versions and configurations
   - rewrote `Windows+U` from `Ease of Access Center` to `Accessibility settings`
   - removed `Windows+Pause` because current behavior is too version-dependent
   - removed overly broad `F1`, `F3`, and `F7` lines that were too context-dependent for a general Windows commands topic
   - narrowed `F4` to File Explorer address-bar-list behavior

3. Action taken in the second pass:
   - rewrote `Windows+V` to version-neutral clipboard wording
   - rewrote `F11` away from a broad all-app fullscreen claim to File Explorer behavior
   - removed overly app-specific `Alt+F`, `Alt+E`, `Alt+V`, and `Alt+H` menu-letter lines
   - rewrote `Windows+K` to current Cast wording
   - rewrote `Windows+U` to a version-neutral `Accessibility settings or Ease of Access`

4. Action taken in the third pass:
   - rewrote `Alt+Enter` to selected-item Properties wording
   - rewrote `Windows+1 through 9` to make the taskbar-app shortcut clearer
   - rewrote `Alt+Up Arrow` to File Explorer context
   - removed `Backspace` as previous-folder navigation because it is not reliable enough as a modern general Windows shortcut

5. Action taken in the fourth pass:
   - removed a duplicate `Ctrl+Shift+Escape` line
   - removed the remaining outdated `Windows+Break` line

6. Action taken in the fifth pass:
   - removed a cluster of browser- and document-specific shortcuts that were too context-dependent for a general Windows commands topic
   - kept the file focused on Windows, Explorer, shell, screenshot, accessibility, and window-management shortcuts

7. Action taken in the sixth pass:
   - rewrote a few remaining lines to be less app-specific
   - removed `F11` and `F10` because they were still too context-bound for a general Windows topic
   - rewrote Explorer-only shortcuts so they say `in File Explorer`
   - rewrote `Windows+G` to `Xbox Game Bar`
   - rewrote `Windows+Comma` to the more accurate temporary desktop peek wording

8. Action taken in the seventh pass:
   - removed `Windows+G` because Xbox Game Bar is not useful enough for the general learner-focused command set
   - removed `Windows+Comma` because desktop peek is also not useful enough for the general learner-focused command set

9. Action taken in the eighth pass:
   - removed lower-value app commands such as `Ctrl+P`, `Ctrl+S`, and `Ctrl+N`
   - removed lower-value edge-case commands such as `Ctrl+Alt+Tab` and `Alt+Shift`
   - kept the Windows file aligned with the majority-usefulness rule rather than broad completeness

10. Action taken in the ninth pass:
   - restored `Ctrl+P` and `Ctrl+S` because they are broadly useful for many learners
   - kept `Ctrl+F`, `Windows+A`, `Application key`, and `Shift+F10`
   - removed screenshot combo lines `Windows+Shift+S` and `Windows+Print Screen`
   - removed `Windows+K`

11. Action taken in the tenth pass:
   - added `Windows+N` because it is broadly useful and part of the current Windows notification/calendar experience

12. Still needs review:
   - several Explorer/window-management shortcuts should be verified against Microsoft wording
   - some shortcuts are context-specific but may still be worth keeping if rewritten carefully

## Public note decision

- No extra public note was added to the blog post about command verification.
- Reason:
  - that would make the blog post feel more technical than it needs to be
  - the better place for version and context caveats is the command content itself and this internal audit note

## Next steps

1. Audit NVDA file line by line and mark:
   - correct
   - correct but too technical
   - wrong
   - too niche for general learners
2. Audit JAWS file with the same categories.
3. Audit Windows file with Microsoft’s current Windows shortcuts page as the baseline.
4. Rewrite only after verification.
5. Keep the learner-facing content practical and general unless a topic is clearly advanced.
