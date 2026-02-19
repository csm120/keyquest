"""Badge system for KeyQuest achievements.

Tracks and awards badges for accomplishments like:
- Completing lessons
- Earning stars
- Maintaining streaks
- Achieving high speeds
"""

# Badge definitions
# Each badge has: name, description, emoji/icon
BADGES = {
    "first_lesson": {
        "name": "First Steps",
        "description": "Complete your first lesson",
        "emoji": "🎯",
        "category": "progress"
    },
    "perfect_lesson": {
        "name": "Perfectionist",
        "description": "Earn 3 stars on any lesson",
        "emoji": "⭐",
        "category": "performance"
    },
    "week_streak": {
        "name": "Week Warrior",
        "description": "Practice 7 days in a row",
        "emoji": "🔥",
        "category": "dedication"
    },
    "ten_lessons": {
        "name": "Persistent Learner",
        "description": "Complete 10 different lessons",
        "emoji": "📚",
        "category": "progress"
    },
    "speed_demon_40": {
        "name": "Speed Demon",
        "description": "Type at 40+ WPM",
        "emoji": "⚡",
        "category": "speed"
    },
    "speed_demon_50": {
        "name": "Lightning Fingers",
        "description": "Type at 50+ WPM",
        "emoji": "⚡⚡",
        "category": "speed"
    },
    "month_streak": {
        "name": "Dedication Master",
        "description": "Practice 30 days in a row",
        "emoji": "💪",
        "category": "dedication"
    },
    "accuracy_master": {
        "name": "Accuracy Master",
        "description": "Achieve 98%+ accuracy on 5 lessons",
        "emoji": "🎯",
        "category": "performance"
    },
    "full_keyboard": {
        "name": "Full Keyboard Master",
        "description": "Complete all 33 lessons",
        "emoji": "👑",
        "category": "progress"
    },
    "hundred_streak": {
        "name": "Century Club",
        "description": "Practice 100 days in a row",
        "emoji": "💯",
        "category": "dedication"
    }
}

# Badge categories for organization
BADGE_CATEGORIES = {
    "progress": "Progress Badges",
    "performance": "Performance Badges",
    "speed": "Speed Badges",
    "dedication": "Dedication Badges"
}


def check_badges(settings, lesson_stats: dict = None) -> list:
    """Check if any new badges have been earned.

    Args:
        settings: User settings object with earned_badges, lesson_stars, etc.
        lesson_stats: Optional dict with current lesson stats {accuracy, wpm, duration}

    Returns:
        List of newly earned badge IDs
    """
    newly_earned = []

    # First lesson badge
    if "first_lesson" not in settings.earned_badges:
        if settings.total_lessons_completed >= 1:
            newly_earned.append("first_lesson")

    # Perfect lesson badge (3 stars)
    if "perfect_lesson" not in settings.earned_badges:
        if any(stars == 3 for stars in settings.lesson_stars.values()):
            newly_earned.append("perfect_lesson")

    # Week streak badge
    if "week_streak" not in settings.earned_badges:
        if settings.current_streak >= 7:
            newly_earned.append("week_streak")

    # Month streak badge
    if "month_streak" not in settings.earned_badges:
        if settings.current_streak >= 30:
            newly_earned.append("month_streak")

    # Century streak badge
    if "hundred_streak" not in settings.earned_badges:
        if settings.current_streak >= 100:
            newly_earned.append("hundred_streak")

    # Ten lessons badge
    if "ten_lessons" not in settings.earned_badges:
        # Count unique lessons with at least 1 star
        completed_count = len([l for l, s in settings.lesson_stars.items() if s > 0])
        if completed_count >= 10:
            newly_earned.append("ten_lessons")

    # Full keyboard badge (all 33 lessons)
    if "full_keyboard" not in settings.earned_badges:
        completed_count = len([l for l, s in settings.lesson_stars.items() if s > 0])
        if completed_count >= 33:
            newly_earned.append("full_keyboard")

    # Speed demon badges (40+ and 50+ WPM)
    if "speed_demon_40" not in settings.earned_badges:
        if settings.highest_wpm >= 40:
            newly_earned.append("speed_demon_40")

    if "speed_demon_50" not in settings.earned_badges:
        if settings.highest_wpm >= 50:
            newly_earned.append("speed_demon_50")

    # Accuracy master (98%+ accuracy on 5 lessons)
    if "accuracy_master" not in settings.earned_badges:
        high_accuracy_count = len([a for a in settings.lesson_best_accuracy.values() if a >= 98])
        if high_accuracy_count >= 5:
            newly_earned.append("accuracy_master")

    return newly_earned


def get_badge_info(badge_id: str) -> dict:
    """Get information about a specific badge.

    Args:
        badge_id: Badge identifier

    Returns:
        Dictionary with badge info (name, description, emoji, category)
    """
    return BADGES.get(badge_id, {
        "name": "Unknown Badge",
        "description": "Badge not found",
        "emoji": "❓",
        "category": "unknown"
    })


def format_badge_announcement(badge_id: str) -> str:
    """Format a badge unlock announcement for speech.

    Args:
        badge_id: Badge identifier

    Returns:
        Formatted announcement text
    """
    badge = get_badge_info(badge_id)
    return f"Badge unlocked! {badge['name']}! {badge['description']}"


def format_badge_list(earned_badges: set, show_locked: bool = True) -> str:
    """Format a list of badges for display in a dialog.

    Args:
        earned_badges: Set of earned badge IDs
        show_locked: Whether to show locked badges

    Returns:
        Formatted badge list text
    """
    lines = [
        "🏆 Your Badges 🏆",
        "",
        f"Earned: {len(earned_badges)} of {len(BADGES)}",
        ""
    ]

    # Group badges by category
    for category_id, category_name in BADGE_CATEGORIES.items():
        category_badges = [b_id for b_id, b_info in BADGES.items() if b_info['category'] == category_id]

        if not category_badges:
            continue

        lines.append(f"{category_name}:")

        for badge_id in category_badges:
            badge = BADGES[badge_id]
            if badge_id in earned_badges:
                lines.append(f"  ✓ {badge['emoji']} {badge['name']}")
                lines.append(f"     {badge['description']}")
            elif show_locked:
                lines.append(f"  ☐ {badge['name']} (locked)")
                lines.append(f"     {badge['description']}")

        lines.append("")

    return "\n".join(lines)


def get_badge_count() -> int:
    """Get total number of available badges.

    Returns:
        Total badge count
    """
    return len(BADGES)


def get_earned_badge_count(earned_badges: set) -> int:
    """Get count of earned badges.

    Args:
        earned_badges: Set of earned badge IDs

    Returns:
        Count of earned badges
    """
    return len(earned_badges)
