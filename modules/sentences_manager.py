import os

from modules.app_paths import get_app_dir


DEFAULT_SPEED_TEST_SENTENCES = [
    "Keep going.",
    "Stay relaxed.",
    "Accuracy matters.",
    "Speed will come.",
    "One key at a time.",
    "Build your skills.",
    "Trust the process.",
    "You are improving.",
]


def _load_sentences_file(file_path: str):
    sentences = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                sentences.append(line)
    return sentences


def get_sentence_topics_from_folder(app_dir: str = ""):
    """Load available practice topics from Sentences/*.txt filenames."""
    app_dir = app_dir or get_app_dir()
    sentences_dir = os.path.join(app_dir, "Sentences")
    topics = []
    try:
        if not os.path.isdir(sentences_dir):
            return []
        for entry in os.listdir(sentences_dir):
            if not entry.lower().endswith(".txt"):
                continue
            topic = os.path.splitext(entry)[0]
            if topic.lower() == "speedtest":
                continue
            topics.append(topic)
    except Exception:
        return []

    return sorted(set(topics), key=lambda t: t.lower())


def load_practice_sentences(language: str = "English", fallback_sentences=None, app_dir: str = ""):
    """Load sentences from the Sentences folder based on language/topic selection."""
    app_dir = app_dir or get_app_dir()
    fallback_sentences = list(fallback_sentences or DEFAULT_SPEED_TEST_SENTENCES)

    available_topics = set(get_practice_topics()) | set(get_sentence_topics_from_folder(app_dir=app_dir))
    if language not in available_topics and language != "SpeedTest":
        language = "English"

    filename1 = f"{language}.txt"
    filename2 = f"{language} Sentences.txt"

    file_path1 = os.path.join(app_dir, "Sentences", filename1)
    file_path2 = os.path.join(app_dir, "Sentences", filename2)

    try:
        if os.path.exists(file_path1):
            sentences = _load_sentences_file(file_path1)
            print(f"Loaded {len(sentences)} {language} sentences from {filename1}")
            return sentences
        if os.path.exists(file_path2):
            sentences = _load_sentences_file(file_path2)
            print(f"Loaded {len(sentences)} {language} sentences from {filename2}")
            return sentences

        print(f"File not found: {file_path1} or {file_path2}")
        print(f"Using {len(fallback_sentences)} fallback sentences")
        return list(fallback_sentences)
    except Exception as e:
        print(f"Could not load sentences for {language}: {e}")
        print(f"Using {len(fallback_sentences)} fallback sentences")
        return list(fallback_sentences)


def load_speed_test_sentences(app_dir: str = ""):
    """Load the speed test sentence pool."""
    return load_practice_sentences(
        "SpeedTest",
        fallback_sentences=DEFAULT_SPEED_TEST_SENTENCES,
        app_dir=app_dir,
    )


PRACTICE_TOPICS = [
    "English",
    "Spanish",
    "Windows Commands",
    "JAWS Commands",
    "NVDA Commands",
    "Science Facts",
    "History Facts",
    "Geography",
    "Math Vocabulary",
    "Literature Quotes",
    "Vocabulary Building",
]

PRACTICE_TOPIC_EXPLANATIONS = {
    "English": "Practice with English sentences.",
    "Spanish": "Practice with Spanish sentences.",
    "Windows Commands": "Learn Windows keyboard shortcuts and commands while typing.",
    "JAWS Commands": "Practice JAWS screen reader commands and shortcuts.",
    "NVDA Commands": "Practice NVDA screen reader commands and shortcuts.",
    "Science Facts": "Type interesting science facts while improving your skills.",
    "History Facts": "Learn historical events and dates while practicing typing.",
    "Geography": "Explore world geography facts and locations while typing.",
    "Math Vocabulary": "Practice mathematical terms and concepts.",
    "Literature Quotes": "Type famous quotes from classic literature.",
    "Vocabulary Building": "Build your vocabulary with grade-appropriate words and definitions.",
}


def get_practice_topics():
    """Return the canonical list of practice topic names."""
    return list(PRACTICE_TOPICS)


def get_practice_topic_explanation(topic: str) -> str:
    """Return a short explanation for a practice topic."""
    return PRACTICE_TOPIC_EXPLANATIONS.get(topic, "")
