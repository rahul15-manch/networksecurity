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
