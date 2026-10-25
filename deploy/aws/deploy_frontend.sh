#!/usr/bin/env bash
# ==============================================================================
# PhishGuard Frontend Production Build and AWS S3/CloudFront Deployment Script
# Idempotent execution: Builds Vite bundle, syncs to S3, and invalidates CloudFront.
# ==============================================================================
set -euo pipefail

# Required Arguments or Environment Variables
S3_BUCKET="${1:-${S3_BUCKET:-}}"
CLOUDFRONT_DIST_ID="${2:-${CLOUDFRONT_DIST_ID:-}}"
API_BASE_URL="${3:-${VITE_API_BASE_URL:-/api}}"

if [ -z "${S3_BUCKET}" ]; then
    echo "Usage: $0 <s3-bucket-name> [cloudfront-distribution-id] [api-base-url]"
    echo "Or export S3_BUCKET and CLOUDFRONT_DIST_ID in your environment."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

echo "=================================================="
echo "Starting PhishGuard Frontend Deployment"
echo "Target S3 Bucket:       ${S3_BUCKET}"
echo "CloudFront Dist ID:     ${CLOUDFRONT_DIST_ID:-Not provided (skipping invalidation)}"
echo "Configured API Base:    ${API_BASE_URL}"
echo "=================================================="

cd "${FRONTEND_DIR}"

echo "[1/4] Installing frontend dependencies..."
npm ci

echo "[2/4] Running frontend test suite..."
npm test -- --run

echo "[3/4] Building production SPA bundle..."
VITE_API_BASE_URL="${API_BASE_URL}" npm run build

if [ ! -d "${FRONTEND_DIR}/dist" ]; then
    echo "ERROR: Build directory ${FRONTEND_DIR}/dist does not exist!" >&2
    exit 1
fi

echo "[4/4] Syncing static assets to Amazon S3 (private bucket with OAC)..."
# Upload assets with long cache-control (1 year immutable for hashed assets)
aws s3 sync "${FRONTEND_DIR}/dist/assets" "s3://${S3_BUCKET}/assets" \
    --delete \
    --cache-control "public, max-age=31536000, immutable"

# Upload index.html and root files with no-cache (to ensure instant updates)
aws s3 sync "${FRONTEND_DIR}/dist" "s3://${S3_BUCKET}" \
    --delete \
    --exclude "assets/*" \
    --cache-control "no-cache, no-store, must-revalidate"

echo "Frontend static files uploaded to s3://${S3_BUCKET}."

if [ -n "${CLOUDFRONT_DIST_ID}" ]; then
    echo "Creating CloudFront cache invalidation for distribution ${CLOUDFRONT_DIST_ID}..."
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "${CLOUDFRONT_DIST_ID}" \
        --paths "/*" \
        --query "Invalidation.Id" \
        --output text)
    echo "CloudFront Invalidation submitted: ${INVALIDATION_ID}"
fi

echo "=================================================="
echo "Frontend deployment completed successfully!"
echo "=================================================="
