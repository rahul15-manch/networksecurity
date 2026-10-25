import unittest
from fastapi.testclient import TestClient
from app import app
from networksecurity.pipeline.prediction_pipeline import PredictionPipeline


class TestURLPredictionAPI(unittest.TestCase):
    """
    Integration tests for POST /predict-url API endpoint.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_predict_url_ssrf_protection_blocks_private_destinations(self):
        targets = [
            "http://127.0.0.1:8000/api",
            "http://127.0.0.5",
            "http://localhost:3000",
            "http://169.254.169.254/latest/meta-data",
            "http://10.0.0.5/admin",
            "http://192.168.0.1",
        ]
        for target in targets:
            response = self.client.post("/predict-url", json={"url": target})
            self.assertEqual(
                response.status_code,
                400,
                msg=f"Expected SSRF block for {target}, got {response.status_code}: {response.text}",
            )
            self.assertIn("Security violation", response.json()["detail"])

    def test_predict_url_rejects_invalid_schemes_and_syntax(self):
        invalid_urls = [
            "ftp://anonymous@files.com",
            "file:///etc/hosts",
            "not-a-valid-url",
            "",
        ]
        for target in invalid_urls:
            response = self.client.post("/predict-url", json={"url": target})
            self.assertIn(
                response.status_code,
                (400, 422),
                msg=f"Expected 400 or 422 for {target}, got {response.status_code}",
            )

    def test_predict_url_unsupported_features_when_heuristics_disabled(self):
        payload = {
            "url": "https://example.com",
            "allow_heuristics": False,
            "fetch_network": False,
        }
        response = self.client.post("/predict-url", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "unsupported_features")
        self.assertEqual(data["feature_coverage"], "incomplete")
        self.assertIsNone(data["prediction"])
        self.assertIsNone(data["class_id"])
        self.assertTrue(len(data["unsupported_features"]) > 0)
        self.assertIn("stages", data)

    def test_predict_url_successful_inference_contract(self):
        payload = {
            "url": "https://example.com",
            "allow_heuristics": True,
            "fetch_network": False,
        }
        response = self.client.post("/predict-url", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn(data["prediction"], ("phishing", "legitimate"))
        self.assertIn(data["class_id"], (0, 1))
        self.assertIn(data["feature_coverage"], ("complete", "heuristic"))
        self.assertIn("model_score", data)
        self.assertIsInstance(data["features"], dict)
        self.assertEqual(len(data["features"]), 30)
        self.assertIn("stages", data)
        self.assertIn("url_lexical", data["stages"])
        self.assertIn("dns_tls", data["stages"])
        self.assertIn("html_content", data["stages"])
        self.assertIn("external_intel", data["stages"])

    def test_predict_url_mocked_phishing_fixture_inference(self):
        phish_html = """
        <html>
        <body>
          <form action="mailto:hacker@evil.com"></form>
          <a href="#">Click 1</a>
          <a href="#">Click 2</a>
          <a href="http://foreign-domain.com">Click 3</a>
          <script>window.status = "Bank Login";</script>
          <iframe frameborder="0"></iframe>
        </body>
        </html>
        """
        pipeline = PredictionPipeline()
        res = pipeline.predict_url(
            url="http://192.0.2.1/extremely-long-suspicious-path-login-account-verification-identity?sec=1",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=phish_html,
            mock_dns=False,
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["prediction"], "phishing")
        self.assertEqual(res["class_id"], 0)
        self.assertIsNotNone(res["model_score"])

    def test_predict_url_defaults_to_strict_mode_when_allow_heuristics_omitted(self):
        # When allow_heuristics is not supplied in the API payload, it must default to False
        response = self.client.post("/predict-url", json={"url": "https://example.com", "fetch_network": False})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "unsupported_features")
        self.assertEqual(data["feature_coverage"], "incomplete")
        self.assertIsNone(data["prediction"])
        self.assertIsNone(data["class_id"])
        self.assertGreater(len(data["unsupported_features"]), 0)

    def test_testsafebrowsing_url_regression_rejects_speculative_prediction(self):
        # Target fixture URL must not emit a false legitimate prediction under default strict settings
        response = self.client.post(
            "/predict-url",
            json={"url": "https://testsafebrowsing.appspot.com/s/phishing.html", "fetch_network": False},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "unsupported_features")
        self.assertEqual(data["feature_coverage"], "incomplete")
        self.assertIsNone(data["prediction"])

    def test_testsafebrowsing_heuristic_mode_returns_uncertain_suspicious_verdict(self):
        # Target fixture URL in heuristic mode with credential form must return uncertain / suspicious
        mock_html = """<!DOCTYPE html>
        <html>
        <head><title>Phishing Test</title></head>
        <body>
        <h1>Phishing test page</h1>
        <form method="POST">
          <input type="password" name="pwd" />
          <input type="submit" value="Login" />
        </form>
        </body>
        </html>"""
        pipeline = PredictionPipeline()
        res = pipeline.predict_url(
            url="https://testsafebrowsing.appspot.com/s/phishing.html",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=mock_html,
            mock_dns=True,
        )
        self.assertEqual(res["status"], "uncertain")
        self.assertEqual(res["prediction"], "uncertain")
        self.assertEqual(res["risk_tier"], "SUSPICIOUS / UNVERIFIED")
        self.assertTrue(res["is_heuristic"])
        self.assertNotEqual(res["prediction"], "legitimate")
        self.assertGreater(res["estimated_count"], 0)
        self.assertIn("SFH", str(res["warnings"]))

    def test_api_discloses_heuristic_mode_and_evidence_counts(self):
        response = self.client.post(
            "/predict-url",
            json={"url": "https://example.com", "allow_heuristics": True, "fetch_network": False},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_heuristic"])
        self.assertIn("observed_count", data)
        self.assertIn("estimated_count", data)
        self.assertIn("missing_count", data)
        self.assertGreater(data["observed_count"], 0)
        self.assertGreater(data["estimated_count"], 0)
        self.assertEqual(data["missing_count"], 0)
        self.assertIn("feature_details", data)
        self.assertEqual(len(data["feature_details"]), 30)

    def test_malformed_html_and_missing_dom_handled_safely(self):
        malformed_html = "<<<not valid html>>> <form action='> <a href="
        pipeline = PredictionPipeline()
        res = pipeline.predict_url(
            url="https://example.com/broken",
            allow_heuristics=True,
            fetch_network=False,
            mock_html=malformed_html,
            mock_dns=True,
        )
        self.assertIn(res["status"], ("success", "uncertain"))
        self.assertEqual(len(res["features"]), 30)
        self.assertEqual(res["features"]["URL_of_Anchor"], 0)


if __name__ == "__main__":
    unittest.main()
