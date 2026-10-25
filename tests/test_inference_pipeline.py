import os
import tempfile
import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import StandardScaler
from fastapi.testclient import TestClient

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.utils.main_utils.utils import save_object
from networksecurity.utils.ml_utils.model.estimator import (
    NetworkModel,
    EXPECTED_FEATURES,
    CLASS_LABEL_MAPPING,
)
from networksecurity.pipeline.prediction_pipeline import PredictionPipeline
from app import app, pipeline as global_pipeline


class TestNetworkModelInference(unittest.TestCase):
    """Unit tests for NetworkModel input validation, ordering, and mapping."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # Create a fitted dummy preprocessor and model on EXPECTED_FEATURES
        self.preprocessor = StandardScaler()
        dummy_X = pd.DataFrame(
            np.ones((10, len(EXPECTED_FEATURES))),
            columns=EXPECTED_FEATURES,
        )
        self.preprocessor.fit(dummy_X)

        self.clf = DummyClassifier(strategy="constant", constant=0)
        self.clf.fit(self.preprocessor.transform(dummy_X), np.zeros(10))

        self.network_model = NetworkModel(
            preprocessor=self.preprocessor,
            model=self.clf,
            expected_features=EXPECTED_FEATURES,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_feature_count_and_column_ordering_preserved(self):
        """Verify input features with randomized column order are realigned to EXPECTED_FEATURES."""
        shuffled_cols = list(reversed(EXPECTED_FEATURES))
        sample_data = {col: 1 for col in shuffled_cols}
        df_input = pd.DataFrame([sample_data])

        prepared_df = self.network_model.validate_and_prepare_input(df_input)
        self.assertEqual(list(prepared_df.columns), EXPECTED_FEATURES)
        self.assertEqual(len(prepared_df.columns), 30)

    def test_target_column_excluded_from_predictor_input(self):
        """Verify target column 'Result' is stripped if passed in the input."""
        sample_data = {col: 1 for col in EXPECTED_FEATURES}
        sample_data[TARGET_COLUMN] = 1  # Accidental target column included
        df_input = pd.DataFrame([sample_data])

        self.assertIn(TARGET_COLUMN, df_input.columns)
        prepared_df = self.network_model.validate_and_prepare_input(df_input)
        self.assertNotIn(TARGET_COLUMN, prepared_df.columns)
        self.assertEqual(list(prepared_df.columns), EXPECTED_FEATURES)

    def test_missing_feature_rejection(self):
        """Verify input missing required columns raises ValueError."""
        incomplete_data = {col: 1 for col in EXPECTED_FEATURES[:25]}
        df_input = pd.DataFrame([incomplete_data])

        with self.assertRaises(ValueError) as ctx:
            self.network_model.validate_and_prepare_input(df_input)
        self.assertIn("missing required features", str(ctx.exception).lower())

    def test_input_formats_support(self):
        """Verify dict, list of dicts, numpy array, and DataFrame inputs."""
        single_dict = {col: 1 for col in EXPECTED_FEATURES}
        df_from_dict = self.network_model.validate_and_prepare_input(single_dict)
        self.assertEqual(df_from_dict.shape, (1, 30))

        list_of_dicts = [single_dict, single_dict]
        df_from_list = self.network_model.validate_and_prepare_input(list_of_dicts)
        self.assertEqual(df_from_list.shape, (2, 30))

        np_array = np.ones((3, 30))
        df_from_np = self.network_model.validate_and_prepare_input(np_array)
        self.assertEqual(df_from_np.shape, (3, 30))

    def test_class_to_label_mapping(self):
        """Verify correct class-to-label mapping: 0=phishing, 1=legitimate."""
        self.assertEqual(CLASS_LABEL_MAPPING[0], "phishing")
        self.assertEqual(CLASS_LABEL_MAPPING[1], "legitimate")

        sample_dict = {col: 1 for col in EXPECTED_FEATURES}
        details = self.network_model.predict_with_details(sample_dict)
        self.assertEqual(len(details), 1)
        self.assertIn(details[0]["prediction"], ["phishing", "legitimate"])
        self.assertEqual(details[0]["class_id"], 0)


class TestPredictionPipeline(unittest.TestCase):
    """Unit tests for artifact loading and pipeline execution."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_model_artifact_raises_filenotfound(self):
        """Verify loading non-existent model raises actionable FileNotFoundError."""
        missing_path = os.path.join(self.temp_dir.name, "nonexistent_model.pkl")
        pipeline = PredictionPipeline(model_path=missing_path)

        with self.assertRaises(FileNotFoundError) as ctx:
            pipeline.load_model()
        self.assertIn("Model artifact not found", str(ctx.exception))

    def test_corrupt_or_invalid_model_artifact_raises_typeerror(self):
        """Verify loading an invalid object (not NetworkModel) raises TypeError."""
        corrupt_path = os.path.join(self.temp_dir.name, "corrupt_model.pkl")
        save_object(corrupt_path, obj={"not": "a_model"})
        pipeline = PredictionPipeline(model_path=corrupt_path)

        with self.assertRaises(TypeError) as ctx:
            pipeline.load_model()
        self.assertIn("not a valid NetworkModel instance", str(ctx.exception))

    def test_real_model_artifact_end_to_end_inference(self):
        """Verify end-to-end inference using the real final_model artifact if present."""
        real_model_path = "final_model/model.pkl"
        if not os.path.exists(real_model_path):
            self.skipTest(f"Skipping: {real_model_path} not found in repository.")

        pipeline = PredictionPipeline(model_path=real_model_path)
        pipeline.load_model()
        self.assertTrue(pipeline.is_model_loaded())

        # Test phishing-typical feature sample (-1 everywhere)
        phishing_features = {col: -1 for col in EXPECTED_FEATURES}
        preds = pipeline.predict_with_details(phishing_features)
        self.assertEqual(len(preds), 1)
        self.assertIn("prediction", preds[0])
        self.assertIn("class_id", preds[0])
        self.assertIn(preds[0]["class_id"], [0, 1])
        if preds[0]["model_score"] is not None:
            self.assertTrue(0.0 <= preds[0]["model_score"] <= 1.0)


