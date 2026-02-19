import unittest

from modules import sentences_manager


class TestSentencesManager(unittest.TestCase):
    def test_practice_topics_are_nonempty_and_have_explanations(self):
        topics = sentences_manager.get_practice_topics()
        self.assertTrue(topics)
        self.assertIn("English", topics)
        for topic in topics:
            self.assertIsInstance(topic, str)
            self.assertNotEqual(topic, "")
            self.assertNotEqual(sentences_manager.get_practice_topic_explanation(topic), "")

    def test_unknown_topic_falls_back_to_english(self):
        fallback = ["Fallback sentence."]
        sentences = sentences_manager.load_practice_sentences(
            "Not A Real Topic",
            fallback_sentences=fallback,
            app_dir="__definitely_not_a_real_app_dir__",
        )
        self.assertEqual(sentences, fallback)


if __name__ == "__main__":
    unittest.main()

