"""Shop Manager - Handle shop items, categories, and purchases.

This module manages the in-game shop where users can spend coins
on sound packs, themes, power-ups, pet items, and music.
"""

from typing import Dict, List, Optional


# Shop item definitions
SHOP_ITEMS = {
    # Sound Packs (100 coins each)
    "sound_mechanical": {
        "name": "Mechanical Keyboard Sounds",
        "category": "sound_packs",
        "cost": 100,
        "description": "Realistic mechanical keyboard click sounds for every keystroke."
    },
    "sound_arcade": {
        "name": "Retro Arcade Sounds",
        "category": "sound_packs",
        "cost": 100,
        "description": "Classic arcade game sounds including beeps, bloops, and power-ups."
    },
    "sound_scifi": {
        "name": "Sci-Fi Future Sounds",
        "category": "sound_packs",
        "cost": 100,
        "description": "Futuristic electronic sounds with digital effects."
    },
    "sound_nature": {
        "name": "Nature Sounds",
        "category": "sound_packs",
        "cost": 100,
        "description": "Peaceful nature sounds including birds, water, and wind."
    },
    "sound_musical": {
        "name": "Musical Notes",
        "category": "sound_packs",
        "cost": 100,
        "description": "Musical scale notes that play as you type."
    },

    # Visual Themes (200 coins each)
    "theme_cyberpunk": {
        "name": "Neon Cyberpunk Theme",
        "category": "themes",
        "cost": 200,
        "description": "Vibrant neon colors with a futuristic cyberpunk aesthetic."
    },
    "theme_terminal": {
        "name": "Retro Terminal Theme",
        "category": "themes",
        "cost": 200,
        "description": "Classic green on black terminal look from the 1980s."
    },
    "theme_forest": {
        "name": "Forest Green Theme",
        "category": "themes",
        "cost": 200,
        "description": "Calming forest greens and earth tones."
    },
    "theme_ocean": {
        "name": "Ocean Blue Theme",
        "category": "themes",
        "cost": 200,
        "description": "Deep ocean blues and aqua accents."
    },
    "theme_galaxy": {
        "name": "Space Galaxy Theme",
        "category": "themes",
        "cost": 200,
        "description": "Dark space theme with purple and blue nebula colors."
    },

    # Power-Ups (25-50 coins)
    "powerup_hint": {
        "name": "Hint Token",
        "category": "powerups",
        "cost": 25,
        "description": "Reveals the next letter in a difficult sequence. Single use.",
        "consumable": True
    },
    "powerup_freeze": {
        "name": "Streak Freeze",
        "category": "powerups",
        "cost": 50,
        "description": "Protects your daily streak for one missed day. Single use.",
        "consumable": True
    },
    "powerup_time": {
        "name": "Time Extension",
        "category": "powerups",
        "cost": 30,
        "description": "Adds 30 seconds to your next speed test. Single use.",
        "consumable": True
    },

    # Pet Items (varies)
    "pet_food_basic": {
        "name": "Basic Pet Food",
        "category": "pet_items",
        "cost": 10,
        "description": "Feed your pet to keep them happy. +5 happiness.",
        "consumable": True
    },
    "pet_food_premium": {
        "name": "Premium Pet Food",
        "category": "pet_items",
        "cost": 25,
        "description": "Delicious premium food your pet loves. +15 happiness.",
        "consumable": True
    },
    "pet_toy_ball": {
        "name": "Bouncy Ball",
        "category": "pet_items",
        "cost": 25,
        "description": "A fun toy for your pet to play with."
    },
    "pet_toy_laser": {
        "name": "Laser Pointer",
        "category": "pet_items",
        "cost": 50,
        "description": "Endless entertainment for your pet."
    },
    "pet_accessory_hat": {
        "name": "Tiny Hat",
        "category": "pet_items",
        "cost": 75,
        "description": "A cute hat for your pet to wear."
    },
    "pet_accessory_bowtie": {
        "name": "Fancy Bowtie",
        "category": "pet_items",
        "cost": 75,
        "description": "Make your pet look dapper with a bowtie."
    },
    "pet_accessory_wings": {
        "name": "Angel Wings",
        "category": "pet_items",
        "cost": 100,
        "description": "Majestic wings for your pet."
    },

    # Background Music (150 coins each)
    "music_classical": {
        "name": "Classical Focus",
        "category": "music",
        "cost": 150,
        "description": "Relaxing classical music to help you focus while typing."
    },
    "music_lofi": {
        "name": "Lo-Fi Beats",
        "category": "music",
        "cost": 150,
        "description": "Chill lo-fi hip hop beats for concentration."
    },
    "music_ambient": {
        "name": "Ambient Space",
        "category": "music",
        "cost": 150,
        "description": "Ethereal ambient soundscapes."
    },
    "music_chiptune": {
        "name": "Chiptune Adventure",
        "category": "music",
        "cost": 150,
        "description": "Upbeat 8-bit chiptune music."
    },
}


