import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from networksecurity.logging.logger import logging
from networksecurity.pipeline.prediction_pipeline import PredictionPipeline
from networksecurity.utils.ml_utils.model.estimator import EXPECTED_FEATURES

# Initialize FastAPI application
app = FastAPI(
    title="Network Security - Phishing Detection API",
    description=(
        "REST API for real-time and batch phishing website classification.\n\n"
        "**Important Note:** Raw URL feature extraction is not implemented in this version. "
        "The model strictly evaluates the 30 pre-engineered domain/network security features "
        "defined in the dataset schema (discrete values: -1, 0, or 1)."
    ),
    version="1.0.0",
)

# Configure CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global prediction pipeline instance
pipeline = PredictionPipeline()


# Pydantic Request Models
class PhishingFeatureItem(BaseModel):
    having_IP_Address: int = Field(..., ge=-1, le=1, description="IP address in URL: -1 (phishing), 1 (legitimate)")
    URL_Length: int = Field(..., ge=-1, le=1, description="URL length: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    Shortining_Service: int = Field(..., ge=-1, le=1, description="Shortening service used: -1 (phishing), 1 (legitimate)")
    having_At_Symbol: int = Field(..., ge=-1, le=1, description="@ symbol present: -1 (phishing), 1 (legitimate)")
    double_slash_redirecting: int = Field(..., ge=-1, le=1, description="// redirecting: -1 (phishing), 1 (legitimate)")
    Prefix_Suffix: int = Field(..., ge=-1, le=1, description="Prefix/suffix hyphen in domain: -1 (phishing), 1 (legitimate)")
    having_Sub_Domain: int = Field(..., ge=-1, le=1, description="Subdomain count: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    SSLfinal_State: int = Field(..., ge=-1, le=1, description="SSL certificate state: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    Domain_registeration_length: int = Field(..., ge=-1, le=1, description="Domain registration length: -1 (phishing), 1 (legitimate)")
    Favicon: int = Field(..., ge=-1, le=1, description="Favicon loaded from external domain: -1 (phishing), 1 (legitimate)")
    port: int = Field(..., ge=-1, le=1, description="Non-standard port: -1 (phishing), 1 (legitimate)")
    HTTPS_token: int = Field(..., ge=-1, le=1, description="HTTPS token in domain part: -1 (phishing), 1 (legitimate)")
    Request_URL: int = Field(..., ge=-1, le=1, description="External request URLs ratio: -1 (phishing), 1 (legitimate)")
    URL_of_Anchor: int = Field(..., ge=-1, le=1, description="Anchor URLs ratio: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    Links_in_tags: int = Field(..., ge=-1, le=1, description="Tags link ratio: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    SFH: int = Field(..., ge=-1, le=1, description="Server Form Handler: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    Submitting_to_email: int = Field(..., ge=-1, le=1, description="Submits to email (mailto): -1 (phishing), 1 (legitimate)")
    Abnormal_URL: int = Field(..., ge=-1, le=1, description="Abnormal URL format: -1 (phishing), 1 (legitimate)")
    Redirect: int = Field(..., ge=0, le=1, description="Number of redirects: 0 (phishing), 1 (legitimate)")
    on_mouseover: int = Field(..., ge=-1, le=1, description="Mouseover status bar modification: -1 (phishing), 1 (legitimate)")
    RightClick: int = Field(..., ge=-1, le=1, description="Right click disabled: -1 (phishing), 1 (legitimate)")
    popUpWidnow: int = Field(..., ge=-1, le=1, description="Popup window with input: -1 (phishing), 1 (legitimate)")
    Iframe: int = Field(..., ge=-1, le=1, description="Iframe redirection: -1 (phishing), 1 (legitimate)")
    age_of_domain: int = Field(..., ge=-1, le=1, description="Age of domain: -1 (phishing), 1 (legitimate)")
    DNSRecord: int = Field(..., ge=-1, le=1, description="DNS record exists: -1 (phishing), 1 (legitimate)")
    web_traffic: int = Field(..., ge=-1, le=1, description="Alexa web traffic rank: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    Page_Rank: int = Field(..., ge=-1, le=1, description="Google PageRank: -1 (phishing), 1 (legitimate)")
    Google_Index: int = Field(..., ge=-1, le=1, description="Indexed in Google: -1 (phishing), 1 (legitimate)")
    Links_pointing_to_page: int = Field(..., ge=-1, le=1, description="Inbound links count: -1 (phishing), 0 (suspicious), 1 (legitimate)")
    Statistical_report: int = Field(..., ge=-1, le=1, description="Appears on PhishTank/StopBadware: -1 (phishing), 1 (legitimate)")

    model_config = {
        "extra": "ignore"  # Automatically ignore accidental 'Result' or auxiliary fields
    }


class BatchPredictionRequest(BaseModel):
    samples: List[PhishingFeatureItem] = Field(..., min_length=1, description="List of feature samples to classify")


# Pydantic Response Models
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Classification outcome: 'phishing' or 'legitimate'")
    class_id: int = Field(..., description="Binary class ID: 0 (phishing) or 1 (legitimate)")
    model_score: Optional[float] = Field(None, description="Estimated probability of legitimate class (0.0 to 1.0)")


class BatchPredictionResponse(BaseModel):
    total_samples: int = Field(..., description="Total number of evaluated samples")
    predictions: List[PredictionResponse] = Field(..., description="List of prediction outputs")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health state: 'healthy' or 'degraded'")
    model_loaded: bool = Field(..., description="Whether the NetworkModel artifact is loaded in memory")
    version: str = Field(..., description="API version")
    supported_features_count: int = Field(..., description="Number of expected engineered features (30)")


@app.on_event("startup")
def startup_event():
    """Attempt to load model artifact on application startup if available."""
    try:
        pipeline.load_model()
        logging.info("Model loaded successfully on API startup.")
    except Exception as e:
        logging.warning(f"Model artifact could not be preloaded on startup: {e}")


@app.get("/", tags=["Info"])
def root():
    return {
        "name": "Network Security - Phishing Detection API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health",
        "supported_features": EXPECTED_FEATURES,
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Returns API health status and reports whether the machine learning artifact is operational.
    """
    model_ready = pipeline.is_model_loaded()
    if not model_ready:
        try:
            pipeline.load_model()
            model_ready = pipeline.is_model_loaded()
        except Exception:
            model_ready = False

    return HealthResponse(
        status="healthy" if model_ready else "degraded",
        model_loaded=model_ready,
        version="1.0.0",
        supported_features_count=len(EXPECTED_FEATURES),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict_single(item: PhishingFeatureItem):
    """
    Classifies a single website feature vector as 'phishing' (0) or 'legitimate' (1).
    """
    try:
        sample_dict = item.model_dump()
        results = pipeline.predict_with_details(sample_dict)
        if not results:
            raise HTTPException(status_code=500, detail="Inference returned empty results.")
        return PredictionResponse(**results[0])
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifact is not available. Please ensure model training has been completed.",
        )
    except (ValueError, KeyError) as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        err_msg = str(e)
        if "not found" in err_msg.lower() or "filenotfound" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model artifact is not available. Please ensure model training has been completed.",
            )
        if "missing required" in err_msg.lower() or "valueerror" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input validation error: missing required features.")
        logging.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal inference failure while processing features.",
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Inference"])
def predict_batch(request: BatchPredictionRequest):
    """
    Classifies multiple website feature vectors in a single batch request.
    """
    try:
        samples_list = [item.model_dump() for item in request.samples]
        results = pipeline.predict_with_details(samples_list)
        formatted_preds = [PredictionResponse(**r) for r in results]
        return BatchPredictionResponse(
            total_samples=len(formatted_preds),
            predictions=formatted_preds,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifact is not available. Please ensure model training has been completed.",
        )
    except (ValueError, KeyError) as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        err_msg = str(e)
        if "not found" in err_msg.lower() or "filenotfound" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model artifact is not available. Please ensure model training has been completed.",
            )
        if "missing required" in err_msg.lower() or "valueerror" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Input validation error: missing required features.")
        logging.error(f"Batch prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal inference failure while processing batch features.",
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app:app", host=host, port=port, reload=False)
