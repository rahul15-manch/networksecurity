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


if __name__ == "__main__":
    unittest.main()
