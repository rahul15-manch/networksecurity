import os
import sys
import tempfile
import unittest
import warnings
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore", category=RuntimeWarning)

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ClassificationMetricArtifact,
    ModelTrainerArtifact,
)
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    ModelTrainerConfig,
)
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.utils.main_utils.utils import evaluate_models, load_object, save_object
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.ml_utils.model.estimator import NetworkModel


class TestLeakageSafeModelSelection(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        # 100 train samples, 30 features
        self.X_train = np.random.choice([-1, 0, 1], size=(100, 30))
        self.y_train = np.random.choice([0, 1], size=100)

        # 40 test samples
        self.X_test = np.random.choice([-1, 0, 1], size=(40, 30))
        self.y_test = np.random.choice([0, 1], size=40)

        self.models = {
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Logistic Regression": LogisticRegression(random_state=42, max_iter=200),
        }
        self.params = {
            "Decision Tree": {"criterion": ["gini", "entropy"]},
            "Logistic Regression": {"C": [0.1, 1.0]},
        }

    def test_evaluate_models_uses_cv_on_training_data_only(self):
        """Verify evaluate_models performs cross-validation without using test data."""
        # Intentionally pass test data via legacy parameters
        dummy_bad_test = np.full_like(self.X_test, 999.0)
        report = evaluate_models(
            X_train=self.X_train,
            y_train=self.y_train,
            X_test=dummy_bad_test,
            y_test=self.y_test,
            models=self.models,
            param=self.params,
            cv=3,
            scoring="f1",
            random_state=42,
        )

        self.assertIn("Decision Tree", report)
        self.assertIn("Logistic Regression", report)
        # CV scores should be valid probabilities/F1 between 0 and 1
        for name, score in report.items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_cv_results_are_deterministic_under_fixed_seed(self):
        """Verify that evaluate_models produces identical CV scores under the same random seed."""
        models1 = {
            "Decision Tree": DecisionTreeClassifier(random_state=42),
        }
        params1 = {"Decision Tree": {"criterion": ["gini", "entropy"]}}

        models2 = {
            "Decision Tree": DecisionTreeClassifier(random_state=42),
        }
        params2 = {"Decision Tree": {"criterion": ["gini", "entropy"]}}

        report1 = evaluate_models(self.X_train, self.y_train, models1, params1, cv=3, random_state=42)
        report2 = evaluate_models(self.X_train, self.y_train, models2, params2, cv=3, random_state=42)

        self.assertAlmostEqual(report1["Decision Tree"], report2["Decision Tree"], places=6)

    def test_best_estimator_is_refitted_and_returned_in_models_dict(self):
        """Verify that evaluate_models replaces the input model with the refitted best estimator."""
        models = {"Decision Tree": DecisionTreeClassifier(random_state=42)}
        params = {"Decision Tree": {"criterion": ["gini", "entropy"]}}

        report = evaluate_models(self.X_train, self.y_train, models, params, cv=3)

        best_estimator = models["Decision Tree"]
        # Must have fitted attributes such as classes_ and tree_
        self.assertTrue(hasattr(best_estimator, "classes_"))
        self.assertTrue(hasattr(best_estimator, "tree_"))


class TestClassificationMetricsAndEvaluation(unittest.TestCase):
    def test_get_classification_score_computes_all_metrics(self):
        """Verify get_classification_score computes F1, precision, recall, accuracy, and ROC-AUC."""
        y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
        y_pred = np.array([0, 1, 0, 1, 1, 1, 0, 0])
        # Probabilities for class 1
        y_prob = np.array([0.1, 0.9, 0.2, 0.8, 0.7, 0.85, 0.3, 0.05])

        metrics = get_classification_score(y_true, y_pred, y_prob)

        self.assertIsInstance(metrics, ClassificationMetricArtifact)
        self.assertIsNotNone(metrics.f1_score)
        self.assertIsNotNone(metrics.precision_score)
        self.assertIsNotNone(metrics.recall_score)
        self.assertIsNotNone(metrics.accuracy_score)
        self.assertIsNotNone(metrics.roc_auc_score)
        self.assertGreater(metrics.roc_auc_score, 0.5)

    def test_get_classification_score_handles_missing_probabilities_gracefully(self):
        """Verify ROC-AUC is gracefully set to None when probabilities are unavailable."""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])

        metrics = get_classification_score(y_true, y_pred, y_prob=None)
        self.assertIsNone(metrics.roc_auc_score)
        self.assertEqual(metrics.accuracy_score, 1.0)
        self.assertEqual(metrics.f1_score, 1.0)

    def test_positive_class_convention(self):
        """Verify class 1 (legitimate) is treated as positive class in precision and recall."""
        # 0 = Phishing, 1 = Legitimate
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 1, 1, 1])  # 1 False Positive for class 1, 2 True Positives

        metrics = get_classification_score(y_true, y_pred)
        # Precision = 2 TP / (2 TP + 1 FP) = 2/3
        self.assertAlmostEqual(metrics.precision_score, 2 / 3, places=4)
        # Recall = 2 TP / (2 TP + 0 FN) = 1.0
        self.assertAlmostEqual(metrics.recall_score, 1.0, places=4)


class TestModelTrainerPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pipe_cfg = TrainingPipelineConfig()
        self.pipe_cfg.artifact_dir = self.temp_dir.name
        self.trainer_cfg = ModelTrainerConfig(self.pipe_cfg)

        # Create dummy preprocessor and numpy arrays
        np.random.seed(42)
        n_train, n_test, n_feats = 80, 20, 30
        X_tr = np.random.choice([-1, 0, 1], size=(n_train, n_feats))
        # Correlate target with first feature so model learns clean pattern
        y_tr = (X_tr[:, 0] == 1).astype(int).reshape(-1, 1)
        train_arr = np.hstack([X_tr, y_tr])

        X_te = np.random.choice([-1, 0, 1], size=(n_test, n_feats))
        y_te = (X_te[:, 0] == 1).astype(int).reshape(-1, 1)
        test_arr = np.hstack([X_te, y_te])

        self.train_npy = os.path.join(self.temp_dir.name, "train.npy")
        self.test_npy = os.path.join(self.temp_dir.name, "test.npy")
        np.save(self.train_npy, train_arr)
        np.save(self.test_npy, test_arr)

        # Create dummy preprocessor object
        from sklearn.pipeline import Pipeline
        from sklearn.impute import SimpleImputer
        dummy_preprocessor = Pipeline([("imputer", SimpleImputer(strategy="most_frequent"))])
        dummy_preprocessor.fit(X_tr)

        self.prep_path = os.path.join(self.temp_dir.name, "preprocessor.pkl")
        save_object(self.prep_path, dummy_preprocessor)

        self.trans_artifact = DataTransformationArtifact(
            transformed_train_file_path=self.train_npy,
            transformed_test_file_path=self.test_npy,
            transformed_object_file_path=self.prep_path,
        )
        self.trainer = ModelTrainer(self.trainer_cfg, self.trans_artifact)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initiate_model_trainer_end_to_end(self):
        """Verify model trainer executes CV selection, evaluates on test once, and produces artifact."""
        artifact = self.trainer.initiate_model_trainer()

        self.assertIsInstance(artifact, ModelTrainerArtifact)
        self.assertTrue(os.path.exists(artifact.trained_model_file_path))

        # Check train and test metrics
        self.assertGreater(artifact.train_metric_artifact.f1_score, 0.0)
        self.assertGreater(artifact.test_metric_artifact.f1_score, 0.0)

        # Check saved NetworkModel inference
        saved_network_model = load_object(artifact.trained_model_file_path)
        self.assertIsInstance(saved_network_model, NetworkModel)

        # Predict with raw input array
        test_input = np.random.choice([-1, 0, 1], size=(5, 30))
        preds = saved_network_model.predict(test_input)
        self.assertEqual(len(preds), 5)
        self.assertTrue(set(preds).issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
