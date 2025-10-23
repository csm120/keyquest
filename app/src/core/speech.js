/**
 * Speech system using Web Speech API
 * DISABLED by default to allow screen readers to work via ARIA live regions.
 * Users can enable Web Speech manually if needed (future feature).
 * Priority mode prevents critical messages from being interrupted.
 */
export class Speech {
  constructor() {
    this.enabled = false; // Disabled by default - rely on screen reader + ARIA
    this.priorityUntil = 0; // timestamp
    this.synth = window.speechSynthesis;
    this.currentUtterance = null;
  }

  say(text, priority = false, protectSeconds = 0) {
    if (!this.enabled || !text) return;

    const now = Date.now();

    if (priority) {
      this.priorityUntil = now + protectSeconds * 1000;
      // Cancel any current speech for priority messages
      this.synth.cancel();
    } else {
      // Drop non-priority if within protect window
      if (now < this.priorityUntil) {
        return;
      }
    }

    try {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      this.currentUtterance = utterance;
      this.synth.speak(utterance);
    } catch (e) {
      console.error("Speech error:", e);
      // Fallback to console
      console.log("Speech:", text);
    }
  }

  cancel() {
    this.synth.cancel();
  }

  toggle() {
    this.enabled = !this.enabled;
    if (!this.enabled) {
      this.cancel();
    }
    return this.enabled;
  }
}
