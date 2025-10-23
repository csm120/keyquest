import { initTheme } from "./a11y/theme.js";
import { updateBuildFooter } from "./build/footer.js";
import { Speech } from "./core/speech.js";
import { Audio } from "./core/audio.js";
import { AppState } from "./core/state.js";
import { loadProgress, saveProgress } from "./core/storage.js";
import * as CONST from "./core/constants.js";

/**
 * KeyQuest - Main Application
 * An accessible, screen-reader-first typing adventure
 */
class KeyQuestApp {
  constructor() {
    this.state = new AppState();
    this.speech = new Speech();
    this.audio = new Audio();

    // DOM elements
    this.statusEl = document.getElementById("status");
    this.alertsEl = document.getElementById("alerts");
    this.rootEl = document.getElementById("game-root");

    // Load saved progress
    const progress = loadProgress();
    this.state.lesson.stage = Math.max(0, Math.min(progress.stage, CONST.STAGE_LETTERS.length - 1));

    // Bind keyboard handler
    document.addEventListener("keydown", (e) => this.handleKeyDown(e));
  }

  // ==================== ANNOUNCE HELPERS ====================

  announceStatus(text) {
    this.statusEl.textContent = "";
    setTimeout(() => {
      this.statusEl.textContent = text;
    }, 10);
  }

  announceAlert(text, priority = false, protect = 0) {
    this.alertsEl.textContent = "";
    setTimeout(() => {
      this.alertsEl.textContent = text;
    }, 10);
    this.speech.say(text, priority, protect);
  }

  // ==================== MAIN LOOP ====================

  start() {
    // Focus the game root to automatically enter application mode for screen readers
    setTimeout(() => {
      this.rootEl.focus();
    }, 100);

    // Add initial screen reader instructions
    this.announceAlert(
      "KeyQuest typing game loaded. Screen reader users: You are now in application mode. Use arrow keys to navigate. If arrow keys don't work, enter forms mode or focus mode in your screen reader. For NVDA press Insert plus Space. For JAWS press Enter.",
      true,
      3.0
    );

    setTimeout(() => {
      this.showMenu();
    }, 500);
  }

  handleKeyDown(e) {
    // Route to appropriate handler based on mode
    switch (this.state.mode) {
      case "MENU":
        this.handleMenuKey(e);
        break;
      case "TUTORIAL":
        this.handleTutorialKey(e);
        break;
      case "LESSON":
        this.handleLessonKey(e);
        break;
      case "TEST":
        this.handleTestKey(e);
        break;
      case "RESULTS":
        this.handleResultsKey(e);
        break;
    }
  }

  // ==================== MENU ====================

  showMenu() {
    this.state.mode = "MENU";
    this.state.menuIndex = 0;

    const stage = this.state.lesson.stage + 1;
    const total = CONST.STAGE_LETTERS.length;

    this.rootEl.innerHTML = `
      <div style="max-width:600px;margin:2rem auto;text-align:center;">
        <h2 id="menu-heading">Main Menu</h2>
        <nav aria-labelledby="menu-heading">
          <div id="menu-list" role="listbox" aria-activedescendant="menu-item-0" tabindex="0"
               style="margin:2rem auto;max-width:300px;border:2px solid var(--fg);border-radius:0.5rem;padding:0.5rem;">
            ${this.state.menuItems.map((item, i) =>
              `<div id="menu-item-${i}" role="option" aria-selected="${i === 0 ? 'true' : 'false'}"
                   style="padding:1rem;margin:0.25rem;background:${i === 0 ? 'var(--hilite, #444)' : 'transparent'};
                   border:1px solid ${i === 0 ? 'var(--fg)' : 'transparent'};border-radius:0.25rem;cursor:pointer;">
                ${item}
              </div>`
            ).join('')}
          </div>
        </nav>
        <p class="muted" style="margin-top:1rem;">Current Stage: ${stage} / ${total}</p>
        <p class="muted" aria-live="polite">Use Up/Down arrows to navigate, Enter or Space to select</p>
      </div>
    `;

    // Focus the listbox
    setTimeout(() => {
      const listbox = document.getElementById("menu-list");
      if (listbox) listbox.focus();
    }, 100);

    const items = this.state.menuItems;
    const current = items[this.state.menuIndex];
    this.announceAlert(
      `Main menu. ${current} selected. Use Up and Down arrows to navigate. Press Enter or Space to select.`,
      true,
      2.0
    );
  }

