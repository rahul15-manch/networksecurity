import os
import sys
import tempfile
import unittest
import warnings
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore", category=RuntimeWarning)

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.entity.artifact_entity import (
    DataValidationArtifact,
    DataTransformationArtifact,
)
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataTransformationConfig,
)
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.main_utils.utils import load_numpy_array_data, load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


class TestDataTransformation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pipe_cfg = TrainingPipelineConfig()
        self.pipe_cfg.artifact_dir = self.temp_dir.name
        self.trans_cfg = DataTransformationConfig(self.pipe_cfg)

        # Create synthetic dataset with 30 features and 1 target column
        self.feature_names = [f"feat_{i}" for i in range(30)]
        np.random.seed(42)

        # Training data: 50 samples
        train_features = np.random.choice([-1, 0, 1], size=(50, 30))
        train_targets = np.random.choice([-1, 1], size=(50, 1))
        self.train_df = pd.DataFrame(train_features, columns=self.feature_names)
        self.train_df[TARGET_COLUMN] = train_targets

        # Testing data: 20 samples
        test_features = np.random.choice([-1, 0, 1], size=(20, 30))
        test_targets = np.random.choice([-1, 1], size=(20, 1))
        self.test_df = pd.DataFrame(test_features, columns=self.feature_names)
        self.test_df[TARGET_COLUMN] = test_targets

        self.train_path = os.path.join(self.temp_dir.name, "valid_train.csv")
        self.test_path = os.path.join(self.temp_dir.name, "valid_test.csv")
        self.train_df.to_csv(self.train_path, index=False)
        self.test_df.to_csv(self.test_path, index=False)

        self.val_artifact = DataValidationArtifact(
            validation_status=True,
            valid_train_file_path=self.train_path,
            valid_test_file_path=self.test_path,
            invalid_train_file_path=None,
            invalid_test_file_path=None,
            drift_report_file_path=os.path.join(self.temp_dir.name, "drift.yaml"),
        )
        self.transformer = DataTransformation(self.val_artifact, self.trans_cfg)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_transformation_pipeline_execution_and_artifacts(self):
        """Verify complete transformation pipeline runs, produces valid arrays and preprocessor artifact."""
        artifact = self.transformer.initiate_data_transformation()
        self.assertIsInstance(artifact, DataTransformationArtifact)
        self.assertTrue(os.path.exists(artifact.transformed_train_file_path))
        self.assertTrue(os.path.exists(artifact.transformed_test_file_path))
        self.assertTrue(os.path.exists(artifact.transformed_object_file_path))

        # Check array shapes: 50 x 31 and 20 x 31
        train_arr = load_numpy_array_data(artifact.transformed_train_file_path)
        test_arr = load_numpy_array_data(artifact.transformed_test_file_path)

        self.assertEqual(train_arr.shape, (50, 31))
        self.assertEqual(test_arr.shape, (20, 31))

    def test_target_column_excluded_from_features_and_encoded_correctly(self):
        """Verify target column is excluded from features, encoded from {-1, 1} to {0, 1}, and appended last."""
        artifact = self.transformer.initiate_data_transformation()
        train_arr = load_numpy_array_data(artifact.transformed_train_file_path)
        test_arr = load_numpy_array_data(artifact.transformed_test_file_path)

        y_train = train_arr[:, -1]
        y_test = test_arr[:, -1]

        # Valid target values must strictly be {0, 1}
        self.assertTrue(set(np.unique(y_train)).issubset({0, 1}))
        self.assertTrue(set(np.unique(y_test)).issubset({0, 1}))

        # Preprocessor feature count must be exactly 30 (target excluded)
        preprocessor = load_object(artifact.transformed_object_file_path)
        dummy_sample = pd.DataFrame(np.ones((1, 30)), columns=self.feature_names)
        transformed_sample = preprocessor.transform(dummy_sample)
        self.assertEqual(transformed_sample.shape, (1, 30))

    def test_preprocessor_fitted_on_training_data_only(self):
        """Verify preprocessor parameters and statistics are learned strictly from train data, not test data."""
        # Use simple constant train data and different test data with NaN
        train_df = pd.DataFrame({
            "col1": [10.0, 10.0, 10.0],
            "col2": [20.0, 20.0, 20.0],
            TARGET_COLUMN: [1, 1, 1],
        })
        test_df = pd.DataFrame({
            "col1": [100.0, np.nan],
            "col2": [200.0, np.nan],
            TARGET_COLUMN: [-1, -1],
        })

        tr_path = os.path.join(self.temp_dir.name, "tr_only.csv")
        te_path = os.path.join(self.temp_dir.name, "te_only.csv")
        train_df.to_csv(tr_path, index=False)
        test_df.to_csv(te_path, index=False)

        val_art = DataValidationArtifact(True, tr_path, te_path, None, None, "drift.yaml")
        transformer = DataTransformation(val_art, self.trans_cfg)
        artifact = transformer.initiate_data_transformation()

        preprocessor = load_object(artifact.transformed_object_file_path)
        test_arr = load_numpy_array_data(artifact.transformed_test_file_path)

        # In row 2 of test, missing values should be imputed from train data (which is 10.0 and 20.0)
        imputed_row = test_arr[1, :-1]
        self.assertAlmostEqual(imputed_row[0], 10.0)
        self.assertAlmostEqual(imputed_row[1], 20.0)

    def test_preprocessor_handles_missing_values_at_inference(self):
        """Verify preprocessor successfully handles np.nan values at inference time using KNN imputation."""
        artifact = self.transformer.initiate_data_transformation()
        preprocessor = load_object(artifact.transformed_object_file_path)

        # Create an inference DataFrame with NaNs
        inference_df = pd.DataFrame(np.ones((5, 30)), columns=self.feature_names)
        inference_df.iloc[0, 0] = np.nan
        inference_df.iloc[1, 5] = np.nan
        inference_df.iloc[2, 10] = np.nan

        transformed = preprocessor.transform(inference_df)
        self.assertEqual(transformed.shape, (5, 30))
        self.assertFalse(np.isnan(transformed).any(), "Imputed output must contain no NaN values")

    def test_consistent_feature_ordering_realigned_for_test_set(self):
        """Verify that test set columns in arbitrary order are realigned to match training column order."""
        reversed_cols = list(reversed(self.feature_names)) + [TARGET_COLUMN]
        reversed_test_df = self.test_df[reversed_cols]
        reversed_test_path = os.path.join(self.temp_dir.name, "reversed_test.csv")
        reversed_test_df.to_csv(reversed_test_path, index=False)

        val_art = DataValidationArtifact(True, self.train_path, reversed_test_path, None, None, "d.yaml")
        transformer = DataTransformation(val_art, self.trans_cfg)
        artifact = transformer.initiate_data_transformation()

        test_arr = load_numpy_array_data(artifact.transformed_test_file_path)
        # Check first row matches expected original feature 0 value
        expected_feat0 = self.test_df["feat_0"].iloc[0]
        actual_feat0 = test_arr[0, 0]
        self.assertEqual(actual_feat0, expected_feat0)

    def test_missing_feature_column_in_test_raises_error(self):
        """Verify ValueError is raised when test dataset is missing a required feature column."""
        corrupted_test_df = self.test_df.drop(columns=["feat_5"])
        corrupted_test_path = os.path.join(self.temp_dir.name, "corrupt_test.csv")
        corrupted_test_df.to_csv(corrupted_test_path, index=False)

        val_art = DataValidationArtifact(True, self.train_path, corrupted_test_path, None, None, "d.yaml")
        transformer = DataTransformation(val_art, self.trans_cfg)

        with self.assertRaises(NetworkSecurityException) as ctx:
            transformer.initiate_data_transformation()
        self.assertIn("feat_5", str(ctx.exception))

    def test_missing_target_column_raises_error(self):
        """Verify ValueError is raised when target column is missing from train or test set."""
        no_target_df = self.train_df.drop(columns=[TARGET_COLUMN])
        no_target_path = os.path.join(self.temp_dir.name, "no_target_tr.csv")
        no_target_df.to_csv(no_target_path, index=False)

        val_art = DataValidationArtifact(True, no_target_path, self.test_path, None, None, "d.yaml")
        transformer = DataTransformation(val_art, self.trans_cfg)

        with self.assertRaises(NetworkSecurityException) as ctx:
            transformer.initiate_data_transformation()
        self.assertIn(f"Target column '{TARGET_COLUMN}' missing", str(ctx.exception))

    def test_read_data_fails_on_empty_and_missing_file(self):
        """Verify read_data validates file existence and rejects empty files."""
        empty_path = os.path.join(self.temp_dir.name, "empty.csv")
        pd.DataFrame().to_csv(empty_path, index=False)

        with self.assertRaises(NetworkSecurityException) as ctx:
            DataTransformation.read_data(empty_path)
        self.assertIn("empty", str(ctx.exception).lower())

        with self.assertRaises(NetworkSecurityException) as ctx:
            DataTransformation.read_data(os.path.join(self.temp_dir.name, "nonexistent.csv"))
        self.assertIn("not found", str(ctx.exception).lower())

    def test_preprocessor_serialization_and_network_model_inference(self):
        """Verify the serialized preprocessor works in downstream NetworkModel inference."""
        artifact = self.transformer.initiate_data_transformation()
        preprocessor = load_object(artifact.transformed_object_file_path)

        train_arr = load_numpy_array_data(artifact.transformed_train_file_path)
        X_tr = train_arr[:, :-1]
        y_tr = train_arr[:, -1]

        clf = LogisticRegression()
        clf.fit(X_tr, y_tr)

        network_model = NetworkModel(preprocessor=preprocessor, model=clf)

        # Run prediction on a raw DataFrame (simulating inference)
        sample_input = pd.DataFrame(np.random.choice([-1, 0, 1], size=(5, 30)), columns=self.feature_names)
        predictions = network_model.predict(sample_input)

        self.assertEqual(len(predictions), 5)
        self.assertTrue(set(predictions).issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
