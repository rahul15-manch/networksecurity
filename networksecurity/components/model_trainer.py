import os
import sys

from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig



from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
import mlflow
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def track_mlflow(self,best_model,classificationmetric,dataset_type="test"):
        try:
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
                if tracking_uri.startswith("http"):
                    mlflow.set_registry_uri(tracking_uri)

            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
            with mlflow.start_run(run_name=f"{best_model.__class__.__name__}_{dataset_type}"):
                f1_score=classificationmetric.f1_score
                precision_score=classificationmetric.precision_score
                recall_score=classificationmetric.recall_score

                mlflow.set_tag("dataset_type", dataset_type)
                mlflow.set_tag("model_name", best_model.__class__.__name__)

                # Clearly distinguish train and test metrics
                mlflow.log_metric(f"{dataset_type}_f1_score", f1_score)
                mlflow.log_metric(f"{dataset_type}_precision_score", precision_score)
                mlflow.log_metric(f"{dataset_type}_recall_score", recall_score)
                if hasattr(classificationmetric, "accuracy_score") and classificationmetric.accuracy_score is not None:
                    mlflow.log_metric(f"{dataset_type}_accuracy", classificationmetric.accuracy_score)
                if hasattr(classificationmetric, "roc_auc_score") and classificationmetric.roc_auc_score is not None:
                    mlflow.log_metric(f"{dataset_type}_roc_auc", classificationmetric.roc_auc_score)

                # Standard metric names for backwards compatibility
                mlflow.log_metric("f1_score", f1_score)
                mlflow.log_metric("precision", precision_score)
                mlflow.log_metric("recall_score", recall_score)

                # Avoid duplicate model logging; registered_model_name must be a string
                model_name = best_model.__class__.__name__
                if tracking_url_type_store != "file" and tracking_uri and tracking_uri.startswith("http"):
                    mlflow.sklearn.log_model(best_model, "model", registered_model_name=model_name)
                else:
                    mlflow.sklearn.log_model(best_model, "model")
        except Exception as e:
            logging.warning(f"MLflow tracking failed: {e}")



        
    def train_model(self, X_train, y_train, x_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(random_state=42),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(random_state=42),
            "Logistic Regression": LogisticRegression(random_state=42, max_iter=500),
            "AdaBoost": AdaBoostClassifier(random_state=42),
        }
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy'],
                'max_depth': [None, 10, 20],
            },
            "Random Forest": {
                'n_estimators': [16, 32, 64, 128],
            },
            "Gradient Boosting": {
                'learning_rate': [0.05, 0.1],
                'n_estimators': [16, 32, 64],
                'subsample': [0.8, 1.0],
            },
            "Logistic Regression": {
                'C': [0.1, 1.0, 10.0],
            },
            "AdaBoost": {
                'learning_rate': [0.1, 1.0],
                'n_estimators': [16, 32, 64],
            },
        }

        # Model selection uses stratified CV on training set ONLY.
        # Test partition is kept completely untouched to prevent data leakage.
        model_report: dict = evaluate_models(
            X_train=X_train,
            y_train=y_train,
            models=models,
            param=params,
            cv=3,
            scoring="f1",
            random_state=42,
        )

        ## Get best model score from CV report
        best_model_score = max(sorted(model_report.values()))

        ## Get best model name from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        logging.info(f"Selected best model via training CV: {best_model_name} with CV F1: {best_model_score:.4f}")

        # Check threshold
        if best_model_score < self.model_trainer_config.expected_accuracy:
            raise ValueError(f"Best model score {best_model_score:.4f} is lower than expected score {self.model_trainer_config.expected_accuracy}")

        # Evaluate on training data
        y_train_pred = best_model.predict(X_train)
        y_train_prob = best_model.predict_proba(X_train) if hasattr(best_model, "predict_proba") else None
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred, y_prob=y_train_prob)
        self.track_mlflow(best_model, classification_train_metric, dataset_type="train")

        # Evaluate ONCE on untouched held-out test data for final evaluation
        y_test_pred = best_model.predict(x_test)
        y_test_prob = best_model.predict_proba(x_test) if hasattr(best_model, "predict_proba") else None
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred, y_prob=y_test_prob)
        self.track_mlflow(best_model, classification_test_metric, dataset_type="test")

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)

        # Model pusher path
        save_object("final_model/model.pkl", Network_Model)

        ## Model Trainer Artifact
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric,
        )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact


        


       
    
    
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
