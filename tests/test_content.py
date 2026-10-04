import unittest

from engine.content_analyzer import analyze_content
from engine.report_engine import analyze_submission


class ContentAnalyzerTests(unittest.TestCase):
    def test_safe_message_has_no_content_signals(self):
        self.assertEqual(analyze_content("The meeting starts at 10:30 in room 4."), [])
        result = analyze_submission(message="The meeting starts at 10:30 in room 4.")
        self.assertEqual(result["band"], "TRUST")
        self.assertEqual(result["score"], 0)

    def test_suspicious_message_identifies_pressure_and_link_prompt(self):
        signals = analyze_content("Urgent, click this link immediately.")
        names = {signal["name"] for signal in signals}
        self.assertIn("urgent_action", names)
        self.assertIn("link_prompt", names)

    def test_high_risk_message_exposes_multiple_requests(self):
        result = analyze_submission(
            message=(
                "Urgent: your account will be suspended. Click this link immediately. "
                "Enter your password, one-time code, bank details, and social security number. "
                "Pay now with gift cards. You have won a prize; claim your reward."
            )
        )
        self.assertGreaterEqual(result["score"], 80)
        self.assertIn("credential_request", {signal["name"] for signal in result["signals"]})
        self.assertIn("sensitive_data", {signal["name"] for signal in result["signals"]})

    def test_social_engineering_checks_secret_and_bypass_requests(self):
        result = analyze_submission(
            message=(
                "Urgent: verify your password and click this link. "
                "Keep this secret and bypass the usual approval process."
            )
        )
        self.assertEqual(result["band"], "SUSPICIOUS")
        self.assertEqual(result["decision"], "STOP")


if __name__ == "__main__":
    unittest.main()
