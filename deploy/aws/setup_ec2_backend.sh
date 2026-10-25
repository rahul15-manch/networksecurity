#!/usr/bin/env bash
# ==============================================================================
# PhishGuard EC2 Backend Automated Provisioning Script
# Target OS: Ubuntu 22.04 / 24.04 LTS (AWS ap-south-1)
# Idempotent execution: Safe to run multiple times.
# ==============================================================================
set -euo pipefail

echo "=================================================="
echo "Starting PhishGuard EC2 Backend Provisioning"
echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=================================================="

# Ensure script is run with sudo or as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root or with sudo." >&2
    exit 1
fi

APP_DIR="/home/ubuntu/networksecurity"
APP_USER="ubuntu"
VENV_DIR="${APP_DIR}/venv"
LOG_DIR="/var/log/phishguard"

echo "[1/7] Updating system packages and installing prerequisites..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    git \
    curl \
    certbot \
    python3-certbot-nginx \
    libssl-dev

echo "[2/7] Preparing application directory and permissions..."
if [ ! -d "${APP_DIR}" ]; then
    echo "ERROR: Application repository not found at ${APP_DIR}." >&2
    echo "Please clone the repository into ${APP_DIR} before running this script." >&2
    exit 1
fi

chown -R ${APP_USER}:${APP_USER} "${APP_DIR}"

# Create dedicated log directory
mkdir -p "${LOG_DIR}"
chown -R ${APP_USER}:${APP_USER} "${LOG_DIR}"
chmod 750 "${LOG_DIR}"

echo "[3/7] Setting up Python virtual environment and dependencies..."
if [ ! -d "${VENV_DIR}" ]; then
    sudo -u ${APP_USER} python3 -m venv "${VENV_DIR}"
fi

sudo -u ${APP_USER} "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
sudo -u ${APP_USER} "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"
sudo -u ${APP_USER} "${VENV_DIR}/bin/pip" install gunicorn
sudo -u ${APP_USER} "${VENV_DIR}/bin/pip" install -e "${APP_DIR}"

echo "[4/7] Validating machine learning model artifacts..."
if [ ! -f "${APP_DIR}/final_model/model.pkl" ]; then
    echo "ERROR: Model artifact final_model/model.pkl not found!" >&2
    echo "Ensure final_model/model.pkl exists in the project root." >&2
    exit 1
fi

# Smoke-test loading model in python
sudo -u ${APP_USER} PYTHONPATH="${APP_DIR}" "${VENV_DIR}/bin/python" -c "
from networksecurity.pipeline.prediction_pipeline import PredictionPipeline
p = PredictionPipeline('${APP_DIR}/final_model/model.pkl')
p.load_model()
print('SUCCESS: Verified NetworkModel artifact loads cleanly.')
"

echo "[5/7] Installing and starting systemd service..."
cp "${APP_DIR}/deploy/aws/phishguard-backend.service" /etc/systemd/system/phishguard-backend.service
systemctl daemon-reload
systemctl enable phishguard-backend.service
systemctl restart phishguard-backend.service

echo "[6/7] Configuring Nginx reverse proxy..."
cp "${APP_DIR}/deploy/aws/nginx_phishguard.conf" /etc/nginx/sites-available/phishguard
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
fi
ln -sf /etc/nginx/sites-available/phishguard /etc/nginx/sites-enabled/phishguard

nginx -t
systemctl reload nginx

echo "[7/7] Probing local health check endpoint..."
sleep 3
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health || echo "FAILED")

if [ "${HEALTH_STATUS}" -eq 200 ]; then
    echo "=================================================="
    echo "PROVISIONING COMPLETE: PhishGuard Backend is Healthy (HTTP 200)!"
    echo "Backend listening on http://127.0.0.1:8000"
    echo "Nginx reverse proxy active on ports 80/443"
    echo "=================================================="
else
    echo "WARNING: Local health check returned status code: ${HEALTH_STATUS}"
    echo "Inspect logs: journalctl -u phishguard-backend -n 50"
fi
