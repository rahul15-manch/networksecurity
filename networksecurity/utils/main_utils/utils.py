import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os,sys
import numpy as np
import dill
import pickle
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import r2_score, accuracy_score, f1_score

def read_yaml_file(file_path:str) -> dict:
    try:
        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    


def write_yaml_file( file_path: str,content:object,replace:bool=False)-> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path, 'w') as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e,sys) 
    

def save_numpy_array_data(file_path: str, array: np.array):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    

def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info("Entered save_object method od mainUtils class ")
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save_object method od mainUtils class ")

    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    
def load_object( file_path: str) -> object:
    try:
        if not os.path.exists(file_path):
            raise Exception (f"File {file_path} does not exist")
        with open(file_path, 'rb') as file_obj:
            return pickle.load(file_obj)
        
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    

def load_numpy_array_data( file_path: str) -> np.array:
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj)
        
    except Exception as e:
        raise NetworkSecurityException(e,sys) from e
    


def evaluate_models(X_train, y_train, *args, **kwargs) -> dict:
    """
    Evaluates candidate models using stratified cross-validation on the training set only.
    Hyperparameter tuning and model selection are conducted without accessing test data,
    preventing test partition data leakage.

    Supports both clean 4-argument call and legacy 6-argument call for backwards compatibility.
    """
    try:
        if len(args) >= 4:
            # Legacy signature: evaluate_models(X_train, y_train, X_test, y_test, models, param)
            logging.warning("evaluate_models received test partition; ignoring test sets to prevent leakage during CV selection.")
            models = args[2]
            param = args[3]
        elif len(args) == 2:
            models = args[0]
            param = args[1]
        else:
            models = kwargs.get("models")
            param = kwargs.get("param", kwargs.get("params", {}))

        if models is None or param is None:
            raise ValueError("evaluate_models requires 'models' and 'param' dictionaries.")

        cv_strategy = kwargs.get("cv", 3)
        random_state = kwargs.get("random_state", 42)
        if isinstance(cv_strategy, int):
            cv = StratifiedKFold(n_splits=cv_strategy, shuffle=True, random_state=random_state)
        else:
            cv = cv_strategy

        scoring = kwargs.get("scoring", "f1")
        report = {}

        for model_name, model in models.items():
            para = param.get(model_name, {})
            gs = GridSearchCV(
                estimator=model,
                param_grid=para,
                cv=cv,
                scoring=scoring,
                refit=True,
                n_jobs=-1,
            )
            gs.fit(X_train, y_train)

            # Update model dict with the refitted best estimator
            models[model_name] = gs.best_estimator_

            # Record the cross-validation score for selection
            best_cv_score = float(gs.best_score_)
            report[model_name] = best_cv_score
            logging.info(f"Model: {model_name} | Best CV {scoring}: {best_cv_score:.4f} | Best Params: {gs.best_params_}")

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)
