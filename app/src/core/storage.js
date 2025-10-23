/**
 * Progress persistence using localStorage
 */
const PROGRESS_KEY = "keyquest:progress";

export function loadProgress() {
  try {
    const data = localStorage.getItem(PROGRESS_KEY);
    if (data) {
      const parsed = JSON.parse(data);
      return {
        stage: parseInt(parsed.stage, 10) || 0
      };
    }
  } catch (e) {
    console.warn("Could not load progress:", e);
  }
  return { stage: 0 };
}

export function saveProgress(stage) {
  try {
    const data = { stage: parseInt(stage, 10) };
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(data));
  } catch (e) {
    console.error("Could not save progress:", e);
  }
}
