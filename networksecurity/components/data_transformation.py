import os
import sys
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constants.training_pipeline import (
    TARGET_COLUMN,
    DATA_TRANSFORMATION_IMPUTER_PARAMS,
)
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact,
)
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    def __init__(
        self,
        data_validation_artifact: DataValidationArtifact,
        data_transformation_config: DataTransformationConfig,
    ):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """
        Reads CSV file and validates file existence and non-emptiness.
        """
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

    @classmethod
    def get_data_transformer_object(cls) -> Pipeline:
        """
        Initializes and returns the preprocessing pipeline.
        Retains KNNImputer to handle missing values during inference while
        preserving compatibility with trained estimators and serialization contracts.
        """
        logging.info("Creating data transformer object with KNNImputer")
        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"Initialized KNNImputer with parameters: {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            processor: Pipeline = Pipeline([("imputer", imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Entered initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation...")
            train_file_path = self.data_validation_artifact.valid_train_file_path
            test_file_path = self.data_validation_artifact.valid_test_file_path

            train_df = DataTransformation.read_data(train_file_path)
            test_df = DataTransformation.read_data(test_file_path)

            # Validate target column presence
            if TARGET_COLUMN not in train_df.columns:
                raise ValueError(f"Target column '{TARGET_COLUMN}' missing from train dataset.")
            if TARGET_COLUMN not in test_df.columns:
                raise ValueError(f"Target column '{TARGET_COLUMN}' missing from test dataset.")

            # Separate features and target for training set
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]

            # Separate features and target for testing set
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]

            # Validate feature consistency between train and test
            train_cols = list(input_feature_train_df.columns)
            test_cols = set(input_feature_test_df.columns)
            missing_in_test = set(train_cols) - test_cols
            if missing_in_test:
                raise ValueError(f"Test dataset missing required feature columns: {sorted(list(missing_in_test))}")

            # Ensure test DataFrame features follow the exact same column ordering as train
            input_feature_test_df = input_feature_test_df[train_cols]

            # Validate and encode target values: {-1, 1} -> {0, 1}
            # Legitimate = 1, Phishing = 0
            target_feature_train_df = target_feature_train_df.replace(-1, 0)
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # Fit preprocessor strictly on training features only
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_df)

            # Transform both train and test feature sets using the fitted preprocessor
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            # Combine transformed features with target column as numpy arrays
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # Ensure destination directories exist
            os.makedirs(os.path.dirname(self.data_transformation_config.transformed_train_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(self.data_transformation_config.transformed_test_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(self.data_transformation_config.transformed_object_file_path), exist_ok=True)

            # Save transformed numpy arrays and preprocessor object
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)

            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
            )
            logging.info(f"Data transformation completed successfully: {data_transformation_artifact}")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
