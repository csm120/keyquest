"""KeyQuest typing games package.

This package contains fun typing games that help improve typing skills
through engaging gameplay with rich audio feedback.

All games inherit from BaseGame to ensure consistent menu structure,
keyboard navigation, and accessibility features.
"""

from games.base_game import BaseGame
from games.letter_fall import LetterFallGame
from games.hangman import HangmanGame

# List of all available games
__all__ = ['BaseGame', 'LetterFallGame', 'HangmanGame']

# Future games should inherit from BaseGame and be added here:
# from games.typing_race import TypingRaceGame
# from games.word_blaster import WordBlasterGame
# __all__.extend(['TypingRaceGame', 'WordBlasterGame'])
