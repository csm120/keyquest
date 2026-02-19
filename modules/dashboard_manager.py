"""Progress Dashboard for KeyQuest Phase 2.

Comprehensive view of improvement over time with audio-based visualization.
"""

from datetime import datetime, timedelta


def record_session(settings, session_data: dict):
    """Record a session in history.

    Args:
        settings: Settings object
        session_data: Dict with date, type, wpm, accuracy, duration
    """
    # Limit history to last 100 sessions
    if len(settings.session_history) >= 100:
        settings.session_history = settings.session_history[-99:]

    session_data["date"] = datetime.now().strftime("%Y-%m-%d")
    settings.session_history.append(session_data)


def get_recent_sessions(settings, days: int = 7) -> list:
    """Get sessions from the last N days.

    Args:
        settings: Settings object
        days: Number of days to look back

    Returns:
        List of session dicts
    """
    if not settings.session_history:
        return []

    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    recent = []
    for session in settings.session_history:
        if session.get("date", "") >= cutoff_str:
            recent.append(session)

    return recent


def calculate_average_wpm(sessions: list) -> float:
    """Calculate average WPM from sessions.

    Args:
        sessions: List of session dicts

    Returns:
        Average WPM or 0.0
    """
    if not sessions:
        return 0.0

    wpm_values = [s.get("wpm", 0) for s in sessions if s.get("wpm", 0) > 0]
    if not wpm_values:
        return 0.0

    return sum(wpm_values) / len(wpm_values)


def calculate_average_accuracy(sessions: list) -> float:
    """Calculate average accuracy from sessions.

    Args:
        sessions: List of session dicts

    Returns:
        Average accuracy or 0.0
    """
    if not sessions:
        return 0.0

    accuracy_values = [s.get("accuracy", 0) for s in sessions if s.get("accuracy", 0) > 0]
    if not accuracy_values:
        return 0.0

    return sum(accuracy_values) / len(accuracy_values)


