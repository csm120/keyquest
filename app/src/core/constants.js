// Game constants ported from Python KeyQuest 9

export const LESSON_BATCH = 8; // practice strings per lesson round
export const TEST_SECONDS = 60; // typing test duration

// Test sentences for speed test
export const TEST_SENTENCES = [
  "Keep going.",
  "Stay relaxed.",
  "Type with care.",
  "Small steps add up.",
  "Find a steady pace.",
  "Focus and breathe.",
  "Hands on home row.",
  "Make few errors.",
  "Stay calm.",
  "You can do this.",
];

// Progressive keyboard lesson stages
export const STAGE_LETTERS = [
  ["a", "s", "d", "f"],        // Stage 0: left-hand home row keys
  ["j", "k"],                   // Stage 1: introduce right-hand index/middle
  ["l", ";"],                   // Stage 2: finish right-hand home row
  ["g", "h"],                   // Stage 3: inner home row
  ["q", "w", "e", "r"],         // Stage 4: left top row
  ["u", "i", "o", "p"],         // Stage 5: right top row
  ["z", "x", "c", "v"],         // Stage 6: left bottom row
  ["n", "m"],                   // Stage 7: right bottom row
  ["b"],                        // Stage 8: center bottom row
  ["t", "y"],                   // Stage 9: mid top row
  ["1", "2", "3", "4", "5"],    // Stage 10: left numbers
  ["6", "7", "8", "9", "0"],    // Stage 11: right numbers
  [",", ".", "'", "/"],         // Stage 12: punctuation
];

// Tutorial configuration
export const TUTORIAL_EACH_COUNT = 3; // 3 of each key per phase

export const PHASE1_KEYS = [
  ["up", "ArrowUp"],
  ["down", "ArrowDown"],
  ["left", "ArrowLeft"],
  ["right", "ArrowRight"],
  ["space", " "],
];

export const PHASE2_KEYS = [
  ...PHASE1_KEYS,
  ["enter", "Enter"]
];

export const FRIENDLY_NAMES = {
  "up": "Up Arrow",
  "down": "Down Arrow",
  "left": "Left Arrow",
  "right": "Right Arrow",
  "space": "Space bar",
  "enter": "Enter",
};

export const HINTS = {
  "up": "Arrow pointing up, above the Down Arrow.",
  "down": "Arrow pointing down, below the Up Arrow.",
  "left": "Arrow pointing left, to the left of Right.",
  "right": "Arrow pointing right, to the right of Left.",
  "space": "Long bar in the middle at the bottom of the keyboard.",
  "enter": "Large key on the right side of the letters; often tall or L‑shaped.",
};

export const RELATIONS = {
  "up-down": "Try Down — one step below.",
  "down-up": "Try Up — one step above.",
  "left-right": "Try Right — the opposite direction.",
  "right-left": "Try Left — the opposite direction.",
  "space-up": "Try Up Arrow — above the Down key cluster.",
  "space-down": "Try Down Arrow — below the Up key.",
  "space-left": "Try Left Arrow — to the left of Right.",
  "space-right": "Try Right Arrow — to the right of Left.",
  "up-enter": "Try Enter — on the right side of the keyboard.",
  "down-enter": "Try Enter — on the right side.",
  "left-enter": "Try Enter — near the right edge, often tall.",
  "right-enter": "Try Enter — just to your right from the letters.",
  "enter-space": "Try Space — the long bar at the bottom.",
};
