"""Pet Manager - Handle virtual pet system with growth, evolution, and moods.

This module manages the virtual pet companion that grows with the user's
typing practice, has moods, and provides encouragement.
"""

from typing import Dict, Optional, List
import datetime


# Pet type definitions
PET_TYPES = {
    "robot": {
        "name": "Robot",
        "theme": "Technology",
        "description": "A helpful robot companion that loves efficiency and precision.",
        "stages": {
            1: {"name": "Basic Bot", "xp_required": 0},
            2: {"name": "Upgraded Bot", "xp_required": 500},
            3: {"name": "Advanced Bot", "xp_required": 2000},
            4: {"name": "Elite Bot", "xp_required": 5000},
            5: {"name": "Supreme Bot", "xp_required": 10000},
        }
    },
    "dragon": {
        "name": "Dragon",
        "theme": "Fantasy",
        "description": "A majestic dragon that grows more powerful with every lesson.",
        "stages": {
            1: {"name": "Baby Dragon", "xp_required": 0},
            2: {"name": "Young Dragon", "xp_required": 500},
            3: {"name": "Adult Dragon", "xp_required": 2000},
            4: {"name": "Elder Dragon", "xp_required": 5000},
            5: {"name": "Ancient Dragon", "xp_required": 10000},
        }
    },
    "owl": {
        "name": "Owl",
        "theme": "Wisdom",
        "description": "A wise owl that values knowledge and careful practice.",
        "stages": {
            1: {"name": "Owlet", "xp_required": 0},
            2: {"name": "Young Owl", "xp_required": 500},
            3: {"name": "Wise Owl", "xp_required": 2000},
            4: {"name": "Sage Owl", "xp_required": 5000},
            5: {"name": "Grand Owl", "xp_required": 10000},
        }
    },
    "cat": {
        "name": "Cat",
        "theme": "Cute",
        "description": "An adorable cat that purrs with satisfaction at your progress.",
        "stages": {
            1: {"name": "Kitten", "xp_required": 0},
            2: {"name": "Young Cat", "xp_required": 500},
            3: {"name": "Adult Cat", "xp_required": 2000},
            4: {"name": "Majestic Cat", "xp_required": 5000},
            5: {"name": "Legendary Cat", "xp_required": 10000},
        }
    },
    "dog": {
        "name": "Dog",
        "theme": "Loyal",
        "description": "A faithful dog companion that cheers you on with every keystroke.",
        "stages": {
            1: {"name": "Puppy", "xp_required": 0},
            2: {"name": "Young Dog", "xp_required": 500},
            3: {"name": "Adult Dog", "xp_required": 2000},
            4: {"name": "Champion Dog", "xp_required": 5000},
            5: {"name": "Legendary Dog", "xp_required": 10000},
        }
    },
    "phoenix": {
        "name": "Phoenix",
        "theme": "Epic",
        "description": "A legendary phoenix that rises from the ashes of your mistakes.",
        "stages": {
            1: {"name": "Phoenix Spark", "xp_required": 0},
            2: {"name": "Rising Phoenix", "xp_required": 500},
            3: {"name": "Blazing Phoenix", "xp_required": 2000},
            4: {"name": "Radiant Phoenix", "xp_required": 5000},
            5: {"name": "Eternal Phoenix", "xp_required": 10000},
        }
    },
    "tribble": {
        "name": "Tribble",
        "theme": "Star Trek",
        "description": "A fuzzy tribble that coos happily when you practice.",
        "stages": {
            1: {"name": "Tiny Tribble", "xp_required": 0},
            2: {"name": "Tribble", "xp_required": 500},
            3: {"name": "Big Tribble", "xp_required": 2000},
            4: {"name": "Giant Tribble", "xp_required": 5000},
            5: {"name": "Mega Tribble", "xp_required": 10000},
        }
    },
}


