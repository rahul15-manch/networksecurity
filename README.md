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

## 🛡️ PhishGuard Frontend Application

A cybersecurity SaaS dashboard built with **React**, **Vite**, **TypeScript**, and **Tailwind CSS** featuring a dedicated Black, Red, Charcoal, and White theme.

### 1. Design & Appearance
- **Color Palette:**
  - Primary Background: `#090909` (Deep void black)
  - Card & Surfaces: `#171717` (Charcoal panels with `#303030` subtle borders)
  - Accents: `#DC2626` (Crimson red), `#EF4444` (Hover red), `#991B1B` (Deep red)
  - Text: `#F5F5F5` (High-contrast white) and `#A3A3A3` (Muted technical gray)
  - Indicators: Accessible green (`#10B981`) for legitimate verdicts to avoid confusing safe outcomes with alerts.

### 2. Frontend Installation & Local Startup

Navigate to the `frontend/` directory and install dependencies:
```bash
cd frontend
npm install
```

Start the Vite development server (proxies `/api` to backend at `http://localhost:8000`):
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Production Build & Verification

Compile TypeScript and build the optimized production bundle:
```bash
npm run build
```
The output will be generated in `frontend/dist/`.

### 4. Running Frontend Tests

Execute the Vitest test suite covering component rendering, API error handling, and duplicate submission prevention:
```bash
npm run test
```

### 5. Frontend Environment Configuration

Configure the backend API URL via `VITE_API_BASE_URL`:
- Copy the template:
  ```bash
  cp .env.example .env
  ```
- Default configuration:
  ```ini
  VITE_API_BASE_URL=http://localhost:8000
  ```

### 6. Key Features & Screens
1. **End-to-End URL Phishing Classifier:**
   - Real-time submission of live web URLs (`http` and `https`).
   - Automated 4-stage feature pipeline: URL syntax & SSRF defense -> Lexical analysis -> DNS/TLS inspection -> Safe DOM attribute parsing.
   - Dual probability bar ($P(\text{legitimate})$ vs $P(\text{phishing})$).
   - Detailed pipeline stage breakdown (lexical count, DNS/TLS status, DOM elements parsed).
   - Strict mode vs Documented Baseline Heuristic toggle for retired services.
2. **Analyze Vector:**
   - Real-time prediction card with model confidence bar.
   - Quick-load benchmark presets (Credential Harvester, Enterprise Banking Portal, Ambiguous Domain).
   - Interactive 30-feature editor grouped by category (Lexical & URL, Security & SSL, Domain & DNS, Page Content & Scripting).
   - Duplicate-submission prevention and accessible loading states.
3. **Model Metrics:**
   - Visual display of cross-validation F1 (95.52%), test accuracy (96.28%), test F1 (96.19%), and ROC-AUC (99.41%).
   - Candidate model comparison matrix (Random Forest vs Gradient Boosting, Decision Tree, Logistic Regression, AdaBoost).
4. **Pipeline & Limits:**
   - 4-stage pipeline visualization and transparent security boundaries.

---

## 🌐 End-to-End URL Feature Extraction & Safety Architecture

The URL feature extraction engine (`networksecurity/components/url_feature_extractor.py`) bridges raw user URLs and the 30-feature trained Random Forest classifier.

### Feature Capability Map (30 Features)

