from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## Configuration of the Data Ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os, sys
import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
from sklearn.model_selection import train_test_split

import certifi
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

from networksecurity.constants.training_pipeline import TARGET_COLUMN

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config= data_ingestion_config

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Validates basic structure, emptiness, and target column existence.
        """
        if dataframe is None or dataframe.empty:
            raise ValueError("Dataframe is empty or None.")
        if len(dataframe.columns) <= 1:
            raise ValueError(f"Dataframe has insufficient columns: {len(dataframe.columns)}")
        if TARGET_COLUMN not in dataframe.columns:
            raise ValueError(f"Required target column '{TARGET_COLUMN}' is missing from dataframe.")

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Read the data from the MongoDB collection and store it in a pandas DataFrame.
        """
        try:
            url = os.getenv("MONGO_DB_URL") if os.getenv("MONGO_DB_URL") is not None else MONGO_DB_URL
            if not url:
                raise ValueError("MONGO_DB_URL environment variable is not set. Please configure it in your .env file or environment.")
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(url, tlsCAFile=certifi.where())
            collection=self.mongo_client[database_name][collection_name]

            df= pd.DataFrame(list(collection.find()))
            if df.empty:
                raise ValueError(f"MongoDB collection '{collection_name}' in database '{database_name}' is empty.")

            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"], axis=1)

            df.replace({"na":np.nan},inplace=True)
            self.validate_dataframe(df)
            return df

        except Exception as e:
            raise NetworkSecurityException(str(e),sys)

    def export_data_into_feature_store(self,dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Exports the entire unmanipulated raw dataset into the feature store.
        """
        try:
            self.validate_dataframe(dataframe)
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            dir_path= os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            if not os.path.exists(feature_store_file_path) or os.path.getsize(feature_store_file_path) == 0:
                raise IOError(f"Feature store file failed to save or is empty at {feature_store_file_path}")

            logging.info(f"Raw data successfully exported to feature store at {feature_store_file_path} with {len(dataframe)} rows.")
            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def prepare_clean_deduplicated_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares a leakage-resistant dataset:
        1. Quantifies raw rows, exact duplicates, and conflicting label groups.
        2. Resolves conflicting label groups via majority vote from the raw observations.
        3. Ensures each distinct feature vector appears exactly once in the split candidate set.
        """
        try:
            total_raw = len(dataframe)
            exact_dups = int(dataframe.duplicated().sum())
            features = [c for c in dataframe.columns if c != TARGET_COLUMN]

            # Unique full rows
            dedup_full = dataframe.drop_duplicates().copy()
            unique_full_rows = len(dedup_full)

            # Identify conflicting feature vectors
            grouped = dedup_full.groupby(features)[TARGET_COLUMN].nunique()
            conflicting_features = grouped[grouped > 1].index
            conflicting_count = len(conflicting_features)

            logging.info(f"Dataset duplicate audit: raw_rows={total_raw}, exact_duplicates={exact_dups}, "
                         f"unique_full_rows={unique_full_rows}, conflicting_label_groups={conflicting_count}")

            # Consistent feature vectors
            consistent_df = dedup_full[~dedup_full.set_index(features).index.isin(conflicting_features)]

            # Resolve conflicting groups via consensus majority vote from the raw observations
            if conflicting_count > 0:
                conflict_raw = dataframe[dataframe.set_index(features).index.isin(conflicting_features)]
                resolved_conflict = (
                    conflict_raw.groupby(features)[TARGET_COLUMN]
                    .agg(lambda s: s.mode()[0])
                    .reset_index()
                )
                clean_df = pd.concat([consistent_df, resolved_conflict], ignore_index=True)
            else:
                clean_df = consistent_df.copy()

            logging.info(f"Prepared clean deduplicated dataset: {len(clean_df)} distinct feature vectors.")
            return clean_df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            self.validate_dataframe(dataframe)

            handle_dups = getattr(self.data_ingestion_config, "handle_duplicates", True)
            random_state = getattr(self.data_ingestion_config, "random_state", 42)
            split_ratio = self.data_ingestion_config.train_test_split_ratio

            if handle_dups:
                split_df = self.prepare_clean_deduplicated_data(dataframe)
            else:
                split_df = dataframe.copy()

            # Deterministic, stratified train-test split
            train_set, test_set = train_test_split(
                split_df,
                test_size=split_ratio,
                random_state=random_state,
                stratify=split_df[TARGET_COLUMN] if TARGET_COLUMN in split_df.columns else None
            )

            # Audit leakage between train and test feature vectors
            features = [c for c in dataframe.columns if c != TARGET_COLUMN]
            train_feats = set(map(tuple, train_set[features].values))
            test_feats = set(map(tuple, test_set[features].values))
            feat_overlap = len(train_feats.intersection(test_feats))

            logging.info(
                f"Performed stratified train-test split: train_size={len(train_set)}, test_size={len(test_set)}, "
                f"random_state={random_state}, feature_overlap={feat_overlap}"
            )

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

            if not os.path.exists(self.data_ingestion_config.training_file_path) or not os.path.exists(self.data_ingestion_config.testing_file_path):
                raise IOError("Train or test file failed to save properly during ingestion.")

            logging.info(f"Exported train data to {self.data_ingestion_config.training_file_path} and test data to {self.data_ingestion_config.testing_file_path}")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self, dataframe: pd.DataFrame = None) -> DataIngestionArtifact:
        try:
            if dataframe is None:
                dataframe = self.export_collection_as_dataframe()
            else:
                self.validate_dataframe(dataframe)

            dataframe = self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
