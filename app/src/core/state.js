/**
 * Application state management
 */
export class AppState {
  constructor() {
    this.mode = "MENU"; // MENU, TUTORIAL, LESSON, TEST, RESULTS
    this.menuIndex = 0;
    this.menuItems = ["Tutorial", "Lesson", "Speed Test", "Quit"];

    // Lesson state
    this.lesson = {
      stage: 0,
      batchWords: [],
      index: 0,
      typed: ""
    };

    // Tutorial state
    this.tutorial = {
      phase: 1, // 1 = arrows+space, 2 = add enter
      sequence: [],
      index: 0,
      requiredName: "",
      requiredKey: "",
      countsDone: {}
    };

    // Test state
    this.test = {
      running: false,
      startTime: 0,
      current: "",
      remaining: [],
      typed: "",
      correctChars: 0,
      totalChars: 0
    };

    // Results
    this.resultsText = "";
  }
}
