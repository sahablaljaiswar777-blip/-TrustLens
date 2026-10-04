import unittest

from engine.decision_engine import decide


class DecisionEngineTests(unittest.TestCase):
    def test_band_to_decision_mapping_at_every_lower_boundary(self):
        expected = {
            0: ("TRUST", "TRUST"),
            20: ("LOW", "VERIFY"),
            40: ("CAUTION", "CAUTION"),
            60: ("SUSPICIOUS", "STOP"),
            80: ("HIGH RISK", "STOP"),
            95: ("CRITICAL", "CRITICAL"),
            100: ("CRITICAL", "CRITICAL"),
        }
        for score, mapping in expected.items():
            with self.subTest(score=score):
                decision = decide(score)
                self.assertEqual((decision["band"], decision["label"]), mapping)
                self.assertTrue(decision["explanation"])
                self.assertTrue(decision["recommendation"])


if __name__ == "__main__":
    unittest.main()
