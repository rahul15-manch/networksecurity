import os
import sys
import tempfile
import unittest
import numpy as np
import pandas as pd

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.entity.artifact_entity import DataIngestionArtifact
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
)
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.exception.exception import NetworkSecurityException


class TestSchemaValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pipe_cfg = TrainingPipelineConfig()
        self.val_cfg = DataValidationConfig(self.pipe_cfg)

        # Create a valid dummy dataset matching schema.yaml
        dv_helper = DataValidation(
            DataIngestionArtifact("dummy_tr", "dummy_te"), self.val_cfg
        )
        self.expected_cols = dv_helper.get_expected_columns()

        # Build dummy dataframe with 20 rows
        dummy_data = {col: [1] * 20 for col in self.expected_cols}
        dummy_data[TARGET_COLUMN] = [1] * 10 + [-1] * 10
        self.valid_df = pd.DataFrame(dummy_data)

        self.train_path = os.path.join(self.temp_dir.name, "train.csv")
        self.test_path = os.path.join(self.temp_dir.name, "test.csv")
        self.valid_df.to_csv(self.train_path, index=False)
        self.valid_df.to_csv(self.test_path, index=False)

        self.ingest_artifact = DataIngestionArtifact(
            trained_file_path=self.train_path,
            test_file_path=self.test_path,
        )
        self.validator = DataValidation(self.ingest_artifact, self.val_cfg)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_validation_passes_on_valid_data(self):
        """Verify schema validation succeeds and produces artifact on compliant dataset."""
        artifact = self.validator.initiate_data_validation()
        self.assertTrue(os.path.exists(artifact.valid_train_file_path))
        self.assertTrue(os.path.exists(artifact.valid_test_file_path))
        self.assertTrue(artifact.validation_status)

    def test_schema_validation_fails_on_missing_column(self):
        """Verify validation raises exception when required column is missing."""
        corrupted_df = self.valid_df.drop(columns=["having_IP_Address"])
        corrupted_path = os.path.join(self.temp_dir.name, "corrupted_train.csv")
        corrupted_df.to_csv(corrupted_path, index=False)

        bad_artifact = DataIngestionArtifact(
            trained_file_path=corrupted_path,
            test_file_path=self.test_path,
        )
        bad_validator = DataValidation(bad_artifact, self.val_cfg)

        with self.assertRaises(NetworkSecurityException) as ctx:
            bad_validator.initiate_data_validation()
        self.assertIn("having_IP_Address", str(ctx.exception))

    def test_schema_validation_detects_unexpected_columns(self):
        """Verify validate_column_names identifies unexpected extraneous columns."""
        df_with_extra = self.valid_df.copy()
        df_with_extra["extraneous_col"] = 99
        is_valid, missing, extra = self.validator.validate_column_names(df_with_extra)
        self.assertIn("extraneous_col", extra)

    def test_schema_validation_fails_on_missing_target(self):
        """Verify validation raises exception when target column is missing."""
        no_target_df = self.valid_df.drop(columns=[TARGET_COLUMN])
        no_target_path = os.path.join(self.temp_dir.name, "no_target.csv")
        no_target_df.to_csv(no_target_path, index=False)

        bad_artifact = DataIngestionArtifact(
            trained_file_path=no_target_path,
            test_file_path=self.test_path,
        )
        bad_validator = DataValidation(bad_artifact, self.val_cfg)

        with self.assertRaises(NetworkSecurityException) as ctx:
            bad_validator.initiate_data_validation()
        self.assertIn("Target column", str(ctx.exception))

    def test_read_data_fails_on_empty_dataset(self):
        """Verify read_data raises exception on an empty CSV file."""
        empty_path = os.path.join(self.temp_dir.name, "empty.csv")
        pd.DataFrame().to_csv(empty_path, index=False)

        with self.assertRaises(NetworkSecurityException) as ctx:
            DataValidation.read_data(empty_path)
        self.assertIn("empty", str(ctx.exception).lower())

    def test_read_data_fails_on_nonexistent_file(self):
        """Verify read_data raises FileNotFoundError wrapped in exception."""
        with self.assertRaises(NetworkSecurityException) as ctx:
            DataValidation.read_data(os.path.join(self.temp_dir.name, "missing.csv"))
        self.assertIn("not found", str(ctx.exception).lower())


