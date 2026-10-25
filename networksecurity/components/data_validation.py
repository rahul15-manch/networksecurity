from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH, TARGET_COLUMN
from scipy.stats import ks_2samp
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file
import pandas as pd
import numpy as np
import os, sys


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found at: {file_path}")
            if os.path.getsize(file_path) == 0:
                raise ValueError(f"Dataset file at {file_path} is empty.")
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                raise ValueError(f"Dataset at {file_path} is empty (no columns to parse).")
            if df.empty:
                raise ValueError(f"Dataset at {file_path} is empty.")
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def get_expected_columns(self) -> list:
        try:
            expected_columns = []
            for col_info in self._schema_config.get("columns", []):
                if isinstance(col_info, dict):
                    expected_columns.extend(col_info.keys())
                else:
                    expected_columns.append(col_info)
            return expected_columns
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_cols = self.get_expected_columns()
            number_of_columns = len(expected_cols)
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"DataFrame has columns: {len(dataframe.columns)}")
            return len(dataframe.columns) == number_of_columns
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_column_names(self, dataframe: pd.DataFrame) -> tuple:
        """
        Validates column names against schema.
        Returns: (is_valid: bool, missing_columns: list, unexpected_columns: list)
        """
        try:
            expected_cols = set(self.get_expected_columns())
            df_cols = set(dataframe.columns)
            missing_cols = sorted(list(expected_cols - df_cols))
            unexpected_cols = sorted(list(df_cols - expected_cols))
            is_valid = len(missing_cols) == 0
            if missing_cols:
                logging.error(f"Missing expected columns in DataFrame: {missing_cols}")
            if unexpected_cols:
                logging.warning(f"Unexpected columns in DataFrame: {unexpected_cols}")
            return is_valid, missing_cols, unexpected_cols
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.05) -> bool:
        """
        Detects data drift using Kolmogorov-Smirnov test.
        Returns True if no drift is found (distribution matches), False if drift detected.
        """
        try:
            status = True
            report = {}
            for column in base_df.columns:
                if column not in current_df.columns:
                    status = False
                    report[column] = {"drift_status": True, "error": "Column missing from current_df"}
                    continue
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                p_value = float(is_same_dist.pvalue)
                is_drift = p_value < threshold
                if is_drift:
                    status = False
                report[column] = {
                    "p_value": p_value,
                    "drift_status": is_drift
                }
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            # Read train and test data
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            # Validate target column presence
            if TARGET_COLUMN not in train_dataframe.columns:
                raise ValueError(f"Target column '{TARGET_COLUMN}' missing from train dataset.")
            if TARGET_COLUMN not in test_dataframe.columns:
                raise ValueError(f"Target column '{TARGET_COLUMN}' missing from test dataset.")

            # Validate column names
            train_cols_valid, train_missing, train_extra = self.validate_column_names(train_dataframe)
            test_cols_valid, test_missing, test_extra = self.validate_column_names(test_dataframe)

            if not train_cols_valid:
                raise ValueError(f"Train DataFrame is missing required columns: {train_missing}")
            if not test_cols_valid:
                raise ValueError(f"Test DataFrame is missing required columns: {test_missing}")

            # Validate column counts
            train_col_count_valid = self.validate_number_of_columns(train_dataframe)
            test_col_count_valid = self.validate_number_of_columns(test_dataframe)
            if not train_col_count_valid or not test_col_count_valid:
                raise ValueError(
                    f"Column count mismatch. Expected {len(self.get_expected_columns())}, "
                    f"got {len(train_dataframe.columns)} in train and {len(test_dataframe.columns)} in test."
                )

            # Check dataset drift
            drift_status = self.detect_dataset_drift(base_df=train_dataframe, current_df=test_dataframe)

            # Save validated files to valid data directory
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            data_validation_artifact = DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
