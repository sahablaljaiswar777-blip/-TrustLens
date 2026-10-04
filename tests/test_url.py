import unittest

from engine.report_engine import analyze_submission
from engine.url_analyzer import analyze_url


class UrlAnalyzerTests(unittest.TestCase):
    def test_empty_and_ordinary_https_url_are_not_flagged(self):
        self.assertEqual(analyze_url(""), [])
        self.assertEqual(analyze_url("https://example.com/account"), [])

    def test_http_shortener_and_brand_like_domain_are_flagged(self):
        names = {signal["name"] for signal in analyze_url("http://paypal-secure.bit.ly/login")}
        self.assertIn("unencrypted_http", names)
        self.assertIn("shortened_url", names)
        self.assertIn("brand_like_host", names)

    def test_malformed_url_returns_an_explainable_signal(self):
        names = {signal["name"] for signal in analyze_url("http://[")}
        self.assertIn("invalid_url", names)

    def test_non_web_scheme_is_identified(self):
        names = {signal["name"] for signal in analyze_url("javascript:alert(1)")}
        self.assertIn("unusual_scheme", names)

    def test_userinfo_and_raw_ip_are_detected(self):
        names = {signal["name"] for signal in analyze_url("https://trusted.example@192.0.2.1/login")}
        self.assertIn("userinfo_url", names)
        self.assertIn("ip_host", names)

    def test_correlated_shortener_and_brand_like_url_is_elevated(self):
        result = analyze_submission(url="https://paypal-secure.bit.ly/login")
        self.assertEqual(result["band"], "CAUTION")
        self.assertEqual(result["decision"], "CAUTION")
        self.assertGreaterEqual(result["score"], 40)


if __name__ == "__main__":
    unittest.main()
