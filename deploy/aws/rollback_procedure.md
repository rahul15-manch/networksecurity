# PhishGuard AWS Rollback and Disaster Recovery Procedure

This document provides clear, deterministic steps to roll back frontend and backend deployments in case of an incident, regression, or service failure.

---

## 1. Backend Service Rollback (EC2)

If a new commit or dependency update introduces errors or regressions on the backend:

### Step 1: Connect to the EC2 Instance
Connect via AWS Systems Manager Session Manager (no open SSH port needed):
```bash
aws ssm start-session --target <instance-id> --region ap-south-1
```
Or via SSH (if bastion / keypair is configured):
```bash
ssh -i /path/to/key.pem ubuntu@<backend-ec2-ip>
```

### Step 2: Switch to Application User and Revert Git Commit
```bash
cd /home/ubuntu/networksecurity

# View git history to find last verified commit (e.g. bdcfc3e)
git log -n 5 --oneline

# Checkout the previous stable commit
git checkout <previous-commit-hash>
```

### Step 3: Re-install / Verify Virtual Environment
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Step 4: Verify Model Artifact
Ensure `final_model/model.pkl` is verified and operational:
```bash
python -c "
from networksecurity.pipeline.prediction_pipeline import PredictionPipeline
p = PredictionPipeline('final_model/model.pkl')
p.load_model()
print('Model verified successfully.')
"
```

### Step 5: Restart Backend Service and Verify Health
```bash
sudo systemctl restart phishguard-backend
sudo systemctl status phishguard-backend

# Test local health probe
curl -I http://127.0.0.1:8000/health
```

---

## 2. Frontend Rollback (S3 & CloudFront)

If the deployed frontend bundle produces client errors or breaks API compatibility:

### Option A: Fast Re-deploy from Local Stable Build
On your administrative machine:
```bash
cd /Users/rahulmanchanda/networksecurity

# Ensure you are on the verified stable git commit
git checkout bdcfc3e

# Build and sync the stable bundle
./deploy/aws/deploy_frontend.sh <s3-bucket-name> <cloudfront-distribution-id> "https://api.yourdomain.com"
```

### Option B: S3 Versioning Rollback (AWS Console or CLI)
Because S3 versioning is enabled in CloudFormation:
```bash
# List previous versions of index.html
aws s3api list-object-versions --bucket <s3-bucket-name> --prefix index.html

# Restore the previous stable version of index.html
aws s3api copy-object \
    --bucket <s3-bucket-name> \
    --copy-source <s3-bucket-name>/index.html?versionId=<previous-version-id> \
    --key index.html

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
    --distribution-id <cloudfront-distribution-id> \
    --paths "/*"
```

---

## 3. Emergency Maintenance Mode

If an ongoing security investigation requires immediately pausing public submissions:

### Fast Backend Cutoff via Nginx
On the EC2 instance, return 503 Service Unavailable:
```bash
sudo tee /etc/nginx/conf.d/maintenance.conf << 'EOF'
server {
    listen 80;
    listen 443;
    location / {
        return 503 "PhishGuard is temporarily offline for scheduled security maintenance.";
    }
}
EOF

sudo systemctl reload nginx
```

### Restore Normal Operations
```bash
sudo rm -f /etc/nginx/conf.d/maintenance.conf
sudo systemctl reload nginx
```
