import os
import sys
import numpy as np
import pandas as pd
from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

EXPECTED_FEATURES = [
    "having_IP_Address",
    "URL_Length",
    "Shortining_Service",
    "having_At_Symbol",
    "double_slash_redirecting",
    "Prefix_Suffix",
    "having_Sub_Domain",
    "SSLfinal_State",
    "Domain_registeration_length",
    "Favicon",
    "port",
    "HTTPS_token",
    "Request_URL",
    "URL_of_Anchor",
    "Links_in_tags",
    "SFH",
    "Submitting_to_email",
    "Abnormal_URL",
    "Redirect",
    "on_mouseover",
    "RightClick",
    "popUpWidnow",
    "Iframe",
    "age_of_domain",
    "DNSRecord",
    "web_traffic",
    "Page_Rank",
    "Google_Index",
    "Links_pointing_to_page",
    "Statistical_report",
]

CLASS_LABEL_MAPPING = {
    0: "phishing",
    1: "legitimate",
}


class NetworkModel:
    def __init__(self, preprocessor, model, expected_features=None):
        try:
            self.preprocessor = preprocessor
            self.model = model
            self.expected_features = expected_features
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @property
    def expected_feature_names(self):
        """
        Determines expected feature names:
        1. Explicitly configured expected_features.
        2. Feature names recorded on fitted preprocessor if available.
        3. Fallback to default 30 EXPECTED_FEATURES.
        """
        if getattr(self, "expected_features", None) is not None:
            return list(self.expected_features)

        preprocessor = getattr(self, "preprocessor", None)
        if preprocessor is not None:
            if hasattr(preprocessor, "feature_names_in_") and preprocessor.feature_names_in_ is not None:
                return list(preprocessor.feature_names_in_)
            if hasattr(preprocessor, "steps"):
                for _, step in preprocessor.steps:
                    if hasattr(step, "feature_names_in_") and step.feature_names_in_ is not None:
                        return list(step.feature_names_in_)
        return list(EXPECTED_FEATURES)

    def validate_and_prepare_input(self, x) -> pd.DataFrame:
        """
        Validates input structure, handles target column exclusion,
        and enforces exact feature column ordering matching training.
        Accepts: pd.DataFrame, dict, list of dicts, or np.ndarray.
        Returns: pd.DataFrame with expected feature columns.
        """
        try:
            expected = self.expected_feature_names
            num_expected = len(expected)

            if isinstance(x, dict):
                df = pd.DataFrame([x])
            elif isinstance(x, list):
                if len(x) == 0:
                    raise ValueError("Input list cannot be empty.")
                if isinstance(x[0], dict):
                    df = pd.DataFrame(x)
                else:
                    df = pd.DataFrame(x, columns=expected)
            elif isinstance(x, np.ndarray):
                if x.ndim == 1:
                    x = x.reshape(1, -1)
                if x.shape[1] != num_expected:
                    raise ValueError(
                        f"Expected {num_expected} features, got numpy array with shape {x.shape}."
                    )
                df = pd.DataFrame(x, columns=expected)
            elif isinstance(x, pd.DataFrame):
                df = x.copy()
            else:
                raise TypeError(f"Unsupported input type for prediction: {type(x).__name__}")

            # Target column exclusion: never allow target column in predictor features
            if TARGET_COLUMN in df.columns:
                logging.warning(f"Target column '{TARGET_COLUMN}' found in input data; excluding it from features.")
                df = df.drop(columns=[TARGET_COLUMN])

            # If columns are default RangeIndex and width matches expected, map to expected
            if list(df.columns) == list(range(num_expected)):
                df.columns = expected

            # Check for missing feature columns
            missing_cols = set(expected) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Input is missing required features: {sorted(list(missing_cols))}")

            # Realign to exact expected feature ordering
            df = df[expected]
            return df

        except (ValueError, TypeError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict(self, x):
        """
        Returns binary class predictions: 0 for phishing, 1 for legitimate.
        """
        try:
            df = self.validate_and_prepare_input(x)
            x_transform = self.preprocessor.transform(df)
            y_hat = self.model.predict(x_transform)
            return y_hat
        except (ValueError, TypeError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict_proba(self, x):
        """
        Returns prediction probabilities if supported by the underlying estimator.
        """
        try:
            df = self.validate_and_prepare_input(x)
            x_transform = self.preprocessor.transform(df)
            if hasattr(self.model, "predict_proba"):
                return self.model.predict_proba(x_transform)
            return None
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict_with_details(self, x) -> list:
        """
        Returns structured prediction details:
        [{"prediction": "phishing"|"legitimate", "class_id": 0|1, "model_score": float|None}]
        """
        try:
            df = self.validate_and_prepare_input(x)
            y_pred = self.predict(df)
            probabilities = self.predict_proba(df)

            results = []
            for i, class_id in enumerate(y_pred):
                class_id_int = int(class_id)
                label = CLASS_LABEL_MAPPING.get(class_id_int, "unknown")
                score = None
                if probabilities is not None:
                    # Dynamically look up class 1 index via classes_ if available
                    if hasattr(self.model, "classes_"):
                        classes_list = [int(c) for c in self.model.classes_]
                        if 1 in classes_list:
                            score = float(probabilities[i, classes_list.index(1)])
                        else:
                            score = float(probabilities[i, 1]) if probabilities.shape[1] > 1 else float(probabilities[i, 0])
                    else:
                        score = float(probabilities[i, 1]) if probabilities.shape[1] > 1 else float(probabilities[i, 0])

                results.append({
                    "prediction": label,
                    "class_id": class_id_int,
                    "model_score": score,
                })
            return results
        except (ValueError, TypeError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        