import json
import os
import unittest
from fastapi.testclient import TestClient

from api.index import app
from networksecurity.pipeline.prediction_pipeline import PredictionPipeline


class TestVercelDeploymentCompatibility(unittest.TestCase):
    """
    Verification tests for Vercel serverless deployment and API routing.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_vercel_config_files_exist_and_valid(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Check vercel.json
        vercel_json_path = os.path.join(root_dir, "vercel.json")
        self.assertTrue(os.path.exists(vercel_json_path), "vercel.json must exist in root")
        with open(vercel_json_path, "r") as f:
            v_config = json.load(f)
        self.assertEqual(v_config.get("outputDirectory"), "frontend/dist")
        self.assertIn("rewrites", v_config)

        # Check .python-version (forces prebuilt wheels on Python 3.12)
        py_ver_path = os.path.join(root_dir, ".python-version")
        self.assertTrue(os.path.exists(py_ver_path), ".python-version must exist in root")
        with open(py_ver_path, "r") as f:
            py_ver = f.read().strip()
        self.assertEqual(py_ver, "3.12", "Python version must be pinned to 3.12 for prebuilt binary wheels")

        # Check pyproject.toml requires-python
        pyproject_path = os.path.join(root_dir, "pyproject.toml")
        self.assertTrue(os.path.exists(pyproject_path), "pyproject.toml must exist")
        with open(pyproject_path, "r") as f:
            pyproject_content = f.read()
        self.assertIn('<3.13', pyproject_content, "requires-python must permit Python 3.12 releases (<3.13)")

        # Check uv.lock
        uv_lock_path = os.path.join(root_dir, "uv.lock")
        self.assertTrue(os.path.exists(uv_lock_path), "uv.lock must exist")

        # Check api/requirements.txt
        req_path = os.path.join(root_dir, "api", "requirements.txt")
        self.assertTrue(os.path.exists(req_path), "api/requirements.txt must exist")
        with open(req_path, "r") as f:
            req_content = f.read()
        self.assertIn("scipy==1.15.3", req_content)
        self.assertIn("scikit-learn==1.7.2", req_content)
        self.assertNotIn("mlflow", req_content, "Heavy MLFlow must NOT be in serverless requirements")

        # Check .vercelignore
        v_ignore = os.path.join(root_dir, ".vercelignore")
        self.assertTrue(os.path.exists(v_ignore), ".vercelignore must exist")
        with open(v_ignore, "r") as f:
            ignore_content = f.read()
        self.assertIn("Artifacts/", ignore_content)
        self.assertIn("Network_Data/", ignore_content)

    def test_health_endpoint_routes_both_with_and_without_api_prefix(self):
        # Test direct /health
        res_direct = self.client.get("/health")
        self.assertEqual(res_direct.status_code, 200)
        data_direct = res_direct.json()
        self.assertEqual(data_direct["status"], "healthy")
        self.assertTrue(data_direct["model_loaded"])

        # Test Vercel /api/health
        res_prefixed = self.client.get("/api/health")
        self.assertEqual(res_prefixed.status_code, 200)
        data_prefixed = res_prefixed.json()
        self.assertEqual(data_prefixed, data_direct)

    def test_predict_url_routes_both_with_and_without_api_prefix(self):
        payload = {
            "url": "https://example.com",
            "allow_heuristics": False,
            "fetch_network": False,
        }
        res_direct = self.client.post("/predict-url", json=payload)
        self.assertEqual(res_direct.status_code, 200)
        data_direct = res_direct.json()

        res_prefixed = self.client.post("/api/predict-url", json=payload)
        self.assertEqual(res_prefixed.status_code, 200)
        data_prefixed = res_prefixed.json()

        self.assertEqual(data_direct["status"], "unsupported_features")
        self.assertEqual(data_prefixed["status"], "unsupported_features")
        self.assertEqual(data_direct["feature_coverage"], data_prefixed["feature_coverage"])

    def test_serverless_model_loads_within_cold_start_budget(self):
        import time
        t0 = time.time()
        pipeline = PredictionPipeline()
        pipeline.load_model()
        duration = time.time() - t0
        self.assertTrue(pipeline.is_model_loaded())
        self.assertLess(duration, 3.0, f"Model load took {duration:.2f}s, expected < 3.0s")

    def test_ssrf_protection_effective_on_vercel_api_route(self):
        res = self.client.post(
            "/api/predict-url",
            json={"url": "http://169.254.169.254/latest/meta-data"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Security violation", res.json()["detail"])


if __name__ == "__main__":
    unittest.main()
