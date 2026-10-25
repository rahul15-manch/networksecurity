import os
import sys

# Ensure project root is in Python module search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Preload model in serverless environment if available
from app import app, pipeline

try:
    if not pipeline.is_model_loaded():
        pipeline.load_model()
except Exception as e:
    # Model will lazy-load on first inference request if not ready on cold start
    pass