class TestDatasetDriftDetection(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pipe_cfg = TrainingPipelineConfig()
        self.val_cfg = DataValidationConfig(self.pipe_cfg)
        self.ingest_art = DataIngestionArtifact("dummy_tr", "dummy_te")
        self.validator = DataValidation(self.ingest_art, self.val_cfg)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_drift_detection_returns_true_when_distributions_match(self):
        """Verify detect_dataset_drift returns True (no drift) for identical distributions."""
        np.random.seed(42)
        base = pd.DataFrame({"col1": np.random.normal(0, 1, 100), "col2": np.random.normal(5, 2, 100)})
        current = pd.DataFrame({"col1": np.random.normal(0, 1, 100), "col2": np.random.normal(5, 2, 100)})

        status = self.validator.detect_dataset_drift(base, current)
        self.assertIsInstance(status, bool)
        self.assertTrue(status, "Drift status should be True when distributions match")

    def test_drift_detection_returns_false_when_drift_occurs(self):
        """Verify detect_dataset_drift returns False when a column undergoes distribution shift."""
        base = pd.DataFrame({"col1": [1] * 100, "col2": [0] * 100})
        # Current df has completely distinct distribution in col1
        current = pd.DataFrame({"col1": [100] * 100, "col2": [0] * 100})

        status = self.validator.detect_dataset_drift(base, current)
        self.assertIsInstance(status, bool)
        self.assertFalse(status, "Drift status should be False when drift is detected")


class TestDataIngestionAndDeduplication(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pipe_cfg = TrainingPipelineConfig()
        # Point artifact paths to temp directory
        self.pipe_cfg.artifact_dir = self.temp_dir.name
        self.ingest_cfg = DataIngestionConfig(self.pipe_cfg)
        self.ingestion = DataIngestion(self.ingest_cfg)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_prepare_clean_deduplicated_data(self):
        """Verify deduplication removes exact duplicates and resolves conflicting labels via majority vote."""
        # Create dataset with:
        # Row A: [1, 2], Result=1 (repeated 3 times)
        # Row B: [3, 4], Result=1 (repeated 2 times) and Result=-1 (repeated 1 time) -> Conflicting group (majority 1)
        # Row C: [5, 6], Result=-1 (single occurrence)
        df = pd.DataFrame({
            "f1": [1, 1, 1, 3, 3, 3, 5],
            "f2": [2, 2, 2, 4, 4, 4, 6],
            TARGET_COLUMN: [1, 1, 1, 1, 1, -1, -1]
        })

        clean_df = self.ingestion.prepare_clean_deduplicated_data(df)

        # There should be exactly 3 unique feature vectors
        self.assertEqual(len(clean_df), 3)

        # Check majority vote for conflicting group [3, 4]: 2 votes for 1 vs 1 vote for -1 -> Result should be 1
        conflict_result = clean_df[(clean_df["f1"] == 3) & (clean_df["f2"] == 4)][TARGET_COLUMN].values[0]
        self.assertEqual(conflict_result, 1)

    def test_split_is_deterministic_and_reproducible(self):
        """Verify train-test split produces identical splits when run with same seed."""
        np.random.seed(42)
        df = pd.DataFrame({
            "f1": np.arange(100),
            "f2": np.arange(100, 200),
            TARGET_COLUMN: [1] * 50 + [-1] * 50
        })

        # Run 1
        self.ingestion.split_data_as_train_test(df)
        train1 = pd.read_csv(self.ingest_cfg.training_file_path)
        test1 = pd.read_csv(self.ingest_cfg.testing_file_path)

        # Run 2
        self.ingestion.split_data_as_train_test(df)
        train2 = pd.read_csv(self.ingest_cfg.training_file_path)
        test2 = pd.read_csv(self.ingest_cfg.testing_file_path)

        pd.testing.assert_frame_equal(train1, train2)
        pd.testing.assert_frame_equal(test1, test2)

    def test_leakage_resistant_split_zero_overlap(self):
        """Verify split ensures zero feature vector overlap between train and test sets."""
        # Create dataset with duplicates
        df = pd.DataFrame({
            "f1": [1, 1, 2, 2, 3, 4, 5, 6, 7, 8] * 5,
            "f2": [10, 10, 20, 20, 30, 40, 50, 60, 70, 80] * 5,
            TARGET_COLUMN: [1, -1, 1, -1, 1, -1, 1, -1, 1, -1] * 5
        })

        self.ingestion.split_data_as_train_test(df)
        train = pd.read_csv(self.ingest_cfg.training_file_path)
        test = pd.read_csv(self.ingest_cfg.testing_file_path)

        features = ["f1", "f2"]
        train_tuples = set(map(tuple, train[features].values))
        test_tuples = set(map(tuple, test[features].values))

        overlap = train_tuples.intersection(test_tuples)
        self.assertEqual(len(overlap), 0, f"Detected feature overlap between train and test: {overlap}")

    def test_export_data_into_feature_store_preserves_all_raw_rows(self):
        """Verify export_data_into_feature_store preserves complete dataset without dropping rows."""
        df = pd.DataFrame({
            "f1": [1, 1, 2, 2],
            "f2": [3, 3, 4, 4],
            TARGET_COLUMN: [1, 1, -1, -1]
        })
        saved = self.ingestion.export_data_into_feature_store(df)
        self.assertEqual(len(saved), len(df))

        stored = pd.read_csv(self.ingest_cfg.feature_store_file_path)
        self.assertEqual(len(stored), 4)

    def test_validate_dataframe_rejects_empty_or_invalid_inputs(self):
        """Verify validate_dataframe rejects empty, single-column, or target-free DataFrames."""
        with self.assertRaises(ValueError):
            self.ingestion.validate_dataframe(pd.DataFrame())

        with self.assertRaises(ValueError):
            self.ingestion.validate_dataframe(pd.DataFrame({"only_one_col": [1, 2]}))

        with self.assertRaises(ValueError):
            self.ingestion.validate_dataframe(pd.DataFrame({"f1": [1, 2], "f2": [3, 4]}))

    def test_stratification_preserves_class_proportions(self):
        """Verify train-test split preserves target class distribution ratio."""
        # Create dataset with 80% positive (class 1) and 20% negative (class -1)
        n_rows = 100
        df = pd.DataFrame({
            "f1": np.arange(n_rows),
            "f2": np.arange(n_rows, 2 * n_rows),
            TARGET_COLUMN: [1] * 80 + [-1] * 20
        })

        self.ingestion.split_data_as_train_test(df)
        train = pd.read_csv(self.ingest_cfg.training_file_path)
        test = pd.read_csv(self.ingest_cfg.testing_file_path)

        train_pos_ratio = (train[TARGET_COLUMN] == 1).mean()
        test_pos_ratio = (test[TARGET_COLUMN] == 1).mean()

        self.assertAlmostEqual(train_pos_ratio, 0.80, delta=0.05)
        self.assertAlmostEqual(test_pos_ratio, 0.80, delta=0.05)


class TestRealDatasetSchemaCompliance(unittest.TestCase):
    def test_network_data_phising_data_matches_schema(self):
        """Verify the local Network_Data/phisingData.csv conforms to data_schema/schema.yaml."""
        pipe_cfg = TrainingPipelineConfig()
        val_cfg = DataValidationConfig(pipe_cfg)
        ingest_art = DataIngestionArtifact("dummy", "dummy")
        validator = DataValidation(ingest_art, val_cfg)

        csv_path = "Network_Data/phisingData.csv"
        self.assertTrue(os.path.exists(csv_path), f"Expected dataset at {csv_path}")

        df = DataValidation.read_data(csv_path)
        self.assertEqual(len(df), 11055, "phisingData.csv should have exactly 11,055 rows")

        # Column count check
        self.assertTrue(validator.validate_number_of_columns(df))

        # Column names check
        is_valid, missing, extra = validator.validate_column_names(df)
        self.assertTrue(is_valid, f"Missing columns in phisingData.csv: {missing}")
        self.assertEqual(len(extra), 0, f"Unexpected columns in phisingData.csv: {extra}")

        # Target presence check
        self.assertIn(TARGET_COLUMN, df.columns)


if __name__ == "__main__":
    unittest.main()
