"""Currency Manager - Handle coin earning, spending, and balance tracking.

This module manages the virtual currency system where users earn coins
through various typing activities and can spend them in the shop.
"""


# Coin earning rates for different activities
COIN_REWARDS = {
    'lesson_completed': 10,
    'speed_test_finished': 5,
    'sentence_practice_session': 5,  # Per session exit
    'game_played': 5,  # Per game completion
    'new_best_wpm': 50,
    'new_best_accuracy': 25,
    'perfect_lesson': 25,  # 100% accuracy on lesson
    'streak_milestone_7': 100,  # 7 day streak
    'streak_milestone_30': 250,  # 30 day streak
    'streak_milestone_100': 500,  # 100 day streak
    'badge_earned': 50,
    'quest_completed': 75,
    'daily_challenge_completed': 25,
    'level_up': 100,
}


def award_coins(settings, activity: str, multiplier: int = 1) -> int:
    """Award coins for an activity.

    Args:
        settings: Settings object with coins attribute
        activity: Activity name (must be in COIN_REWARDS)
        multiplier: Optional multiplier for the reward

    Returns:
        Number of coins awarded
    """
    if activity not in COIN_REWARDS:
        return 0

    coins_earned = COIN_REWARDS[activity] * multiplier
    settings.coins += coins_earned

    return coins_earned


def can_afford(settings, cost: int) -> bool:
    """Check if user has enough coins for a purchase.

    Args:
        settings: Settings object with coins attribute
        cost: Cost in coins

    Returns:
        True if user can afford, False otherwise
    """
    return settings.coins >= cost


def spend_coins(settings, cost: int) -> bool:
    """Spend coins on a purchase.

    Args:
        settings: Settings object with coins attribute
        cost: Cost in coins

    Returns:
        True if purchase successful, False if insufficient coins
    """
    if not can_afford(settings, cost):
        return False

    settings.coins -= cost
    return True


def get_balance(settings) -> int:
    """Get current coin balance.

    Args:
        settings: Settings object with coins attribute

    Returns:
        Current coin balance
    """
    return settings.coins


def format_balance(coins: int) -> str:
    """Format coin balance for display.

    Args:
        coins: Number of coins

    Returns:
        Formatted string
    """
    if coins == 1:
        return "1 coin"
    else:
        return f"{coins} coins"


def get_total_coins_earned(settings) -> int:
    """Get lifetime total coins earned (includes spent coins).

    Args:
        settings: Settings object

    Returns:
        Total coins earned lifetime
    """
    # Lifetime totals require tracking earned and spent values separately.
    # Current behavior returns the live balance.
    return settings.coins


# Coin earning announcements
def get_coin_announcement(activity: str, coins_earned: int) -> str:
    """Get announcement text for coin earning.

    Args:
        activity: Activity that earned coins
        coins_earned: Number of coins earned

    Returns:
        Announcement text
    """
    announcements = {
        'lesson_completed': f"Lesson complete! Earned {coins_earned} coins.",
        'speed_test_finished': f"Speed test finished! Earned {coins_earned} coins.",
        'sentence_practice_session': f"Practice session complete! Earned {coins_earned} coins.",
        'game_played': f"Game finished! Earned {coins_earned} coins.",
        'new_best_wpm': f"New personal best WPM! Earned {coins_earned} coins!",
        'new_best_accuracy': f"New best accuracy! Earned {coins_earned} coins!",
        'perfect_lesson': f"Perfect lesson! Earned {coins_earned} bonus coins!",
        'streak_milestone_7': f"7 day streak milestone! Earned {coins_earned} coins!",
        'streak_milestone_30': f"30 day streak milestone! Earned {coins_earned} coins!",
        'streak_milestone_100': f"100 day streak milestone! Earned {coins_earned} coins!",
        'badge_earned': f"Badge earned! Received {coins_earned} coins!",
        'quest_completed': f"Quest completed! Earned {coins_earned} coins!",
        'daily_challenge_completed': f"Daily challenge complete! Earned {coins_earned} coins!",
        'level_up': f"Level up! Earned {coins_earned} coins!",
    }

    return announcements.get(activity, f"Earned {coins_earned} coins!")