# Pet mood definitions
PET_MOODS = {
    "happy": {
        "name": "Happy",
        "description": "Your pet is content and cheerful!",
        "trigger": "good_performance",
        "messages": [
            "Great typing today!",
            "You're doing amazing!",
            "I'm so proud of you!",
            "Keep up the excellent work!",
            "You're getting better every day!",
        ]
    },
    "excited": {
        "name": "Excited",
        "description": "Your pet is thrilled by your achievement!",
        "trigger": "new_record",
        "messages": [
            "WOW! That was incredible!",
            "You just set a new record!",
            "I knew you could do it!",
            "That's the best I've ever seen you type!",
            "You're absolutely amazing!",
        ]
    },
    "tired": {
        "name": "Tired",
        "description": "Your pet needs rest from the long session.",
        "trigger": "long_session",
        "messages": [
            "Maybe it's time for a break?",
            "I'm getting a bit tired...",
            "You've been practicing for a while now.",
            "How about a short rest?",
            "Don't forget to take breaks!",
        ]
    },
    "sad": {
        "name": "Sad",
        "description": "Your pet is feeling down.",
        "trigger": "streak_broken",
        "messages": [
            "It's okay, everyone has off days.",
            "Don't give up! You can do this!",
            "Tomorrow is a new opportunity!",
            "I believe in you!",
            "You'll get back on track!",
        ]
    },
    "encouraging": {
        "name": "Encouraging",
        "description": "Your pet wants to help you improve.",
        "trigger": "struggling",
        "messages": [
            "Take your time, you've got this!",
            "Focus on accuracy first!",
            "Every mistake is a chance to learn!",
            "You're improving with every try!",
            "Don't rush, just do your best!",
        ]
    },
}


def get_pet_info(pet_type: str) -> Optional[Dict]:
    """Get information about a pet type.

    Args:
        pet_type: Pet type identifier

    Returns:
        Pet info dict or None if not found
    """
    return PET_TYPES.get(pet_type)


def calculate_pet_stage(pet_xp: int) -> int:
    """Calculate pet stage based on XP.

    Args:
        pet_xp: Pet's total XP

    Returns:
        Pet stage (1-5)
    """
    if pet_xp >= 10000:
        return 5
    elif pet_xp >= 5000:
        return 4
    elif pet_xp >= 2000:
        return 3
    elif pet_xp >= 500:
        return 2
    else:
        return 1


def get_pet_stage_info(pet_type: str, stage: int) -> Optional[Dict]:
    """Get stage information for a pet.

    Args:
        pet_type: Pet type identifier
        stage: Stage number (1-5)

    Returns:
        Stage info dict or None if not found
    """
    pet = get_pet_info(pet_type)
    if not pet:
        return None

    return pet["stages"].get(stage)


def xp_to_next_stage(pet_xp: int, current_stage: int) -> int:
    """Calculate XP needed for next stage.

    Args:
        pet_xp: Current pet XP
        current_stage: Current stage (1-5)

    Returns:
        XP needed for next stage (0 if at max stage)
    """
    if current_stage >= 5:
        return 0

    next_stage_xp = {
        1: 500,
        2: 2000,
        3: 5000,
        4: 10000,
        5: 0
    }

    return max(0, next_stage_xp[current_stage] - pet_xp)


def check_evolution(old_xp: int, new_xp: int) -> Dict:
    """Check if pet evolved.

    Args:
        old_xp: Previous XP
        new_xp: New XP

    Returns:
        Dict with evolution info: {evolved: bool, new_stage: int}
    """
    old_stage = calculate_pet_stage(old_xp)
    new_stage = calculate_pet_stage(new_xp)

    return {
        "evolved": new_stage > old_stage,
        "old_stage": old_stage,
        "new_stage": new_stage
    }


def determine_mood(settings, recent_performance: Dict) -> str:
    """Determine pet's current mood based on user's performance.

    Args:
        settings: Settings object
        recent_performance: Dict with performance data:
            {
                "new_best_wpm": bool,
                "new_best_accuracy": bool,
                "accuracy": float,
                "session_duration": float (minutes),
                "streak_broken": bool
            }

    Returns:
        Mood identifier
    """
    # Check for specific triggers
    if recent_performance.get("streak_broken"):
        return "sad"

    if recent_performance.get("new_best_wpm") or recent_performance.get("new_best_accuracy"):
        return "excited"

    if recent_performance.get("session_duration", 0) > 30:  # More than 30 minutes
        return "tired"

    accuracy = recent_performance.get("accuracy", 0)
    if accuracy < 70:
        return "encouraging"

    # Default to happy
    return "happy"


def get_mood_message(mood: str) -> str:
    """Get a random message for a mood.

    Args:
        mood: Mood identifier

    Returns:
        Message string
    """
    import random

    mood_info = PET_MOODS.get(mood, PET_MOODS["happy"])
    return random.choice(mood_info["messages"])


