import pygame
from typing import Optional

# Tutorial progression: beginner-first and adaptive.
# 1) Space intro
# 2) Arrow keys
# 3) Enter
# 4) Control
# 5) Mixed practice
PHASE1_KEYS = [("space", pygame.K_SPACE)]
PHASE2_INTRO_KEYS = [
    ("up", pygame.K_UP),
    ("down", pygame.K_DOWN),
    ("left", pygame.K_LEFT),
    ("right", pygame.K_RIGHT),
]
PHASE2_MIX_KEYS = PHASE1_KEYS + PHASE2_INTRO_KEYS
PHASE3_INTRO_KEYS = [("enter", pygame.K_RETURN)]
PHASE3_MIX_KEYS = PHASE2_MIX_KEYS + PHASE3_INTRO_KEYS
PHASE4_INTRO_KEYS = [("control", pygame.K_LCTRL)]
PHASE4_MIX_KEYS = PHASE3_MIX_KEYS + PHASE4_INTRO_KEYS

TUTORIAL_EACH_COUNT = 3
TUTORIAL_MIX_COUNT = 5

FRIENDLY = {
    "up": "Up Arrow",
    "down": "Down Arrow",
    "left": "Left Arrow",
    "right": "Right Arrow",
    "space": "Space bar",
    "enter": "Enter",
    "control": "Control",
}

HINTS = {
    "up": "Arrow pointing up, above the Down Arrow.",
    "down": "Arrow pointing down, below the Up Arrow.",
    "left": "Arrow pointing left, to the left of Right.",
    "right": "Arrow pointing right, to the right of Left.",
    "space": "Long bar in the middle at the bottom of the keyboard.",
    "enter": "Large key on the right side of the letters.",
    "control": "Bottom left corner of the keyboard.",
}

TACTILE_GUIDE = {
    "space": (
        "Find the long horizontal bar at the bottom center of the keyboard. "
        "Rest both thumbs near the bottom row and sweep gently left and right until you feel the longest key."
    ),
    "up": (
        "Find the arrow key cluster. It feels like an upside-down T shape. "
        "Up Arrow is the top key in that cluster."
    ),
    "down": (
        "In the arrow cluster, Down Arrow is the center key on the bottom row, directly below Up."
    ),
    "left": (
        "In the arrow cluster bottom row, Left Arrow is to the left of Down."
    ),
    "right": (
        "In the arrow cluster bottom row, Right Arrow is to the right of Down."
    ),
    "enter": (
        "Enter is on the right side of the main letter keys. "
        "Move your right hand from the letter area toward the edge and feel for a tall key."
    ),
    "control": (
        "Control is on the bottom row. "
        "Left Control is at the bottom-left corner. "
        "Right Control is near the bottom-right side."
    ),
}

RELATION = {
    ("up", "down"): "Try Down one step below",
    ("down", "up"): "Try Up one step above",
    ("left", "right"): "Try Right the opposite direction",
    ("right", "left"): "Try Left the opposite direction",
    ("space", "up"): "Try Up Arrow above the Down key cluster",
    ("space", "down"): "Try Down Arrow below the Up key",
    ("space", "left"): "Try Left Arrow to the left of Right",
    ("space", "right"): "Try Right Arrow to the right of Left",
    ("up", "enter"): "Try Enter on the right side of the keyboard",
    ("down", "enter"): "Try Enter on the right side",
    ("left", "enter"): "Try Enter near the right edge",
    ("right", "enter"): "Try Enter just to your right from the letters",
    ("enter", "space"): "Try Space the long bar at the bottom",
    ("space", "enter"): "Try Enter on the right side of the keyboard",
}

# Encouragement messages
ENCOURAGEMENT = {
    "correct": ["Great", "Nice", "Perfect", "Excellent", "Well done", "Good job"],
    "streak_3": ["You are on fire", "Three in a row", "Keep it up", "Awesome streak"],
    "streak_5": ["Five correct! Amazing", "You are crushing it", "Fantastic"],
    "stage_complete": ["Stage complete", "You did it", "Moving up", "Great progress"],
    "struggle": ["That is okay", "Keep trying", "You will get it", "Practice helps"],
    "comeback": ["There you go", "Back on track", "Nice recovery"],
}


def phase_keys(phase: int):
    """Return the instructional key set for a tutorial phase."""
    if phase == 1:
        return PHASE1_KEYS
    if phase == 2:
        return PHASE2_INTRO_KEYS
    if phase == 3:
        return PHASE3_INTRO_KEYS
    if phase == 4:
        return PHASE4_INTRO_KEYS
    return PHASE4_MIX_KEYS


def input_keyset_for_phase(phase: int):
    """Return keys that should be recognized for guidance in the current phase."""
    if phase == 1:
        return PHASE1_KEYS
    if phase == 2:
        return PHASE2_MIX_KEYS
    if phase == 3:
        return PHASE3_MIX_KEYS
    return PHASE4_MIX_KEYS


def next_mode_from_performance(accuracy: float, mistakes: int) -> str:
    """Decide next phase pace from the previous phase performance."""
    if accuracy >= 0.90 and mistakes <= 2:
        return "fast"
    if accuracy < 0.75 or mistakes >= 6:
        return "slow"
    return "normal"


def _phase_base_count(phase: int, mode: str) -> int:
    fast = {1: 3, 2: 2, 3: 2, 4: 2, 5: 3}
    normal = {1: 5, 2: 3, 3: 3, 4: 3, 5: 5}
    slow = {1: 7, 2: 5, 3: 5, 4: 5, 5: 7}
    if mode == "fast":
        return fast.get(phase, 3)
    if mode == "slow":
        return slow.get(phase, 5)
    return normal.get(phase, 5)


def build_phase_sequence(phase: int, mode: str = "normal", key_errors: Optional[dict] = None):
    """Build adaptive per-phase sequence and target counts.

    Returns:
        tuple[list[tuple[str, int]], dict[str, int]]
    """
    key_errors = key_errors or {}
    keys = phase_keys(phase)
    base_count = _phase_base_count(phase, mode)
    target_counts = {}
    sequence = []

    for name, key in keys:
        extra = min(3, int(key_errors.get(name, 0)) // 3)
        count = base_count + extra
        target_counts[name] = count
        sequence.extend([(name, key)] * count)

    return sequence, target_counts


def get_intro_items_for_phase(phase: int):
    """Return tactile guidance items for intro review before a phase starts."""
    if phase == 1:
        return [("space", TACTILE_GUIDE["space"])]
    if phase == 2:
        return [
            ("up", TACTILE_GUIDE["up"]),
            ("down", TACTILE_GUIDE["down"]),
            ("left", TACTILE_GUIDE["left"]),
            ("right", TACTILE_GUIDE["right"]),
        ]
    if phase == 3:
        return [("enter", TACTILE_GUIDE["enter"])]
    if phase == 4:
        return [("control", TACTILE_GUIDE["control"])]
    return [
        ("space", TACTILE_GUIDE["space"]),
        ("up", TACTILE_GUIDE["up"]),
        ("enter", TACTILE_GUIDE["enter"]),
        ("control", TACTILE_GUIDE["control"]),
    ]
