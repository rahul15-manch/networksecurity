import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import StandardScaler

from networksecurity.entity.artifact_entity import (
    ClassificationMetricArtifact,
    DataIngestionArtifact,
    DataTransformationArtifact,
)
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    ModelTrainerConfig,
)
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.exception.exception import NetworkSecurityException


class TestSecurityConfigurations(unittest.TestCase):
    def test_no_hardcoded_secrets_in_tracked_files(self):
        """Verify that known plaintext credentials are not in source files."""
        sensitive_patterns = [
            "Admin123",
            "Rahul@123",
            "mongodb+srv://rahulmanchanda015:",
        ]
        files_to_check = [
            "test_mongodb.py",
            "push_data.py",
            "networksecurity/components/model_trainer.py",
            "networksecurity/components/data_ingestion.py",
        ]
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in sensitive_patterns:
                        self.assertNotIn(
                            pattern,
                            content,
                            f"Sensitive pattern found in {file_path}",
                        )

    def test_model_trainer_import_does_not_inject_hardcoded_secrets(self):
        """Verify that importing model_trainer does not set secret environment variables."""
        self.assertNotIn(
            "MLFLOW_TRACKING_PASSWORD",
            os.environ,
            "MLFLOW_TRACKING_PASSWORD should not be pre-set in os.environ by import",
        )

    def test_data_ingestion_fails_fast_when_mongo_url_missing(self):
        """Verify data ingestion does not silently connect to localhost when MONGO_DB_URL is missing."""
        pipe_cfg = TrainingPipelineConfig()
        ingest_cfg = DataIngestionConfig(pipe_cfg)
        ingest_comp = DataIngestion(ingest_cfg)

        with patch.dict(os.environ, {}, clear=True):
            # Also patch module-level MONGO_DB_URL to None
            with patch("networksecurity.components.data_ingestion.MONGO_DB_URL", None):
                with self.assertRaises(NetworkSecurityException) as ctx:
                    ingest_comp.export_collection_as_dataframe()
                self.assertIn("MONGO_DB_URL", str(ctx.exception))


class TestModelSerializationAndInference(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.model_path = os.path.join(self.temp_dir.name, "model.pkl")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_network_model_instance(self):
        """Verify that saving Network_Model saves an instance and allows prediction."""
        X_dummy = pd.DataFrame({"f1": [1.0, 2.0, 3.0], "f2": [4.0, 5.0, 6.0]})
        y_dummy = np.array([0, 1, 0])

        preprocessor = StandardScaler()
        preprocessor.fit(X_dummy)

        clf = DummyClassifier(strategy="most_frequent")
        clf.fit(preprocessor.transform(X_dummy), y_dummy)

        # Instantiated wrapper
        network_model_instance = NetworkModel(preprocessor=preprocessor, model=clf)

        # Save instance
        save_object(self.model_path, obj=network_model_instance)

        # Load object
        loaded_model = load_object(self.model_path)

        # Must be an instance of NetworkModel, NOT the class object
        self.assertIsInstance(
            loaded_model,
            NetworkModel,
            "Loaded model should be an instance of NetworkModel",
        )
        self.assertNotEqual(
            loaded_model,
            NetworkModel,
            "Loaded object must not be the uninstantiated class object",
        )

        # Must successfully run predict on raw feature DataFrame
        preds = loaded_model.predict(X_dummy)
        self.assertEqual(len(preds), len(X_dummy))
        self.assertTrue(isinstance(preds, np.ndarray))


class TestMLflowTrackingLogic(unittest.TestCase):
    def setUp(self):
        self.pipe_cfg = TrainingPipelineConfig()
        self.trainer_cfg = ModelTrainerConfig(self.pipe_cfg)
        self.trans_artifact = DataTransformationArtifact(
            transformed_train_file_path="dummy_train.npy",
            transformed_test_file_path="dummy_test.npy",
            transformed_object_file_path="dummy_preprocessor.pkl",
        )
        self.trainer = ModelTrainer(self.trainer_cfg, self.trans_artifact)
        self.mock_model = DummyClassifier(strategy="most_frequent")
        self.mock_metric = ClassificationMetricArtifact(
            f1_score=0.95,
            precision_score=0.96,
            recall_score=0.94,
        )

    @patch("networksecurity.components.model_trainer.mlflow")
    def test_track_mlflow_registered_model_name_is_string(self, mock_mlflow):
        """Verify registered_model_name receives a string and not an estimator instance."""
        mock_mlflow.get_tracking_uri.return_value = "https://mock.dagshub.com/repo.mlflow"
        mock_mlflow.start_run.return_value.__enter__.return_value = MagicMock()

        with patch.dict(os.environ, {"MLFLOW_TRACKING_URI": "https://mock.dagshub.com/repo.mlflow"}):
            self.trainer.track_mlflow(self.mock_model, self.mock_metric, dataset_type="test")

        # Verify log_model was called
        mock_mlflow.sklearn.log_model.assert_called_once()
        args, kwargs = mock_mlflow.sklearn.log_model.call_args

        # First argument should be model instance
        self.assertEqual(args[0], self.mock_model)
        # Second argument should be artifact path
        self.assertEqual(args[1], "model")

        # If registered_model_name was passed, verify it is a string
        if "registered_model_name" in kwargs:
            reg_name = kwargs["registered_model_name"]
            self.assertIsInstance(
                reg_name,
                str,
                f"registered_model_name must be str, got {type(reg_name)}",
            )
            self.assertEqual(reg_name, self.mock_model.__class__.__name__)

    @patch("networksecurity.components.model_trainer.mlflow")
    def test_track_mlflow_single_log_model_call(self, mock_mlflow):
        """Verify log_model is called only once per run (no duplicate logging)."""
        mock_mlflow.get_tracking_uri.return_value = "file:///tmp/mlruns"
        mock_mlflow.start_run.return_value.__enter__.return_value = MagicMock()

        self.trainer.track_mlflow(self.mock_model, self.mock_metric, dataset_type="test")
        self.assertEqual(
            mock_mlflow.sklearn.log_model.call_count,
            1,
            "log_model must only be called once to avoid duplicate artifact logging",
        )

    @patch("networksecurity.components.model_trainer.mlflow")
    def test_track_mlflow_distinguishes_train_and_test_metrics(self, mock_mlflow):
        """Verify metrics and tags distinguish train vs test data partitions."""
        mock_mlflow.get_tracking_uri.return_value = "file:///tmp/mlruns"
        mock_mlflow.start_run.return_value.__enter__.return_value = MagicMock()

        # Track train metrics
        self.trainer.track_mlflow(self.mock_model, self.mock_metric, dataset_type="train")
        mock_mlflow.set_tag.assert_any_call("dataset_type", "train")
        mock_mlflow.log_metric.assert_any_call("train_f1_score", 0.95)

        # Track test metrics
        self.trainer.track_mlflow(self.mock_model, self.mock_metric, dataset_type="test")
        mock_mlflow.set_tag.assert_any_call("dataset_type", "test")
        mock_mlflow.log_metric.assert_any_call("test_f1_score", 0.95)


if __name__ == "__main__":
    unittest.main()
