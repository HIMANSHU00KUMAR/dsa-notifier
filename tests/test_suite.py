import unittest
import os
import tempfile
import json
from src.history_manager import HistoryManager
from src.formatter import format_whatsapp_message, get_difficulty_badge
from src.config import Config


class TestFormatter(unittest.TestCase):
    def test_difficulty_badge(self):
        self.assertIn("Easy", get_difficulty_badge(900))
        self.assertIn("Medium", get_difficulty_badge(1400))
        self.assertIn("Hard", get_difficulty_badge(1800))
        self.assertIn("Very Hard", get_difficulty_badge(2200))
        self.assertIn("Master", get_difficulty_badge(2600))
        self.assertIn("Unrated", get_difficulty_badge(None))

    def test_message_formatting(self):
        problem = {
            "key": "1872E",
            "contestId": 1872,
            "index": "E",
            "name": "Data Structures Fan",
            "rating": 1500,
            "tags": ["bitmasks", "data structures"],
            "url": "https://codeforces.com/problemset/problem/1872/E",
            "user_rating": 1450,
            "target_range": "1400-1600"
        }
        msg = format_whatsapp_message(problem, handle="test_coder", target_range="1400-1600")
        self.assertIn("1872E", msg)
        self.assertIn("Data Structures Fan", msg)
        self.assertIn("Medium (1500)", msg)
        self.assertIn("https://codeforces.com/problemset/problem/1872/E", msg)
        self.assertIn("@test_coder", msg)
        self.assertIn("DAILY DSA NOTIFIER", msg)


class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_file = os.path.join(self.temp_dir.name, "history.json")
        self.manager = HistoryManager(self.history_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_empty_history(self):
        self.assertEqual(self.manager.load_history(), [])
        self.assertEqual(self.manager.get_excluded_keys(), set())

    def test_record_and_exclude(self):
        prob = {
            "key": "1500A",
            "contestId": 1500,
            "index": "A",
            "name": "Array Problem",
            "rating": 1200,
            "tags": ["math"],
            "url": "https://codeforces.com/problemset/problem/1500/A"
        }
        self.manager.record_problem(prob)
        
        excluded = self.manager.get_excluded_keys()
        self.assertIn("1500A", excluded)
        
        history = self.manager.load_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["key"], "1500A")


class TestConfig(unittest.TestCase):
    def test_whatsapp_validation(self):
        cfg = Config(notification_channel="whatsapp", whatsapp_phone="", callmebot_api_key="")
        errors = cfg.validate()
        self.assertTrue(len(errors) > 0)

        cfg_valid = Config(notification_channel="whatsapp", whatsapp_phone="919876543210", callmebot_api_key="123456")
        errors_valid = cfg_valid.validate()
        self.assertEqual(len(errors_valid), 0)

    def test_ntfy_validation(self):
        cfg_invalid = Config(notification_channel="ntfy", ntfy_topic="")
        self.assertTrue(len(cfg_invalid.validate()) > 0)

        cfg_valid = Config(notification_channel="ntfy", ntfy_topic="my-topic-123")
        self.assertEqual(len(cfg_valid.validate()), 0)

    def test_telegram_validation(self):
        cfg_invalid = Config(notification_channel="telegram", telegram_bot_token="", telegram_chat_id="")
        self.assertTrue(len(cfg_invalid.validate()) > 0)

        cfg_valid = Config(notification_channel="telegram", telegram_bot_token="token123", telegram_chat_id="chat123")
        self.assertEqual(len(cfg_valid.validate()), 0)


if __name__ == "__main__":
    unittest.main()