  updateMenuHighlight() {
    const listbox = document.getElementById("menu-list");
    const menuItems = this.rootEl.querySelectorAll('[role="option"]');

    menuItems.forEach((item, i) => {
      const isSelected = i === this.state.menuIndex;
      item.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      item.style.background = isSelected ? 'var(--hilite, #444)' : 'transparent';
      item.style.border = `1px solid ${isSelected ? 'var(--fg)' : 'transparent'}`;
    });

    if (listbox) {
      listbox.setAttribute('aria-activedescendant', `menu-item-${this.state.menuIndex}`);
    }
  }

  handleMenuKey(e) {
    if (e.key === "Escape") {
      // Could add confirmation dialog, for now just stay in menu
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      this.state.menuIndex = (this.state.menuIndex - 1 + this.state.menuItems.length) % this.state.menuItems.length;
      this.updateMenuHighlight();
      this.announceStatus(this.state.menuItems[this.state.menuIndex]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      this.state.menuIndex = (this.state.menuIndex + 1) % this.state.menuItems.length;
      this.updateMenuHighlight();
      this.announceStatus(this.state.menuItems[this.state.menuIndex]);
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      const choice = this.state.menuItems[this.state.menuIndex];

      if (choice === "Tutorial") {
        this.startTutorial();
      } else if (choice === "Lesson") {
        this.startLesson();
      } else if (choice === "Speed Test") {
        this.startTest();
      } else if (choice === "Quit") {
        this.announceAlert("Goodbye!", true);
        setTimeout(() => {
          window.close();
        }, 1000);
      }
    }
  }

  // ==================== TUTORIAL ====================

  startTutorial() {
    this.state.mode = "TUTORIAL";
    const t = this.state.tutorial;
    t.phase = 1;
    t.sequence = [];
    t.countsDone = {};

    // Build sequence: 3 of each key for phase 1
    for (const [name, key] of CONST.PHASE1_KEYS) {
      for (let i = 0; i < CONST.TUTORIAL_EACH_COUNT; i++) {
        t.sequence.push([name, key]);
      }
    }

    // Shuffle
    for (let i = t.sequence.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [t.sequence[i], t.sequence[j]] = [t.sequence[j], t.sequence[i]];
    }

    t.index = 0;

    this.renderTutorial();

    this.announceAlert(
      "Tutorial. First: arrows and the space bar, three each. Arrows are together: Up above Down, Left beside Right. Space is the long bar at the bottom.",
      true,
      2.5
    );

    this.loadTutorialPrompt();
  }

  renderTutorial() {
    const t = this.state.tutorial;
    const keys = t.phase === 1 ? CONST.PHASE1_KEYS : CONST.PHASE2_KEYS;

    this.rootEl.innerHTML = `
      <div style="max-width:700px;margin:2rem auto;text-align:center;">
        <h2>Tutorial - Phase ${t.phase}</h2>
        <div style="margin:2rem 0;font-size:2rem;padding:2rem;border:3px solid var(--fg);">
          Press: <strong id="tutorial-prompt">...</strong>
        </div>
        <div style="margin:2rem 0;">
          <h3>Progress:</h3>
          ${keys.map(([name]) => {
            const count = t.countsDone[name] || 0;
            return `<p>${CONST.FRIENDLY_NAMES[name]}: ${count}/${CONST.TUTORIAL_EACH_COUNT}</p>`;
          }).join('')}
        </div>
        <p class="muted">Ctrl+Space to repeat prompt, Escape to return to menu</p>
      </div>
    `;
  }

  loadTutorialPrompt() {
    const t = this.state.tutorial;

    if (t.index >= t.sequence.length) {
      if (t.phase === 1) {
        // Move to phase 2
        t.phase = 2;
        t.sequence = [];
        for (const [name, key] of CONST.PHASE2_KEYS) {
          for (let i = 0; i < CONST.TUTORIAL_EACH_COUNT; i++) {
            t.sequence.push([name, key]);
          }
        }
        // Shuffle
        for (let i = t.sequence.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [t.sequence[i], t.sequence[j]] = [t.sequence[j], t.sequence[i]];
        }
        t.index = 0;
        this.renderTutorial();
        this.announceAlert(
          "Great! Now also use Enter. Enter is on the right side of the letters, often tall or L‑shaped.",
          true,
          2.5
        );
        this.loadTutorialPrompt();
        return;
      } else {
        // Tutorial complete
        this.announceAlert("Tutorial complete. Returning to menu.", true);
        setTimeout(() => this.showMenu(), 1500);
        return;
      }
    }

    const [name, key] = t.sequence[t.index];
    t.requiredName = name;
    t.requiredKey = key;

    const promptEl = document.getElementById("tutorial-prompt");
    if (promptEl) {
      promptEl.textContent = CONST.FRIENDLY_NAMES[name];
    }

    this.announceStatus(`Press ${CONST.FRIENDLY_NAMES[name]}.`);
  }

  handleTutorialKey(e) {
    if (e.key === "Escape") {
      this.showMenu();
      return;
    }

    // Ctrl+Space repeats prompt
    if (e.key === " " && e.ctrlKey) {
      e.preventDefault();
      const t = this.state.tutorial;
      this.announceStatus(`Press ${CONST.FRIENDLY_NAMES[t.requiredName]}.`);
      return;
    }

    const t = this.state.tutorial;
    const keyset = t.phase === 1 ? CONST.PHASE1_KEYS : CONST.PHASE2_KEYS;

    // Find which key was pressed
    let pressedName = null;
    for (const [name, key] of keyset) {
      if (e.key === key) {
        pressedName = name;
        break;
      }
    }

    if (pressedName === null) {
      // Invalid key
      if (t.phase === 1) {
        this.announceStatus("Use the arrow keys or the space bar.");
      } else {
        this.announceStatus("Use arrows, space, or Enter.");
      }
      return;
    }

    // Check if correct
    if (e.key === t.requiredKey) {
      e.preventDefault();
      this.audio.beepOk();
      t.countsDone[t.requiredName] = (t.countsDone[t.requiredName] || 0) + 1;
      t.index++;

      const praises = ["Good.", "Nice.", "Correct."];
      this.announceStatus(praises[Math.floor(Math.random() * praises.length)]);

      this.renderTutorial();

      setTimeout(() => {
        this.loadTutorialPrompt();
      }, 500);
    } else {
      e.preventDefault();
      this.audio.beepBad();

      const target = t.requiredName;
      const pressed = pressedName;
      const relationKey = `${pressed}-${target}`;
      const guidance = CONST.RELATIONS[relationKey] || `Try ${CONST.FRIENDLY_NAMES[target]}.`;
      const hint = CONST.HINTS[target];

      this.announceAlert(`${CONST.FRIENDLY_NAMES[pressed]}. ${guidance} ${hint}`);
    }
  }

  // ==================== LESSON ====================

  startLesson() {
    this.state.mode = "LESSON";
    const stage = this.state.lesson.stage;
    this.state.lesson.index = 0;
    this.state.lesson.typed = "";

    this.buildLessonBatch();
    this.renderLesson();

    // Get all cumulative keys for this stage
    const allKeys = new Set();
    for (let i = 0; i <= stage; i++) {
      CONST.STAGE_LETTERS[i].forEach(k => allKeys.add(k));
    }
    const keyList = Array.from(allKeys).sort().join(', ');

    this.announceAlert(
      `Lesson Stage ${stage + 1}. Practice keys: ${keyList}. Control Space repeats the prompt.`,
      true,
      2.0
    );

    setTimeout(() => {
      this.lessonPrompt();
    }, 1500);
  }

  buildLessonBatch() {
    const stage = this.state.lesson.stage;
    const allowed = new Set();

    // Accumulate all keys up to this stage
    for (let i = 0; i <= stage; i++) {
      CONST.STAGE_LETTERS[i].forEach(k => allowed.add(k));
    }

    const allowedList = Array.from(allowed).sort();
    const batch = [];

    for (let i = 0; i < CONST.LESSON_BATCH; i++) {
      const minLen = 1;
      const maxLen = stage < 2 ? 4 : 5;
      const length = Math.floor(Math.random() * (maxLen - minLen + 1)) + minLen;

      let word = "";
      for (let j = 0; j < length; j++) {
        word += allowedList[Math.floor(Math.random() * allowedList.length)];
      }
      batch.push(word);
    }

    this.state.lesson.batchWords = batch;
  }

  renderLesson() {
    const l = this.state.lesson;
    const target = l.batchWords[l.index] || "";
    const stage = l.stage;

    // Get all keys for this stage
    const allKeys = new Set();
    for (let i = 0; i <= stage; i++) {
      CONST.STAGE_LETTERS[i].forEach(k => allKeys.add(k));
    }
    const keyList = Array.from(allKeys).sort().join(', ');

    this.rootEl.innerHTML = `
      <div style="max-width:700px;margin:2rem auto;text-align:center;">
        <h2>Lesson - Stage ${stage + 1}</h2>
        <p class="muted">Keys: ${keyList}</p>
        <div style="margin:2rem 0;font-size:2.5rem;padding:2rem;border:3px solid var(--accent, #9ec1ff);">
          <div id="lesson-target">${target}</div>
        </div>
        <div style="font-size:2rem;padding:1rem;min-height:3rem;border:2px solid var(--fg);">
          <span id="lesson-typed">${l.typed}</span>
        </div>
        <p style="margin-top:2rem;">Item ${l.index + 1} of ${l.batchWords.length}</p>
        <p class="muted">Ctrl+Space repeats prompt | Escape returns to menu</p>
      </div>
    `;
  }

  lessonPrompt() {
    const target = this.state.lesson.batchWords[this.state.lesson.index];
    this.announceAlert(`Type: ${target}`, true);
  }

  nextLessonItem() {
    this.state.lesson.index++;
    this.state.lesson.typed = "";

    if (this.state.lesson.index >= this.state.lesson.batchWords.length) {
      // Batch complete
      this.showLessonResults();
    } else {
      this.renderLesson();
      setTimeout(() => {
        this.lessonPrompt();
      }, 500);
    }
  }

  showLessonResults() {
    this.state.mode = "RESULTS";
    const stage = this.state.lesson.stage;

    if (stage + 1 < CONST.STAGE_LETTERS.length) {
      this.state.resultsText = `Great job! You completed stage ${stage + 1}. Press Space to add new keys, Enter to repeat this stage, or Escape for menu.`;
    } else {
      this.state.resultsText = `Excellent! You have mastered all stages. Press Enter to practice this stage again or Escape for menu.`;
    }

    this.renderResults();
    this.announceAlert(this.state.resultsText, true, 3.0);
  }

  handleLessonKey(e) {
    if (e.key === "Escape") {
      this.showMenu();
      return;
    }

    // Ctrl+Space repeats prompt
    if (e.key === " " && e.ctrlKey) {
      e.preventDefault();
      this.lessonPrompt();
      return;
    }

    // Backspace
    if (e.key === "Backspace") {
      e.preventDefault();
      this.state.lesson.typed = this.state.lesson.typed.slice(0, -1);
      this.renderLesson();
      return;
    }

    // Only process printable characters
    if (e.key.length === 1 && e.key.match(/[a-z0-9;,.'\/\s]/i)) {
      e.preventDefault();
      const ch = e.key;
      const target = this.state.lesson.batchWords[this.state.lesson.index];

      this.state.lesson.typed += ch;
      const typed = this.state.lesson.typed;

      // Check if prefix matches
      if (!target.startsWith(typed)) {
        this.audio.beepBad();
        this.state.lesson.typed = "";
        this.renderLesson();
        return;
      }

      // Check if complete
      if (typed === target) {
        this.audio.beepOk();
        this.nextLessonItem();
      } else {
        this.renderLesson();
      }
    }
  }

  // ==================== SPEED TEST ====================

  startTest() {
    this.state.mode = "TEST";
    const sentences = [...CONST.TEST_SENTENCES];

    // Shuffle sentences
    for (let i = sentences.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [sentences[i], sentences[j]] = [sentences[j], sentences[i]];
    }

    this.state.test = {
      running: false, // Will start on first keystroke
      startTime: 0,
      current: "",
      remaining: sentences,
      typed: "",
      correctChars: 0,
      totalChars: 0
    };

    this.renderTest();

    this.announceAlert("Speed test. Sixty seconds. Control Space repeats the remaining text.", true, 2.0);

    setTimeout(() => {
      this.loadNextSentence();
    }, 1500);
  }

  loadNextSentence() {
    if (this.state.test.remaining.length === 0) {
      this.finishTest();
      return;
    }

    this.state.test.current = this.state.test.remaining.shift();
    this.state.test.typed = "";
    this.renderTest();
    this.announceStatus(this.state.test.current);
  }

  renderTest() {
    const t = this.state.test;
    let remaining = CONST.TEST_SECONDS;

    if (t.startTime > 0) {
      const elapsed = (Date.now() - t.startTime) / 1000;
      remaining = Math.max(0, CONST.TEST_SECONDS - elapsed);
    }

    this.rootEl.innerHTML = `
      <div style="max-width:700px;margin:2rem auto;text-align:center;">
        <h2>Speed Test</h2>
        <div style="margin:2rem 0;font-size:1.5rem;color:var(--accent, #9ec1ff);">
          ${t.current}
        </div>
        <div style="font-size:2rem;padding:1rem;min-height:3rem;border:2px solid var(--fg);">
          ${t.typed}
        </div>
        <p style="margin-top:2rem;font-size:1.5rem;">Time: ${Math.ceil(remaining)}s</p>
        <p class="muted">Ctrl+Space repeats text | Escape returns to menu</p>
      </div>
    `;

    // Auto-update timer if running
    if (t.startTime > 0 && remaining > 0) {
      setTimeout(() => {
        if (this.state.mode === "TEST" && this.state.test.startTime > 0) {
          const elapsed = (Date.now() - this.state.test.startTime) / 1000;
          if (elapsed >= CONST.TEST_SECONDS) {
            this.finishTest();
          } else {
            this.renderTest();
          }
        }
      }, 1000);
    }
  }

  finishTest() {
    const t = this.state.test;
    t.running = false;

    const acc = t.totalChars > 0 ? (t.correctChars / t.totalChars) * 100 : 0;
    const elapsed = t.startTime > 0 ? (Date.now() - t.startTime) / 1000 : CONST.TEST_SECONDS;
    const words = t.correctChars / 5.0;
    const minutes = elapsed / 60.0;
    const wpm = minutes > 0 ? words / minutes : 0;

    this.state.mode = "RESULTS";
    this.state.resultsText = `Speed test complete. WPM ${wpm.toFixed(1)}. Accuracy ${acc.toFixed(1)} percent. Press Enter to repeat, or Escape for menu.`;

    this.renderResults();
    this.announceAlert(this.state.resultsText, true, 3.0);
  }

  handleTestKey(e) {
    if (e.key === "Escape") {
      this.showMenu();
      return;
    }

    // Ctrl+Space repeats remaining text
    if (e.key === " " && e.ctrlKey) {
      e.preventDefault();
      const current = this.state.test.current;
      const typed = this.state.test.typed;
      const remaining = current.substring(typed.length);
      this.announceAlert(remaining || current, true);
      return;
    }

    const t = this.state.test;

    // Start timer on first keystroke
    if (!t.startTime && e.key.length === 1) {
      t.startTime = Date.now();
      t.running = true;
    }

    // Backspace
    if (e.key === "Backspace") {
      e.preventDefault();
      t.typed = t.typed.slice(0, -1);
      this.renderTest();
      return;
    }

    // Only process printable characters
    if (e.key.length === 1) {
      e.preventDefault();
      const ch = e.key;
      const pos = t.typed.length;

      t.typed += ch;
      t.totalChars++;

      // Check correctness
      if (pos < t.current.length && ch === t.current[pos]) {
        t.correctChars++;
      }

      // Check if sentence complete
      if (t.typed === t.current) {
        this.loadNextSentence();
      } else {
        this.renderTest();
      }
    }
  }

  // ==================== RESULTS ====================

  renderResults() {
    this.rootEl.innerHTML = `
      <div style="max-width:700px;margin:2rem auto;text-align:center;">
        <h2>Results</h2>
        <div style="margin:3rem 0;font-size:1.5rem;line-height:2;">
          ${this.state.resultsText}
        </div>
        <p class="muted">Follow the instructions above</p>
      </div>
    `;
  }

  handleResultsKey(e) {
    if (e.key === "Escape") {
      this.showMenu();
      return;
    }

    if (e.key === " ") {
      e.preventDefault();
      // Space advances stage (if lesson result allows it)
      if (this.state.resultsText.includes("stage")) {
        const newStage = Math.min(this.state.lesson.stage + 1, CONST.STAGE_LETTERS.length - 1);
        this.state.lesson.stage = newStage;
        saveProgress(newStage);
        this.startLesson();
      }
    }

    if (e.key === "Enter") {
      e.preventDefault();
      // Repeat lesson or test
      if (this.state.resultsText.includes("Speed test")) {
        this.startTest();
      } else {
        saveProgress(this.state.lesson.stage);
        this.startLesson();
      }
    }
  }
}

// ==================== BOOT ====================

function boot() {
  initTheme();
  updateBuildFooter();

  const app = new KeyQuestApp();
  app.start();
}

if (document.readyState !== "loading") {
  boot();
} else {
  window.addEventListener("DOMContentLoaded", boot);
}
