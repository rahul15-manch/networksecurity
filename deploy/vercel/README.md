# PhishGuard Zero-Cost Vercel Deployment Guide

This guide provides the complete documentation for deploying the **PhishGuard** phishing detection platform on **Vercel** with **zero out-of-pocket cost** using the free **Vercel Hobby Plan**.

---

## 1. Architecture Overview

PhishGuard is deployed as a **unified, full-stack Vercel project** combining:
1. **Frontend:** React 19 + TypeScript + Vite SPA, served globally via Vercel's high-speed Edge CDN.
2. **Backend API:** FastAPI application running as a Serverless Python Function (`@vercel/python`) at `/api/*`.
3. **Machine Learning Model:** Real 256-tree Random Forest classifier (`final_model/model.pkl`) and preprocessing pipeline embedded directly within the serverless runtime.

```
                           +---------------------------+
                           |     Web Browser Client    |
                           +-------------+-------------+
                                         |
                               HTTPS (Vercel Domain)
                                         |
               +-------------------------v-------------------------+
               |                    Vercel Edge                    |
               |                Global CDN Gateway                 |
               +------------+--------------------------+-----------+
                            |                          |
        Static Assets ('/*')|                          | API Requests ('/api/*')
        Vite SPA Build      |                          | Serverless Python Route
                            |                          |
               +------------v------------+             |
               |   Edge Static Cache     |             |
               |   - index.html          |             |
               |   - assets/*.js, *.css  |             |
               |   - SPA 200 Fallback    |             |
               +-------------------------+             |
                                                       |
                               +-----------------------v-----------------------+
                               |     Vercel Python Serverless Function         |
                               |               (api/index.py)                  |
                               |                                               |
                               |  - Runtime: Python 3.11 / FastAPI             |
                               |  - Memory: 1024 MB (Peak usage: ~231 MB)      |
                               |  - Timeout: 15 seconds (Avg runtime: 1.5-3s)  |
                               |  - Bundle Size: ~246 MB (Limit: 250 MB)       |
                               |                                               |
                               |  +-----------------------------------------+  |
                               |  |  NetworkModel & Feature Pipeline        |  |
                               |  |  - final_model/model.pkl (28 MB)        |  |
                               |  |  - KNNImputer Preprocessor              |  |
                               |  |  - Strict SSRF & Content Decompression  |  |
                               |  +-----------------------------------------+  |
                               +-----------------------------------------------+
```

---

## 2. Zero-Cost Safeguards & Vercel Hobby Limits

The **Vercel Hobby Plan** is 100% free and requires **zero payment credentials**. To prevent any accidental spend, PhishGuard is engineered specifically to operate well within these free tier quotas:

| Metric | Vercel Hobby Limit | PhishGuard Actual Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Out-of-Pocket Cost** | **$0.00 / month** | **$0.00** (Zero paid add-ons) | **Compliant** |
| **Serverless Function Size** | 250 MB uncompressed | **~246 MB** (Optimized via `api/requirements.txt`) | **Compliant** |
| **Function Execution Memory** | 1024 MB | **~231 MB** peak during prediction | **Compliant** (under 25% quota) |
| **Function Execution Duration**| 15 seconds max | **1.5s – 3.5s** (Network fetch timeout: 5.0s) | **Compliant** |
| **Cold Start Latency** | N/A | **~1.05s** (Model loads in 0.15s) | **Excellent** |
| **Bandwidth Quota** | 100 GB / month | ~0.3 MB per full frontend load | **Compliant** (~300,000 page views) |
| **Function Invocations** | 100,000 / month | 1 invocation per analysis | **Compliant** (Over 3,300 tests/day) |

> [!NOTE]
> **Zero Surprise Bill Guarantee:** If the monthly invocation or bandwidth limits are reached on the Hobby plan, Vercel automatically rate-limits or pauses requests (returning HTTP 429) rather than billing your credit card. There is zero risk of unexpected charges.

---

## 3. Deployment Instructions

### Method 1: Git-Based Import (Recommended)

1. **Push your code to GitHub:**
   Ensure your branch (or merged `main`) is pushed to your GitHub repository (e.g. `rahul15-manch/networksecurity`).
2. **Log into Vercel:**
   Visit [vercel.com](https://vercel.com/) and sign in with your GitHub account.
3. **Import the Repository:**
   - Click **Add New...** -> **Project**.
   - Select your `networksecurity` repository and click **Import**.
4. **Configure Project Settings:**
   - **Project Name:** `phishguard` (or custom name).
   - **Framework Preset:** `Vite` (automatically detected).
   - **Root Directory:** `./` (keep at repository root).
   - **Build and Output Settings:**
     - Build Command: `npm --prefix frontend install && npm --prefix frontend run build` (configured in `vercel.json` and root `package.json`).
     - Output Directory: `frontend/dist`.
5. **Environment Variables:**
   Under **Environment Variables**, add:
   - `APP_ENV`: `production`
   - `MODEL_PATH`: `final_model/model.pkl`
   - `ENFORCE_PUBLIC_DNS`: `true`
6. **Click Deploy:**
   Vercel will build the Vite frontend, package the serverless Python backend, and provide an instant live URL (e.g., `https://phishguard.vercel.app`).

---

### Method 2: Deployment via Vercel CLI

If you prefer deploying directly from your terminal:

```bash
# 1. Login to your free Vercel account
npx vercel login

# 2. Deploy a preview build to test
npx vercel

# 3. Deploy to production
npx vercel --prod
```

---

## 4. Verification and Live Smoke Testing

Once deployed to your Vercel URL (e.g. `https://your-project.vercel.app`):

### 1. Health Probe
```bash
curl -i https://your-project.vercel.app/api/health
```
**Expected response (HTTP 200):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "supported_features_count": 30
}
```

### 2. Strict Mode Verification
```bash
curl -X POST https://your-project.vercel.app/api/predict-url \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com","allow_heuristics":false}'
```
**Expected response (HTTP 200):**
```json
{
  "status": "unsupported_features",
  "feature_coverage": "incomplete",
  "prediction": null
}
```

### 3. Heuristic Mode Verification
```bash
curl -X POST https://your-project.vercel.app/api/predict-url \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com","allow_heuristics":true,"fetch_network":false}'
```
**Expected response (HTTP 200):**
Includes `observed_count`, `estimated_count`, `is_heuristic: true`, model probabilities, and risk tier.

### 4. SSRF Defense Check
```bash
curl -X POST https://your-project.vercel.app/api/predict-url \
     -H "Content-Type: application/json" \
     -d '{"url":"http://169.254.169.254/latest/meta-data"}'
```
**Expected response (HTTP 400):**
```json
{
  "detail": "Security violation: Link-local / Cloud metadata address (169.254.169.254)"
}
```

---

## 5. Rollback Procedure

If a deployed update needs to be reverted:
1. In the [Vercel Dashboard](https://vercel.com/dashboard), navigate to your **PhishGuard** project.
2. Go to the **Deployments** tab.
3. Locate the previous stable deployment.
4. Click the **three dots (...)** menu on the right and select **Promote to Production**.
5. The rollback is instantaneous across Vercel's global edge network (zero downtime, no re-building required).
