
import unittest
from pathlib import Path

from src.parser import ForumParser


class TestForumParser(unittest.TestCase):

    def setUp(self):
        self.parser = ForumParser()

        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "habr_comments.html"
        )

        self.html = fixture_path.read_text(
            encoding="utf-8"
        )

    def tearDown(self):
        self.parser.close()

    def test_parse_html_success(self):
        result = self.parser.parse_html(self.html)

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]["id"], 1001)
        self.assertEqual(result[0]["name"], "ivan")

        self.assertIn(
            "Отличная статья!",
            result[0]["message"]
        )

    def test_parse_html_preserves_html(self):
        result = self.parser.parse_html(self.html)

        message = result[1]["message"]

        self.assertIn("<strong>", message)
        self.assertIn("Буду пробовать.", message)


if __name__ == "__main__":
    unittest.main()