def feed_pet(settings, food_type: str = "basic") -> Dict:
    """Feed the pet.

    Args:
        settings: Settings object with pet data
        food_type: "basic" or "premium"

    Returns:
        Dict with result: {success: bool, message: str, happiness_gain: int}
    """
    happiness_gain = 5 if food_type == "basic" else 15

    # Update pet happiness (capped at 100)
    if not hasattr(settings, 'pet_happiness'):
        settings.pet_happiness = 50  # Default starting happiness

    settings.pet_happiness = min(100, settings.pet_happiness + happiness_gain)

    # Update last fed time
    settings.pet_last_fed = datetime.datetime.now().isoformat()

    return {
        "success": True,
        "message": f"Your pet enjoyed the food! Happiness +{happiness_gain}",
        "happiness_gain": happiness_gain,
        "new_happiness": settings.pet_happiness
    }


def get_pet_status(settings) -> Dict:
    """Get current pet status.

    Args:
        settings: Settings object with pet data

    Returns:
        Dict with pet status information
    """
    pet_type = getattr(settings, "pet_type", "")
    if not pet_type or pet_type not in PET_TYPES:
        return {
            "has_pet": False,
            "message": "You haven't chosen a pet yet!"
        }

    stage = calculate_pet_stage(getattr(settings, "pet_xp", 0))
    pet_info = get_pet_info(pet_type)
    stage_info = get_pet_stage_info(pet_type, stage)
    if not pet_info or not stage_info:
        return {
            "has_pet": False,
            "message": "Your saved pet data is invalid. Please choose a pet again."
        }

    return {
        "has_pet": True,
        "pet_type": pet_type,
        "pet_name": settings.pet_name or pet_info["name"],
        "stage": stage,
        "stage_name": stage_info["name"],
        "xp": getattr(settings, "pet_xp", 0),
        "xp_to_next": xp_to_next_stage(getattr(settings, "pet_xp", 0), stage),
        "happiness": getattr(settings, 'pet_happiness', 50),
        "mood": getattr(settings, 'pet_mood', "happy"),
    }


def choose_pet(settings, pet_type: str, pet_name: str = "") -> Dict:
    """Choose a pet.

    Args:
        settings: Settings object
        pet_type: Pet type identifier
        pet_name: Optional custom name

    Returns:
        Dict with result: {success: bool, message: str}
    """
    if pet_type not in PET_TYPES:
        return {
            "success": False,
            "message": f"Invalid pet type: {pet_type}"
        }

    pet_info = get_pet_info(pet_type)

    settings.pet_type = pet_type
    settings.pet_name = pet_name or pet_info["name"]
    settings.pet_xp = 0
    settings.pet_happiness = 50
    settings.pet_mood = "happy"
    settings.pet_last_fed = datetime.datetime.now().isoformat()

    return {
        "success": True,
        "message": f"You chose {settings.pet_name} the {pet_info['name']}! Take good care of them!"
    }


def award_pet_xp(settings, amount: int) -> Dict:
    """Award XP to pet.

    Args:
        settings: Settings object
        amount: XP to award

    Returns:
        Dict with evolution info
    """
    if not settings.pet_type:
        return {"has_pet": False}

    old_xp = settings.pet_xp
    settings.pet_xp += amount

    evolution = check_evolution(old_xp, settings.pet_xp)

    return {
        "has_pet": True,
        "xp_awarded": amount,
        "total_xp": settings.pet_xp,
        **evolution
    }


def apply_session_pet_progress(settings, recent_performance: Dict, xp_amount: int) -> Dict:
    """Apply pet mood and XP updates for a completed typing session.

    Args:
        settings: Settings object with pet fields
        recent_performance: Performance data used for mood selection
        xp_amount: Pet XP to award for this session

    Returns:
        Dict with mood/evolution results
    """
    if not getattr(settings, "pet_type", ""):
        return {"has_pet": False}

    previous_mood = getattr(settings, "pet_mood", "happy")
    mood = determine_mood(settings, recent_performance)
    settings.pet_mood = mood
    mood_changed = mood != previous_mood

    # Small passive happiness drift based on session outcome.
    current_happiness = getattr(settings, "pet_happiness", 50)
    if mood in ("happy", "excited"):
        current_happiness = min(100, current_happiness + 1)
    elif mood == "tired":
        current_happiness = max(0, current_happiness - 1)
    elif mood == "sad":
        current_happiness = max(0, current_happiness - 2)
    settings.pet_happiness = current_happiness

    xp_result = award_pet_xp(settings, max(0, int(xp_amount)))

    return {
        "has_pet": True,
        "mood": mood,
        "mood_changed": mood_changed,
        "mood_message": get_mood_message(mood),
        "happiness": settings.pet_happiness,
        **xp_result,
    }
