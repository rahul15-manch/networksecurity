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

## 🚀 Prediction API & Model Serving

A minimal, production-grade FastAPI serving layer provides real-time and batch phishing classification using the trained `NetworkModel` artifact.

### 1. Installation & Dependencies

Install requirements including API dependencies (`fastapi`, `uvicorn`, `pydantic`):
```bash
pip install -r requirements.txt
```

### 2. Model Artifact Configuration

The inference pipeline loads the serialized `NetworkModel` (containing fitted imputer and classifier) from:
- Default path: `final_model/model.pkl`
- Custom path: Configure via the `MODEL_PATH` environment variable:
  ```bash
  export MODEL_PATH="final_model/model.pkl"
  ```
Refer to `.env.example` for optional service environment configurations (`PORT`, `HOST`, `CORS_ORIGINS`).

### 3. Starting the Service Locally

Launch using `uvicorn`:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
Or directly run the application entrypoint:
```bash
python app.py
```
Interactive OpenAPI documentation will be accessible at: `http://localhost:8000/docs`

### 4. API Endpoints & Contract

#### `GET /health`
Returns the operational health and artifact loading state.
- **Response (200 OK):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "supported_features_count": 30
}
```

#### `POST /predict`
Evaluates a single website feature vector.
- **Request (200 OK):**
```json
{
  "having_IP_Address": -1,
  "URL_Length": 1,
  "Shortining_Service": 1,
  "having_At_Symbol": 1,
  "double_slash_redirecting": -1,
  "Prefix_Suffix": -1,
  "having_Sub_Domain": -1,
  "SSLfinal_State": -1,
  "Domain_registeration_length": -1,
  "Favicon": 1,
  "port": 1,
  "HTTPS_token": -1,
  "Request_URL": 1,
  "URL_of_Anchor": -1,
  "Links_in_tags": 1,
  "SFH": -1,
  "Submitting_to_email": -1,
  "Abnormal_URL": -1,
  "Redirect": 0,
  "on_mouseover": 1,
  "RightClick": 1,
  "popUpWidnow": 1,
  "Iframe": 1,
  "age_of_domain": -1,
  "DNSRecord": -1,
  "web_traffic": -1,
  "Page_Rank": -1,
  "Google_Index": 1,
  "Links_pointing_to_page": 1,
  "Statistical_report": -1
}
```
- **Response (200 OK):**
```json
{
  "prediction": "phishing",
  "class_id": 0,
  "model_score": 0.03125
}
```

#### `POST /predict/batch`
Evaluates multiple website feature vectors in a single call.
- **Request Body:** `{"samples": [ ...list of feature objects... ]}`
- **Response (200 OK):**
```json
{
  "total_samples": 2,
  "predictions": [
    {
      "prediction": "legitimate",
      "class_id": 1,
      "model_score": 0.9453
    },
    {
      "prediction": "phishing",
      "class_id": 0,
      "model_score": 0.0312
    }
  ]
}
```

### 5. Expected Feature Schema & Ordering

The model accepts exactly 30 discrete engineered domain/URL features in the following canonical order:
1. `having_IP_Address`
2. `URL_Length`
3. `Shortining_Service`
4. `having_At_Symbol`
5. `double_slash_redirecting`
6. `Prefix_Suffix`
7. `having_Sub_Domain`
8. `SSLfinal_State`
9. `Domain_registeration_length`
10. `Favicon`
11. `port`
12. `HTTPS_token`
13. `Request_URL`
14. `URL_of_Anchor`
15. `Links_in_tags`
16. `SFH`
17. `Submitting_to_email`
18. `Abnormal_URL`
19. `Redirect` (allowed values: 0, 1)
20. `on_mouseover`
21. `RightClick`
22. `popUpWidnow`
23. `Iframe`
24. `age_of_domain`
25. `DNSRecord`
26. `web_traffic`
27. `Page_Rank`
28. `Google_Index`
29. `Links_pointing_to_page`
30. `Statistical_report`

Allowed discrete values: `{-1, 0, 1}` (except `Redirect` which is `{0, 1}`). Target column `Result` must not be supplied, but is safely stripped if passed.

### 6. Target Encoding & Class Mapping

- `0` → `phishing` (malicious)
- `1` → `legitimate` (benign)
- `model_score` → Estimated probability of the `legitimate` class ($P(Y=1|X)$).

### 7. Running Tests

Run the full automated test suite (55 unit and integration tests):
```bash
./venv/bin/python3 -m unittest discover -s tests -v
```

### 8. Known Limitations

- **Raw URLs not accepted:** The model and API do not currently implement automatic URL scraping, DNS queries, or lexical feature extraction. Predictions must be made using pre-computed engineered features. Submitting raw string URLs (e.g. `https://example.com`) directly is not supported.

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
