import unittest

from engine.risk_engine import calculate_score, risk_band


class RiskEngineTests(unittest.TestCase):
    def test_score_is_bounded_and_accepts_empty_signals(self):
        self.assertEqual(calculate_score([]), 0)
        self.assertEqual(calculate_score([{"points": 1000, "category": "content"}]), 25)
        self.assertEqual(calculate_score([{"points": 25, "category": "content"}] * 10), 100)

    def test_cross_category_signals_get_deterministic_correlation_bonus(self):
        signals = [
            {"points": 5, "category": "content"},
            {"points": 5, "category": "url"},
        ]
        self.assertEqual(calculate_score(signals), 15)
        self.assertEqual(
            calculate_score(signals + [
                {"points": 5, "category": "sender"},
                {"points": 5, "category": "social_engineering"},
            ]),
            30,
        )

    def test_distinct_signals_within_one_category_get_small_correlation_bonus(self):
        signals = [
            {"points": 18, "category": "url", "name": "shortened_url"},
            {"points": 18, "category": "url", "name": "brand_like_host"},
        ]
        self.assertEqual(calculate_score(signals), 41)
        self.assertEqual(calculate_score(signals * 2), 77)

    def test_risk_band_boundaries(self):
        expected = {
            0: "TRUST",
            19: "TRUST",
            20: "LOW",
            39: "LOW",
            40: "CAUTION",
            59: "CAUTION",
            60: "SUSPICIOUS",
            79: "SUSPICIOUS",
            80: "HIGH RISK",
            94: "HIGH RISK",
            95: "CRITICAL",
            100: "CRITICAL",
        }
        for score, band in expected.items():
            with self.subTest(score=score):
                self.assertEqual(risk_band(score), band)

    def test_out_of_range_scores_are_clamped(self):
        self.assertEqual(risk_band(-10), "TRUST")
        self.assertEqual(risk_band(120), "CRITICAL")


if __name__ == "__main__":
    unittest.main()
