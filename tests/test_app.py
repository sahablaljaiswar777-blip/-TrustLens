import json
import tempfile
import unittest
from pathlib import Path

from app import create_app
from database.db import add_analysis, dashboard_stats, get_analysis, list_analyses


class FlaskIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "test.sqlite3")
        self.app = create_app({
            "TESTING": True,
            "DATABASE_PATH": self.database_path,
            "SECRET_KEY": "test-key",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_primary_pages_render(self):
        for route in ("/", "/analyze", "/history", "/reports", "/simulation", "/about"):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_analysis_persists_compact_redacted_result_and_detail_routes_work(self):
        response = self.client.post("/analyze", data={
            "message": "Please verify password: topsecret and visit https://example.test/path?token=secret",
            "url": "https://example.test/path?token=secret",
        })
        self.assertEqual(response.status_code, 302)
        detail = self.client.get(response.headers["Location"])
        self.assertEqual(detail.status_code, 200)
        rows = list_analyses(self.database_path)
        self.assertEqual(len(rows), 1)
        self.assertLessEqual(len(rows[0]["preview"]), 240)
        self.assertNotIn("topsecret", rows[0]["preview"])
        self.assertNotIn("token=secret", rows[0]["preview"])
        saved = get_analysis(self.database_path, rows[0]["id"])
        self.assertIsNotNone(saved)
        self.assertNotIn("topsecret", json.dumps(saved["result"]))
        self.assertEqual(self.client.get(f"/reports/{rows[0]['id']}").status_code, 200)

    def test_blank_or_overlong_submission_is_rejected(self):
        blank = self.client.post("/analyze", data={})
        self.assertEqual(blank.status_code, 400)
        too_long = self.client.post("/analyze", data={"message": "x" * 4001})
        self.assertEqual(too_long.status_code, 400)
        self.assertEqual(list_analyses(self.database_path), [])

    def test_simulation_is_fictional_and_saved(self):
        page = self.client.get("/simulation")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b".test", page.data)
        response = self.client.post("/simulation", data={"scenario": "delivery"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(list_analyses(self.database_path)), 1)
        self.assertIn("Simulation:", list_analyses(self.database_path)[0]["title"])

    def test_dashboard_distinguishes_high_risk_and_trusted_counts(self):
        safe_result = {"score": 0, "band": "TRUST", "decision": "TRUST"}
        high_result = {"score": 82, "band": "HIGH RISK", "decision": "STOP"}
        add_analysis(self.database_path, "Safe example", "Compact safe preview", safe_result)
        add_analysis(self.database_path, "High risk example", "Compact high-risk preview", high_result)
        stats = dashboard_stats(self.database_path)
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["high_risk"], 1)
        self.assertEqual(stats["trusted"], 1)
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"High-risk detections", page.data)
        self.assertIn(b"Trusted-range results", page.data)

    def test_history_filter_and_missing_analysis(self):
        self.client.post("/analyze", data={"message": "Ordinary meeting notes."})
        self.assertEqual(self.client.get("/history?band=TRUST").status_code, 200)
        self.assertEqual(self.client.get("/history?band=unknown").status_code, 200)
        self.assertEqual(self.client.get("/result/99999").status_code, 404)
        self.assertEqual(self.client.get("/reports/99999").status_code, 404)


if __name__ == "__main__":
    unittest.main()