| Feature Name | Category | Extraction Source | Reliability | Domain & Heuristic Fallback |
| :--- | :--- | :--- | :--- | :--- |
| `having_IP_Address` | Lexical | Hostname parsing (IPv4/IPv6/hex) | High | `{-1, 1}`: -1 if IP, 1 if domain |
| `URL_Length` | Lexical | URL character length | High | `{-1, 0, 1}`: 1 if <54, 0 if 54-75, -1 if >75 |
| `Shortining_Service` | Lexical | Known shortener registry (bit.ly, etc.) | High | `{-1, 1}`: -1 if shortener, 1 if direct |
| `having_At_Symbol` | Lexical | String search for `@` | High | `{-1, 1}`: -1 if `@` present, 1 if clean |
| `double_slash_redirecting` | Lexical | Path search for `//` after proto | High | `{-1, 1}`: -1 if `//` in path, 1 if clean |
| `Prefix_Suffix` | Lexical | Hyphen `-` search in domain labels | High | `{-1, 1}`: -1 if `-` present, 1 if clean |
| `having_Sub_Domain` | Lexical | Domain label dots count (minus www) | High | `{-1, 0, 1}`: 1 if <=1, 0 if 2, -1 if >2 |
| `SSLfinal_State` | DNS/TLS | TLS certificate chain & validity | High | `{-1, 0, 1}`: 1 if trusted >=1yr, 0 if untrusted, -1 if HTTP/err |
| `Domain_registeration_length`| External | WHOIS validity period | Retired/Commercial | `{-1, 1}`: Fallback -1 (conservative baseline) |
| `Favicon` | HTML DOM | `<link rel="icon">` domain origin | High | `{-1, 1}`: -1 if foreign domain, 1 if same/relative |
| `port` | Lexical | URL port inspection | High | `{-1, 1}`: 1 if standard (80/443/8080), -1 if nonstandard |
| `HTTPS_token` | Lexical | `https` string search in hostname | High | `{-1, 1}`: -1 if `https` in host, 1 if clean |
| `Request_URL` | HTML DOM | `<img>`, `<video>`, `<audio>` sources | High | `{-1, 1}`: -1 if >=61% foreign media, 1 if <61% |
| `URL_of_Anchor` | HTML DOM | `<a>` tags with `#`, `javascript:`, foreign | High | `{-1, 0, 1}`: -1 if >67%, 0 if 31-67%, 1 if <31% |
| `Links_in_tags` | HTML DOM | `<meta>`, `<script>`, `<link>` domains | High | `{-1, 0, 1}`: -1 if >81%, 0 if 17-81%, 1 if <17% |
| `SFH` | HTML DOM | `<form action="...">` origin analysis | High | `{-1, 0, 1}`: -1 if empty/'about:blank', 0 foreign, 1 same |
| `Submitting_to_email` | HTML DOM | `mailto:` protocol in forms/anchors | High | `{-1, 1}`: -1 if `mailto:` present, 1 if clean |
| `Abnormal_URL` | Lexical | Host identity vs path consistency | High | `{-1, 1}`: 1 if normal host identity, -1 if abnormal |
| `Redirect` | HTTP Net | HTTP 3xx redirect hop counter | High | `{0, 1}`: 0 if >1 redirects, 1 if <=1 redirect |
| `on_mouseover` | HTML DOM | `window.status` manipulation search | High | `{-1, 1}`: -1 if status modified, 1 if clean |
| `RightClick` | HTML DOM | `event.button==2` or contextmenu block | High | `{-1, 1}`: -1 if right click disabled, 1 if clean |
| `popUpWidnow` | HTML DOM | `window.open` credential prompt search | High | `{-1, 1}`: -1 if popup prompt, 1 if clean |
| `Iframe` | HTML DOM | `<iframe>` with `frameborder="0"` / hidden | High | `{-1, 1}`: -1 if invisible iframe, 1 if clean |
| `age_of_domain` | External | WHOIS domain creation date | Retired/Commercial | `{-1, 1}`: Fallback 1 if active TLS/DNS, else -1 |
| `DNSRecord` | DNS/TLS | DNS A/AAAA resolution probe | High | `{-1, 1}`: 1 if domain resolves, -1 if NXDOMAIN |
| `web_traffic` | External | Alexa traffic popularity rank | Sunset May 2022 | `{-1, 0, 1}`: Fallback -1 (conservative baseline) |
| `Page_Rank` | External | Google PageRank Toolbar API | Sunset Apr 2016 | `{-1, 1}`: Fallback -1 (conservative baseline) |
| `Google_Index` | External | Search engine index status | Commercial/Private | `{-1, 1}`: Fallback 1 if live site accessible, else -1 |
| `Links_pointing_to_page` | External | Inbound backlinks count | Commercial API | `{-1, 0, 1}`: Fallback 0 (neutral unknown) |
| `Statistical_report` | External | PhishTank / StopBadware blacklist | External Feed | `{-1, 1}`: Fallback 1 (clean default) |

### SSRF Protection & Safety Controls
1. **Scheme Restriction:** Accepts strictly `http` and `https` schemes; rejects `file://`, `ftp://`, `data:`, `javascript:`, and malformed protocols.
2. **Credentials Blocking:** Rejects URLs containing embedded user authentication (`http://user:pass@host`).
3. **Private Network & Loopback Defense:**
   - Pre-resolves DNS before any network connection.
   - Blocks private RFC 1918 blocks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
   - Blocks loopback (`127.0.0.0/8`, `::1`) and localhost hostnames (`localhost`, `*.localhost`, `*.local`).
   - Blocks cloud metadata and link-local destinations (`169.254.0.0/16`, `fe80::/10`).
   - Blocks multicast and reserved IP spaces (`224.0.0.0/4`, `240.0.0.0/4`).
4. **Execution Safety:** HTML is parsed using a streaming Python standard library parser without JavaScript execution.
5. **Resource Caps:** Enforces a strict 3.0-second timeout, 512 KB max download limit, and maximum 2 redirect hops.

### API Contract (`POST /predict-url`)

**Request:**
```json
{
  "url": "https://example.com",
  "allow_heuristics": true,
  "fetch_network": true
}
```

**Response (Success with Heuristic Baseline):**
```json
{
  "status": "success",
  "url": "https://example.com",
  "prediction": "legitimate",
  "class_id": 1,
  "model_score": 0.71875,
  "feature_coverage": "heuristic",
  "extracted_count": 30,
  "total_expected": 30,
  "features": { ... 30 discrete feature values ... },
  "stages": {
    "url_lexical": {"status": "success", "count": 10},
    "dns_tls": {"status": "success", "count": 2},
    "html_content": {"status": "success", "count": 11},
    "external_intel": {"status": "heuristic_baseline", "count": 7}
  },
  "unsupported_features": [],
  "warnings": [
    "External intelligence features (Alexa Rank, Google PageRank) use documented baseline defaults because original upstream APIs have been retired."
  ]
}
```

**Response (Strict Mode / Unsupported Features):**
```json
{
  "status": "unsupported_features",
  "url": "https://example.com",
  "prediction": null,
  "class_id": null,
  "model_score": null,
  "feature_coverage": "incomplete",
  "extracted_count": 23,
  "total_expected": 30,
  "features": { ... 23 features ... },
  "stages": { ... },
  "unsupported_features": [
    "web_traffic", "Page_Rank", "Google_Index", "Links_pointing_to_page",
    "Statistical_report", "Domain_registeration_length", "age_of_domain"
  ],
  "message": "Feature vector is incomplete because third-party intelligence services (e.g. Alexa Rank, Google PageRank) are retired or unavailable. Enable 'allow_heuristics' to apply documented baseline defaults."
}
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