# Category information
SHOP_CATEGORIES = {
    "sound_packs": {
        "name": "Sound Packs",
        "description": "Change the sounds you hear while typing"
    },
    "themes": {
        "name": "Visual Themes",
        "description": "Customize the look of KeyQuest"
    },
    "powerups": {
        "name": "Power-Ups",
        "description": "Helpful boosts for your typing practice"
    },
    "pet_items": {
        "name": "Pet Items",
        "description": "Feed, play with, and accessorize your pet"
    },
    "music": {
        "name": "Background Music",
        "description": "Relaxing music tracks to practice with"
    },
}


def get_category_items(category: str) -> List[str]:
    """Get all item IDs in a category.

    Args:
        category: Category name

    Returns:
        List of item IDs in that category
    """
    return [item_id for item_id, item in SHOP_ITEMS.items() if item["category"] == category]


def get_item_info(item_id: str) -> Optional[Dict]:
    """Get information about a shop item.

    Args:
        item_id: Item identifier

    Returns:
        Item info dict or None if not found
    """
    return SHOP_ITEMS.get(item_id)


def is_owned(settings, item_id: str) -> bool:
    """Check if user owns an item.

    Args:
        settings: Settings object with owned_items
        item_id: Item identifier

    Returns:
        True if owned, False otherwise
    """
    return item_id in settings.owned_items


def is_consumable(item_id: str) -> bool:
    """Check if an item is consumable (can be purchased multiple times).

    Args:
        item_id: Item identifier

    Returns:
        True if consumable, False otherwise
    """
    item = get_item_info(item_id)
    return item and item.get("consumable", False)


def can_purchase(settings, item_id: str) -> tuple[bool, str]:
    """Check if user can purchase an item.

    Args:
        settings: Settings object
        item_id: Item identifier

    Returns:
        Tuple of (can_purchase, reason)
    """
    item = get_item_info(item_id)

    if not item:
        return False, "Item not found"

    # Check if already owned (unless consumable)
    if not is_consumable(item_id) and is_owned(settings, item_id):
        return False, "Already owned"

    # Check if can afford
    if settings.coins < item["cost"]:
        return False, f"Insufficient coins. Need {item['cost']}, have {settings.coins}"

    return True, "OK"


def purchase_item(settings, item_id: str) -> tuple[bool, str]:
    """Purchase an item from the shop.

    Args:
        settings: Settings object
        item_id: Item identifier

    Returns:
        Tuple of (success, message)
    """
    can_buy, reason = can_purchase(settings, item_id)

    if not can_buy:
        return False, reason

    item = get_item_info(item_id)

    # Deduct coins
    settings.coins -= item["cost"]

    # Add to owned items (or inventory for consumables)
    if is_consumable(item_id):
        # For consumables, track quantity in inventory
        if item_id not in settings.inventory:
            settings.inventory[item_id] = 0
        settings.inventory[item_id] += 1
        return True, f"Purchased {item['name']}! You now have {settings.inventory[item_id]}."
    else:
        # For permanent items, add to owned_items
        settings.owned_items.add(item_id)
        return True, f"Purchased {item['name']}!"


def use_consumable(settings, item_id: str) -> tuple[bool, str]:
    """Use a consumable item from inventory.

    Args:
        settings: Settings object
        item_id: Item identifier

    Returns:
        Tuple of (success, message)
    """
    if not is_consumable(item_id):
        return False, "Item is not consumable"

    if item_id not in settings.inventory or settings.inventory[item_id] <= 0:
        return False, "You don't have any of this item"

    settings.inventory[item_id] -= 1

    item = get_item_info(item_id)
    return True, f"Used {item['name']}!"


def get_inventory_count(settings, item_id: str) -> int:
    """Get quantity of consumable item in inventory.

    Args:
        settings: Settings object
        item_id: Item identifier

    Returns:
        Quantity owned
    """
    return settings.inventory.get(item_id, 0)


def format_item_display(item_id: str, owned: bool, quantity: int = 0) -> str:
    """Format item for display in shop.

    Args:
        item_id: Item identifier
        owned: Whether user owns the item
        quantity: For consumables, how many they own

    Returns:
        Formatted string
    """
    item = get_item_info(item_id)
    if not item:
        return ""

    status = ""
    if is_consumable(item_id):
        if quantity > 0:
            status = f" (Owned: {quantity})"
    else:
        if owned:
            status = " [OWNED]"

    return f"{item['name']} - {item['cost']} coins{status}"
