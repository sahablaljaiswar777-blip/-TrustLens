import unittest

from engine.report_engine import analyze_submission
from engine.sender_analyzer import analyze_sender


class SenderAnalyzerTests(unittest.TestCase):
    def test_matching_sender_text_does_not_raise_mismatch(self):
        self.assertEqual(analyze_sender("alerts@examplebank.test", "Example Bank"), [])

    def test_mismatched_sender_domain_is_explained(self):
        signals = analyze_sender("security@unrelated-mail.test", "Example Bank")
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["name"], "sender_org_mismatch")
        self.assertEqual(signals[0]["category"], "sender")
        self.assertIn("does not obviously match", signals[0]["reason"])

    def test_report_correlates_content_url_and_sender_categories(self):
        result = analyze_submission(
            message="Urgent: verify your password and click this link.",
            url="http://paypal-secure.bit.ly/login",
            sender="security@unrelated-mail.test",
            claimed_organization="Example Bank",
        )
        self.assertEqual(
            set(result["categories"]),
            {"content", "url", "sender"},
        )
        self.assertGreater(result["score"], 80)
        self.assertEqual(result["band"], "CRITICAL")
        self.assertEqual(result["decision"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
