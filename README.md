# 🛡️ Network Security - Phishing Detection

This project implements an end-to-end ML pipeline for detecting phishing attacks from network data. It automates data ingestion, validation, transformation, model training, and experiment tracking using MLflow, while maintaining modular code and artifacts for reproducibility.
## 🛠️ Tech Stack  

### 📊 Data Processing  
- 🐼 Pandas ![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas&logoColor=white)  
- 🔢 NumPy ![NumPy](https://img.shields.io/badge/-NumPy-013243?logo=numpy&logoColor=white)  
- 📝 PyYAML ![PyYAML](https://img.shields.io/badge/-PyYAML-yellow)  
- 📦 Dill ![Dill](https://img.shields.io/badge/-Dill-green)  

### 🤖 Machine Learning  
- 🎯 Scikit-Learn ![Scikit-Learn](https://img.shields.io/badge/-Scikit--Learn-F7931E?logo=scikitlearn&logoColor=white)  

### 📈 Visualization  
- 📊 Matplotlib ![Matplotlib](https://img.shields.io/badge/-Matplotlib-0C55A5)  
- 🌊 Seaborn ![Seaborn](https://img.shields.io/badge/-Seaborn-268BD2)  

### 🗄️ Database  
- 🍃 MongoDB ![MongoDB](https://img.shields.io/badge/-MongoDB-47A248?logo=mongodb&logoColor=white)  
- 🔌 PyMongo ![PyMongo](https://img.shields.io/badge/-PyMongo-47A248)  

### ⚙️ MLOps & Tracking  
- 📊 MLflow ![MLflow](https://img.shields.io/badge/-MLflow-0194E2?logo=mlflow&logoColor=white)  
- 🚀 DagsHub ![DagsHub](https://img.shields.io/badge/-DagsHub-orange)  
- 🐳 Docker ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)  

### 💻 Core  
- 🐍 Python ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)  

## 🚀 Features

- Data Pipeline
  - 📥 Data Ingestion (CSV → Feature Store → Train/Test split)
  - ✅ Data Validation (Schema checks & drift detection)
  - 🔄 Data Transformation (Preprocessing & feature engineering)-
  - 🤖 Model Training (ML algorithms for phishing detection)

- Experiment Tracking with MLflow
  - Logs metrics: f1_score, precision_score, recall_score
  - Saves trained models & parameters
  - Supports model versioning
- Modular Codebase
  - components/ → ingestion, transformation, validation, training
  - entity/ → pipeline configs & artifact entities
  - utils/ → helper utilities (metrics, estimators, logging)
- Production-Ready Setup
  - 🐳 Docker support
  - 📊 Logs & Artifacts stored with timestamps
  - 📂 Clean separation of raw, processed, and validated data

## 🏗️ Project Structure
```
.
├── Artifacts/
│   ├── 10_01_2025_19_10_31/
│   │   ├── data_ingestion/
│   │   │   └── feature_store/
│   │   │       └── phishing.csv
│   │   ├── data_transformation/
│   │   │   └── transformed/
│   │   │       ├── test.csv
│   │   │       └── train.csv
│   │   ├── data_validation/
│   │   │   ├── drift_report/
│   │   │   │   └── report.yaml
│   │   │   └── validated/
│   │   │       └── phishing.csv
│   │   └── model_trainer/
│   │       ├── model/
│   │       │   └── model.pkl
│   │       └── mlflow/
│   │           └── metric_score/
│   │               └── model_score.yaml
│   ├── 10_01_2025_19_34_35/
│   └── 10_01_2025_20_25_12/
│       ├── data_ingestion/
│       ├── data_transformation/
│       ├── data_validation/
│       └── model_trainer/
├── data_schema/
│   └── schema.yaml
├── logs/
│   ├── running_log.log
│   ├── 10_01_2025_19_10_31/
│   ├── 10_01_2025_19_34_35/
│   └── 10_01_2025_20_25_12/
├── mlruns/
│   └── 0/
│       ├── meta.yaml
│       ├── <multiple runs>/
│       │   ├── artifacts/
│       │   ├── metrics/
│       │   ├── params/
│       │   └── meta.yaml
│       └── experiments/
├── Network_Data/
│   └── phishing.csv
├── networksecurity/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   ├── data_validation.py
│   │   └── model_trainer.py
│   ├── entity/
│   │   ├── artifact_entity.py
│   │   └── config_entity.py
│   ├── exception/
│   │   └── __init__.py
│   ├── logging/
│   │   └── __init__.py
│   ├── pipeline/
│   │   └── training_pipeline.py
│   └── utils/
│       ├── __init__.py
│       ├── main_utils.py
│       ├── metric_evaluation.py
│       └── model_estimator.py
├── notebooks/
│   ├── Data_Preprocessing.ipynb
│   └── EDA.ipynb
├── .dockerignore
├── .gitignore
├── application.py
├── Dockerfile
├── main.py
├── push_data.py
├── README.md
├── requirements.txt
├── setup.py
└── test_mongodb.py
```

## ⚙️ Installation

- Clone the repository
```
git clone https://github.com/yourusername/network-security.git
cd network-security
```

- Create a virtual environment & install dependencies
```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

- Run MLflow Tracking Server (optional)
```
mlflow ui
```
## ▶️ Usage

- Run full pipeline
```
python main.py
```
- Train model only
```
python -m networksecurity.components.model_trainer
```
- Validate schema
```
python -m networksecurity.components.data_validation
```
## 📊 Experiment Tracking (MLflow)

- Start MLflow UI
- mlflow ui
- Visit: http://127.0.0.1:5000
- Track metrics (precision, recall, f1_score) and compare models

## 🐳 Docker Setup

- Build image:
```

docker build -t network-security .
```

- Run container:
```
docker run -it network-security
```
- 📂 Artifacts & Logs
```
- Artifacts/ → Data ingestion, validation reports, trained models

- logs/ → Timestamped logs for pipeline debugging

- mlruns/ → MLflow experiments
```
## 📌 Roadmap

-  Deploy as REST API (FastAPI/Flask)

 - CI/CD integration (GitHub Actions)

 - Cloud storage for artifacts (AWS S3 / GCP)

-  Streamlit dashboard for monitoring

## 👨‍💻 Author

**Rahul Manchanda**
- 📧 Email: [rahulmanchanda015@gmail.com](mailto:rahulmanchanda015@gmail.com)  
- 💼 LinkedIn: [Rahul Manchanda](https://www.linkedin.com/in/rahul-manchanda-3959b120a/)  
- 💻 GitHub: [rahul15-manch](https://github.com/rahul15-manch)  
