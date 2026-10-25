import sys
from networksecurity.entity.artifact_entity import ClassificationMetricArtifact
from networksecurity.exception.exception import NetworkSecurityException
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, roc_auc_score


def get_classification_score(y_true, y_pred, y_prob=None) -> ClassificationMetricArtifact:
    """
    Computes classification evaluation metrics for binary classification.
    Target convention: 0 = Phishing, 1 = Legitimate.
    Computes F1, precision, recall, accuracy, and ROC-AUC (when probability scores are provided).
    """
    try:
        model_f1 = float(f1_score(y_true, y_pred, zero_division=0))
        model_precision = float(precision_score(y_true, y_pred, zero_division=0))
        model_recall = float(recall_score(y_true, y_pred, zero_division=0))
        model_accuracy = float(accuracy_score(y_true, y_pred))

        model_roc_auc = None
        if y_prob is not None:
            try:
                # If 2D probability array (n_samples, 2), extract positive class (column 1)
                if hasattr(y_prob, "ndim") and y_prob.ndim == 2 and y_prob.shape[1] == 2:
                    scores = y_prob[:, 1]
                else:
                    scores = y_prob
                model_roc_auc = float(roc_auc_score(y_true, scores))
            except Exception:
                model_roc_auc = None

        classification_metric = ClassificationMetricArtifact(
            f1_score=model_f1,
            precision_score=model_precision,
            recall_score=model_recall,
            accuracy_score=model_accuracy,
            roc_auc_score=model_roc_auc,
        )
        return classification_metric

    except Exception as e:
        raise NetworkSecurityException(e, sys)