class TestFastAPIServingEndpoints(unittest.TestCase):
    """Integration tests for FastAPI serving layer."""

    def setUp(self):
        self.client = TestClient(app)
        self.valid_sample = {col: 1 for col in EXPECTED_FEATURES}

    def test_root_endpoint(self):
        """Verify GET / returns API metadata and supported features."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(len(data["supported_features"]), 30)

    def test_health_endpoint_success(self):
        """Verify GET /health returns healthy status when model is available."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["status"], ["healthy", "degraded"])
        self.assertEqual(data["supported_features_count"], 30)

    def test_health_endpoint_when_model_missing(self):
        """Verify GET /health reports degraded when model artifact cannot be found."""
        with patch.object(global_pipeline, "model_path", "nonexistent/path/model.pkl"):
            with patch.object(global_pipeline, "model", None):
                response = self.client.get("/health")
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "degraded")
                self.assertFalse(data["model_loaded"])

    def test_predict_single_success(self):
        """Verify POST /predict returns valid schema with prediction, class_id, model_score."""
        response = self.client.post("/predict", json=self.valid_sample)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("prediction", data)
        self.assertIn("class_id", data)
        self.assertIn(data["class_id"], [0, 1])
        self.assertIn(data["prediction"], ["phishing", "legitimate"])
        if data["model_score"] is not None:
            self.assertTrue(0.0 <= data["model_score"] <= 1.0)

    def test_predict_single_with_target_column_ignored(self):
        """Verify POST /predict safely ignores extra 'Result' column in payload."""
        sample_with_target = dict(self.valid_sample)
        sample_with_target["Result"] = 1

        response = self.client.post("/predict", json=sample_with_target)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["prediction"], ["phishing", "legitimate"])

    def test_predict_single_missing_features_returns_422(self):
        """Verify POST /predict rejects incomplete payload with HTTP 422."""
        incomplete = {"having_IP_Address": 1, "URL_Length": -1}
        response = self.client.post("/predict", json=incomplete)
        self.assertEqual(response.status_code, 422)

    def test_predict_single_invalid_feature_value_returns_422(self):
        """Verify POST /predict rejects out-of-range feature values with HTTP 422."""
        invalid_sample = dict(self.valid_sample)
        invalid_sample["having_IP_Address"] = 999  # Allowed values: -1, 0, 1
        response = self.client.post("/predict", json=invalid_sample)
        self.assertEqual(response.status_code, 422)

    def test_predict_batch_success(self):
        """Verify POST /predict/batch processes multiple samples."""
        sample_legit = {col: 1 for col in EXPECTED_FEATURES}
        sample_phish = {col: -1 for col in EXPECTED_FEATURES}
        sample_phish["Redirect"] = 0

        batch_payload = {
            "samples": [
                sample_legit,
                sample_phish,
            ]
        }
        response = self.client.post("/predict/batch", json=batch_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_samples"], 2)
        self.assertEqual(len(data["predictions"]), 2)
        for pred in data["predictions"]:
            self.assertIn(pred["prediction"], ["phishing", "legitimate"])
            self.assertIn(pred["class_id"], [0, 1])

    def test_predict_when_model_missing_returns_503(self):
        """Verify POST /predict returns 503 when model artifact is missing without leaking paths."""
        with patch.object(global_pipeline, "model", None):
            with patch.object(global_pipeline, "load_model", side_effect=FileNotFoundError("Model not found")):
                response = self.client.post("/predict", json=self.valid_sample)
                self.assertEqual(response.status_code, 503)
                detail = response.json()["detail"]
                self.assertIn("not available", detail.lower())
                # Verify internal filesystem path is NOT leaked
                self.assertNotIn("/Users/", detail)


if __name__ == "__main__":
    unittest.main()
