import os
import sys
import pandas as pd
from typing import Union, List, Dict, Any
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel, EXPECTED_FEATURES

DEFAULT_MODEL_PATH = "final_model/model.pkl"


class PredictionPipeline:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH)
        self.model: NetworkModel = None

    def load_model(self) -> NetworkModel:
        """
        Safely loads the trained NetworkModel instance from disk.
        Produces clear, actionable errors without exposing sensitive environment paths.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model artifact not found at '{self.model_path}'. "
                "Ensure the training pipeline has been executed and final model saved."
            )
        try:
            obj = load_object(self.model_path)
            if not isinstance(obj, NetworkModel):
                raise TypeError(
                    f"Loaded artifact is not a valid NetworkModel instance (got {type(obj).__name__})."
                )
            self.model = obj
            logging.info(f"Successfully loaded NetworkModel from {self.model_path}")
            return self.model
        except (FileNotFoundError, TypeError, ValueError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def is_model_loaded(self) -> bool:
        return self.model is not None

    def predict(self, input_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]):
        """
        Runs binary class predictions on valid input features.
        """
        try:
            if self.model is None:
                self.load_model()
            return self.model.predict(input_data)
        except (FileNotFoundError, TypeError, ValueError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict_with_details(self, input_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Runs prediction and returns structured output:
        [{'prediction': 'phishing'|'legitimate', 'class_id': 0|1, 'model_score': float|None}]
        """
        try:
            if self.model is None:
                self.load_model()
            return self.model.predict_with_details(input_data)
        except (FileNotFoundError, TypeError, ValueError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict_url(
        self,
        url: str,
        allow_heuristics: bool = False,
        fetch_network: bool = True,
        mock_html: str = None,
        mock_dns: bool = None,
    ) -> Dict[str, Any]:
        """
        Extracts 30 features from a submitted URL and runs model prediction.
        Enforces SSRF protections and returns structured pipeline details.
        """
        try:
            from networksecurity.components.url_feature_extractor import URLFeatureExtractor
            extractor = URLFeatureExtractor()
            extraction_res = extractor.extract_features(
                url=url,
                allow_heuristics=allow_heuristics,
                fetch_network=fetch_network,
                mock_html=mock_html,
                mock_dns=mock_dns,
            )

            coverage = extraction_res["feature_coverage"]
            if coverage == "incomplete":
                return {
                    "status": "unsupported_features",
                    "url": url,
                    "prediction": None,
                    "class_id": None,
                    "model_score": None,
                    "feature_coverage": coverage,
                    "extracted_count": extraction_res["extracted_count"],
                    "total_expected": extraction_res["total_expected"],
                    "features": extraction_res["features"],
                    "stages": extraction_res["stages"],
                    "unsupported_features": extraction_res["unsupported_features"],
                    "warnings": extraction_res["warnings"],
                    "message": (
                        "Feature vector is incomplete because third-party intelligence services "
                        "(e.g. Alexa Rank, Google PageRank) are retired or unavailable. "
                        "Enable 'allow_heuristics' to apply documented baseline defaults."
                    ),
                }

            # Predict with full feature vector
            preds = self.predict_with_details(extraction_res["features"])
            if not preds:
                raise ValueError("Inference returned empty results for URL feature vector.")

            primary = preds[0]
            return {
                "status": "success",
                "url": url,
                "prediction": primary["prediction"],
                "class_id": primary["class_id"],
                "model_score": primary["model_score"],
                "feature_coverage": coverage,
                "extracted_count": extraction_res["extracted_count"],
                "total_expected": extraction_res["total_expected"],
                "features": extraction_res["features"],
                "stages": extraction_res["stages"],
                "unsupported_features": [],
                "warnings": extraction_res["warnings"],
            }
        except (FileNotFoundError, TypeError, ValueError):
            raise
        except Exception as e:
            raise NetworkSecurityException(e, sys)
