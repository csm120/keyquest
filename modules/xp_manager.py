"""XP and Level system for KeyQuest Phase 2.

Manages experience points, level progression, and level-up rewards.
"""

# =========== Level System Configuration ===========

LEVELS = [
    {"level": 1, "name": "Keyboard Novice", "xp_required": 0},
    {"level": 2, "name": "Learning Typist", "xp_required": 500},
    {"level": 3, "name": "Practice Apprentice", "xp_required": 1500},
    {"level": 4, "name": "Competent Typist", "xp_required": 3000},
    {"level": 5, "name": "Intermediate Typist", "xp_required": 5000},
    {"level": 6, "name": "Skilled Typist", "xp_required": 8000},
    {"level": 7, "name": "Advanced Typist", "xp_required": 12000},
    {"level": 8, "name": "Expert Typist", "xp_required": 17000},
    {"level": 9, "name": "Master Typist", "xp_required": 25000},
    {"level": 10, "name": "Keyboard Legend", "xp_required": 35000},
]

# XP Awards for various actions
XP_AWARDS = {
    "keystroke": 1,          # Per correct keystroke
    "lesson": 100,           # Completing a lesson
    "speed_test": 50,        # Completing speed test
    "sentence_practice": 50, # Completing sentence practice
    "perfect_accuracy": 50,  # Bonus for 100% accuracy
    "new_best_wpm": 100,     # New personal best WPM
    "new_best_accuracy": 50, # New personal best accuracy
    "daily_streak": 50,      # Daily streak milestone
    "badge_earned": 75,      # Earning a badge
    "quest_complete": 200,   # Completing a quest
    "daily_challenge": 100,  # Completing daily challenge
    "game_win": 25,          # Winning a game
}


def get_level_info(level: int) -> dict:
    """Get information about a specific level.

    Args:
        level: Level number (1-10)

    Returns:
        Dict with level, name, and xp_required
    """
    if 1 <= level <= 10:
        return LEVELS[level - 1]
    return LEVELS[0]  # Default to level 1


def calculate_level(xp: int) -> int:
    """Calculate current level based on XP.

    Args:
        xp: Total experience points

    Returns:
        Current level (1-10)
    """
    for i in range(len(LEVELS) - 1, -1, -1):
        if xp >= LEVELS[i]["xp_required"]:
            return LEVELS[i]["level"]
    return 1


def xp_to_next_level(current_xp: int, current_level: int) -> int:
    """Calculate XP needed to reach next level.

    Args:
        current_xp: Current total XP
        current_level: Current level

    Returns:
        XP needed for next level (0 if max level)
    """
    if current_level >= 10:
        return 0  # Max level reached

    next_level_info = get_level_info(current_level + 1)
    return next_level_info["xp_required"] - current_xp


def check_level_up(old_xp: int, new_xp: int) -> dict:
    """Check if XP gain resulted in level up.

    Args:
        old_xp: XP before gain
        new_xp: XP after gain

    Returns:
        Dict with leveled_up (bool), old_level, new_level, level_name
    """
    old_level = calculate_level(old_xp)
    new_level = calculate_level(new_xp)

    return {
        "leveled_up": new_level > old_level,
        "old_level": old_level,
        "new_level": new_level,
        "level_name": get_level_info(new_level)["name"]
    }


def award_xp(settings, xp_amount: int, reason: str = "") -> dict:
    """Award XP to the player and check for level up.

    Args:
        settings: Settings object from state
        xp_amount: Amount of XP to award
        reason: Reason for XP award (for logging/display)

    Returns:
        Dict with xp_gained, total_xp, leveled_up, new_level, level_name
    """
    old_xp = settings.xp
    settings.xp += xp_amount

    level_info = check_level_up(old_xp, settings.xp)

    # Update level in settings
    settings.level = level_info["new_level"]

    return {
        "xp_gained": xp_amount,
        "total_xp": settings.xp,
        "reason": reason,
        "leveled_up": level_info["leveled_up"],
        "old_level": level_info["old_level"],
        "new_level": level_info["new_level"],
        "level_name": level_info["level_name"]
    }


def get_progress_to_next_level(xp: int, level: int) -> dict:
    """Get progress toward next level as percentage.

    Args:
        xp: Current total XP
        level: Current level

    Returns:
        Dict with current_level_xp, next_level_xp, xp_in_level, percentage
    """
    if level >= 10:
        return {
            "current_level_xp": LEVELS[9]["xp_required"],
            "next_level_xp": LEVELS[9]["xp_required"],
            "xp_in_level": 0,
            "percentage": 100.0
        }

    current_level_xp = get_level_info(level)["xp_required"]
    next_level_xp = get_level_info(level + 1)["xp_required"]
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp

    percentage = (xp_in_level / xp_needed * 100.0) if xp_needed > 0 else 100.0

    return {
        "current_level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
        "percentage": percentage
    }


def format_xp_display(settings) -> str:
    """Format XP and level info for display.

    Args:
        settings: Settings object

    Returns:
        Formatted string with level and XP info
    """
    level_info = get_level_info(settings.level)
    progress = get_progress_to_next_level(settings.xp, settings.level)

    if settings.level >= 10:
        return f"Level {settings.level}: {level_info['name']}\n" \
               f"XP: {settings.xp:,} (MAX LEVEL)"

    return f"Level {settings.level}: {level_info['name']}\n" \
           f"XP: {settings.xp:,} / {progress['next_level_xp']:,}\n" \
           f"Progress: {progress['percentage']:.1f}% to Level {settings.level + 1}"