def format_dashboard(settings) -> str:
    """Generate comprehensive progress dashboard.

    Args:
        settings: Settings object

    Returns:
        Formatted dashboard string
    """
    lines = ["📊 Progress Dashboard\n"]

    # ===== SECTION 1: OVERVIEW =====
    lines.append("=" * 40)
    lines.append("OVERVIEW")
    lines.append("=" * 40)

    # Format practice time
    hours = int(settings.total_practice_time // 3600)
    minutes = int((settings.total_practice_time % 3600) // 60)
    lines.append(f"Total Practice Time: {hours}h {minutes}m")
    lines.append(f"Lessons Completed: {settings.total_lessons_completed}")
    lines.append(f"Current Level: {settings.level}")
    lines.append(f"Current Streak: {settings.current_streak} days")
    if settings.longest_streak > 0:
        lines.append(f"Longest Streak: {settings.longest_streak} days")

    # ===== SECTION 2: SPEED PROGRESS =====
    lines.append("\n" + "=" * 40)
    lines.append("SPEED PROGRESS")
    lines.append("=" * 40)

    if settings.highest_wpm > 0:
        lines.append(f"Best WPM Ever: {settings.highest_wpm:.1f}")

    # Calculate recent averages
    this_week = get_recent_sessions(settings, 7)
    last_week = get_recent_sessions(settings, 14)  # 14 days, then filter 7-14

    # Filter last week to days 7-14
    last_week = [s for s in last_week if s not in this_week]

    if this_week:
        this_week_wpm = calculate_average_wpm(this_week)
        lines.append(f"This Week Average: {this_week_wpm:.1f} WPM")

        if last_week:
            last_week_wpm = calculate_average_wpm(last_week)
            lines.append(f"Last Week Average: {last_week_wpm:.1f} WPM")

            improvement = this_week_wpm - last_week_wpm
            if improvement > 0:
                percentage = (improvement / last_week_wpm * 100.0) if last_week_wpm > 0 else 0
                lines.append(f"Improvement: +{improvement:.1f} WPM ({percentage:.1f}% increase) 📈")
            elif improvement < 0:
                percentage = (abs(improvement) / last_week_wpm * 100.0) if last_week_wpm > 0 else 0
                lines.append(f"Change: {improvement:.1f} WPM ({percentage:.1f}% decrease) 📉")
            else:
                lines.append(f"Consistent performance ✓")

    # ===== SECTION 3: ACCURACY TRENDS =====
    lines.append("\n" + "=" * 40)
    lines.append("ACCURACY TRENDS")
    lines.append("=" * 40)

    if this_week:
        this_week_acc = calculate_average_accuracy(this_week)
        lines.append(f"This Week Average: {this_week_acc:.1f}%")

        if last_week:
            last_week_acc = calculate_average_accuracy(last_week)
            lines.append(f"Last Week Average: {last_week_acc:.1f}%")

            improvement = this_week_acc - last_week_acc
            if improvement > 0:
                lines.append(f"Improvement: +{improvement:.1f}% 📈")
            elif improvement < 0:
                lines.append(f"Change: {improvement:.1f}% 📉")
            else:
                lines.append(f"Consistent accuracy ✓")

    # Count perfect accuracy sessions
    perfect_count = sum(1 for s in settings.session_history if s.get("accuracy", 0) >= 100)
    if perfect_count > 0:
        lines.append(f"Perfect Accuracy Sessions: {perfect_count}")

    # ===== SECTION 4: ACHIEVEMENTS =====
    lines.append("\n" + "=" * 40)
    lines.append("ACHIEVEMENTS")
    lines.append("=" * 40)

    badges_earned = len(settings.earned_badges)
    total_badges = 10  # From badge_manager
    lines.append(f"Badges Earned: {badges_earned} of {total_badges}")

    quests_completed = len(settings.completed_quests)
    total_quests = 10  # From quest_manager
    lines.append(f"Quests Completed: {quests_completed} of {total_quests}")

    # Count total stars
    total_stars = sum(settings.lesson_stars.values())
    max_stars = len(settings.lesson_stars) * 3  # 3 stars per lesson
    if max_stars > 0:
        lines.append(f"Stars Collected: {total_stars} of {max_stars} possible")

    # ===== SECTION 5: MILESTONES =====
    lines.append("\n" + "=" * 40)
    lines.append("MILESTONES")
    lines.append("=" * 40)

    milestones = []

    if settings.total_lessons_completed >= 1:
        milestones.append(f"✓ First Lesson Completed")
    if settings.total_lessons_completed >= 10:
        milestones.append(f"✓ 10 Lessons Completed")
    if settings.total_lessons_completed >= 20:
        milestones.append(f"✓ 20 Lessons Completed")
    if settings.total_lessons_completed >= 33:
        milestones.append(f"✓ All Lessons Completed!")

    if settings.highest_wpm >= 20:
        milestones.append(f"✓ Reached 20 WPM")
    if settings.highest_wpm >= 40:
        milestones.append(f"✓ Reached 40 WPM")
    if settings.highest_wpm >= 60:
        milestones.append(f"✓ Reached 60 WPM")

    if settings.current_streak >= 3:
        milestones.append(f"✓ 3-Day Streak")
    if settings.current_streak >= 7:
        milestones.append(f"✓ 7-Day Streak")
    if settings.current_streak >= 30:
        milestones.append(f"✓ 30-Day Streak!")

    if milestones:
        for milestone in milestones:
            lines.append(milestone)
    else:
        lines.append("Keep practicing to reach milestones!")

    # ===== SECTION 6: NEXT GOALS =====
    lines.append("\n" + "=" * 40)
    lines.append("NEXT GOALS")
    lines.append("=" * 40)

    next_goals = []

    # Lesson goals
    if settings.total_lessons_completed < 10:
        remaining = 10 - settings.total_lessons_completed
        next_goals.append(f"Complete {remaining} more lessons to reach 10 total")
    elif settings.total_lessons_completed < 20:
        remaining = 20 - settings.total_lessons_completed
        next_goals.append(f"Complete {remaining} more lessons to reach 20 total")
    elif settings.total_lessons_completed < 33:
        remaining = 33 - settings.total_lessons_completed
        next_goals.append(f"Complete {remaining} more lessons to finish all!")

    # WPM goals
    if settings.highest_wpm < 20:
        next_goals.append(f"Reach 20 WPM (currently {settings.highest_wpm:.1f})")
    elif settings.highest_wpm < 40:
        next_goals.append(f"Reach 40 WPM (currently {settings.highest_wpm:.1f})")
    elif settings.highest_wpm < 60:
        next_goals.append(f"Reach 60 WPM (currently {settings.highest_wpm:.1f})")

    # Streak goals
    if settings.current_streak < 3:
        next_goals.append(f"Practice 3 days in a row")
    elif settings.current_streak < 7:
        next_goals.append(f"Reach 7-day streak (currently {settings.current_streak})")
    elif settings.current_streak < 30:
        next_goals.append(f"Reach 30-day streak (currently {settings.current_streak})")

    if next_goals:
        for goal in next_goals[:3]:  # Show top 3 goals
            lines.append(f"• {goal}")
    else:
        lines.append("You've achieved all major milestones! Keep practicing!")

    lines.append("\n" + "=" * 40)
    lines.append("Keep up the great work! 🎉")
    lines.append("=" * 40)

    return "\n".join(lines)


def format_weekly_summary(settings) -> str:
    """Generate weekly summary report.

    Args:
        settings: Settings object

    Returns:
        Formatted weekly summary
    """
    this_week = get_recent_sessions(settings, 7)

    if not this_week:
        return "No practice sessions this week. Start practicing to see your weekly summary!"

    lines = ["📅 This Week's Summary\n"]

    # Count sessions
    lines.append(f"Practice Sessions: {len(this_week)}")

    # Total time
    total_time = sum(s.get("duration", 0) for s in this_week)
    minutes = int(total_time // 60)
    lines.append(f"Total Practice Time: {minutes} minutes")

    # Averages
    avg_wpm = calculate_average_wpm(this_week)
    avg_acc = calculate_average_accuracy(this_week)
    lines.append(f"Average WPM: {avg_wpm:.1f}")
    lines.append(f"Average Accuracy: {avg_acc:.1f}%")

    # Best performances
    best_wpm_session = max(this_week, key=lambda s: s.get("wpm", 0), default=None)
    if best_wpm_session and best_wpm_session.get("wpm", 0) > 0:
        lines.append(f"Best WPM: {best_wpm_session['wpm']:.1f}")

    best_acc_session = max(this_week, key=lambda s: s.get("accuracy", 0), default=None)
    if best_acc_session and best_acc_session.get("accuracy", 0) > 0:
        lines.append(f"Best Accuracy: {best_acc_session['accuracy']:.1f}%")

    return "\n".join(lines)
