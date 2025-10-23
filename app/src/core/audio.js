/**
 * Audio feedback system for correct/incorrect typing
 * Uses Web Audio API to generate simple tones
 */
export class Audio {
  constructor() {
    this.context = null;
    try {
      this.context = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
      console.warn("Web Audio API not available");
    }
  }

  playTone(frequency, duration) {
    if (!this.context) return;

    try {
      const oscillator = this.context.createOscillator();
      const gainNode = this.context.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(this.context.destination);

      oscillator.frequency.value = frequency;
      oscillator.type = 'sine';

      // Envelope to avoid clicks
      const now = this.context.currentTime;
      gainNode.gain.setValueAtTime(0, now);
      gainNode.gain.linearRampToValueAtTime(0.3, now + 0.01);
      gainNode.gain.linearRampToValueAtTime(0, now + duration);

      oscillator.start(now);
      oscillator.stop(now + duration);
    } catch (e) {
      console.error("Audio error:", e);
    }
  }

  beepOk() {
    this.playTone(1200, 0.07); // Pleasant ding
  }

  beepBad() {
    this.playTone(300, 0.1); // Lower tone for error
  }
}
