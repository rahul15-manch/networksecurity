# PhishGuard AWS Production Deployment Guide

This guide details the complete, production-grade deployment of the **PhishGuard** phishing detection platform on Amazon Web Services (AWS) in the **`ap-south-1` (Mumbai)** region.

---

## 1. Architecture Overview

```
                                  +-----------------------+
                                  |   Web Browser User    |
                                  +-----------+-----------+
                                              |
                          HTTPS (Route 53 / CloudFront Domain)
                                              |
                   +--------------------------v--------------------------+
                   |                 Amazon CloudFront                   |
                   |               CDN & Edge Termination                |
                   +--------------+-----------------------+--------------+
                                  |                       |
               Default Cache ('/*')                       | Cache Behavior ('/api/*')
               Origin: S3 Bucket (OAC)                    | Origin: EC2 Backend
                                  |                       |
                   +--------------v--------------+        |
                   |       Amazon S3 (Private)   |        |
                   |  React / Vite Static Assets |        |
                   +-----------------------------+        |
                                                          |
                                           HTTPS (Proxy to Port 80/443)
                                                          |
                                  +-----------------------v--------------+
                                  |       Amazon EC2 (t4g/t3.small)      |
                                  |        ap-south-1 (Mumbai)           |
                                  |                                      |
                                  |   +------------------------------+   |
                                  |   |   Nginx Reverse Proxy        |   |
                                  |   |   - TLS 1.3 / Security Headers|   |
                                  |   |   - Rate Limiting (10 req/s) |   |
                                  |   +--------------+---------------+   |
                                  |                  |                   |
                                  |           HTTP 127.0.0.1:8000        |
                                  |                  |                   |
                                  |   +--------------v---------------+   |
                                  |   |   systemd: phishguard-backend|   |
                                  |   |   Gunicorn (4 Uvicorn Workers)|  |
                                  |   |   FastAPI Application        |   |
                                  |   |   - Model: final_model/      |   |
                                  |   |   - Preprocessor Pipeline    |   |
                                  |   |   - SSRF Protection Layer    |   |
                                  |   +------------------------------+   |
                                  +--------------------------------------+
```

### Key Architectural Characteristics
- **Zero Public S3 Access:** The S3 bucket blocks 100% of public ACLs and bucket policies. Assets are accessible strictly through CloudFront via **Origin Access Control (OAC)**.
- **SSRF Hardened:** The backend validates every submitted URL and all redirect hops against RFC 1918 private IPs, loopback, link-local, and AWS IMDS metadata (`169.254.169.254`).
- **No Inbound SSH Needed:** The EC2 instance attaches the `AmazonSSMManagedInstanceCore` IAM policy, allowing administrative access exclusively via AWS Systems Manager Session Manager.
- **Model Isolation:** The trained 256-tree Random Forest artifact and preprocessing pipeline run directly inside the secured EC2 runtime.

---

## 2. Resource Inventory and Estimated Ongoing Costs

| AWS Resource | Configuration Tier | Purpose | Monthly Cost Estimate (ap-south-1) |
| :--- | :--- | :--- | :--- |
| **Amazon EC2** | `t4g.small` (2 vCPU, 2GB RAM, Graviton) or `t3.small` | Runs Gunicorn + Uvicorn + Nginx + Model inference | ~$12.00 – $15.00 / month (Eligible for Savings Plans / Free Tier for t2/t3.micro) |
| **Amazon EBS** | 20 GB `gp3` SSD | Root operating system volume and model storage | ~$1.60 / month |
| **Amazon S3** | Standard Storage (< 10 MB) | Static Vite frontend bundle | < $0.05 / month |
| **Amazon CloudFront** | Price Class 200 or All | Global HTTPS content delivery and TLS termination | Free Tier (first 1 TB data transfer / month is free) |
| **AWS IAM / SSM** | Default | Session Manager remote administration | Free |
| **Total Estimated Cost** | | | **~$14.00 – $17.00 / month** |

*Tip: To avoid unwanted charges during testing, stop the EC2 instance when not in use.*

---

## 3. Deployment Method A: Automated via CloudFormation & Scripts

### Step 1: Deploy Infrastructure with CloudFormation
From your local terminal with AWS credentials configured:
```bash
aws cloudformation create-stack \
    --stack-name phishguard-production \
    --template-body file://deploy/aws/cloudformation_template.yaml \
    --parameters ParameterKey=ProjectName,ParameterValue=phishguard ParameterKey=Environment,ParameterValue=production \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ap-south-1

# Wait for stack completion
aws cloudformation wait stack-create-complete \
    --stack-name phishguard-production \
    --region ap-south-1

# View outputs (Bucket name, CloudFront domain, Security Group, IAM profile)
aws cloudformation describe-stacks \
    --stack-name phishguard-production \
    --query "Stacks[0].Outputs" \
    --region ap-south-1
```

### Step 2: Launch and Configure the EC2 Backend Instance
1. Launch an Ubuntu 22.04 or 24.04 LTS instance (`t4g.small` or `t3.small`) in `ap-south-1` using the created `phishguard-backend-sg` security group and `phishguard-ec2-instance-profile`.
2. Connect to the instance via AWS SSM or SSH:
   ```bash
   aws ssm start-session --target <instance-id> --region ap-south-1
   ```
3. Clone the repository and run the provisioning script:
   ```bash
   sudo su - ubuntu
   git clone https://github.com/rahul15-manch/networksecurity.git /home/ubuntu/networksecurity
   cd /home/ubuntu/networksecurity
   git checkout fix/phase1-security-runTime

   # Run automated backend setup
   sudo ./deploy/aws/setup_ec2_backend.sh
   ```
4. Verify backend health check:
   ```bash
   curl http://127.0.0.1:8000/health
   # Expected: {"status":"healthy","model_loaded":true,"version":"1.0.0","supported_features_count":30}
   ```

### Step 3: Deploy Frontend to S3 and Invalidate CloudFront
From your local administrative terminal:
```bash
# Set your outputs from CloudFormation
S3_BUCKET="phishguard-frontend-<account-id>-ap-south-1"
DIST_ID="<cloudfront-distribution-id>"
API_URL="https://api.yourdomain.com" # or "https://<cloudfront-domain>/api"

./deploy/aws/deploy_frontend.sh "${S3_BUCKET}" "${DIST_ID}" "${API_URL}"
```

---

## 4. Deployment Method B: Step-by-Step AWS Management Console Guide

### Part 1: S3 Bucket Setup
1. Open the [Amazon S3 Console](https://s3.console.aws.amazon.com/).
2. Select Region: **Asia Pacific (Mumbai) ap-south-1**.
3. Click **Create bucket**.
   - Bucket name: `phishguard-frontend-<your-name>-ap-south-1`
   - Object Ownership: **ACLs disabled (recommended)**.
   - Block Public Access settings: **Keep "Block all public access" checked** (100% private).
   - Bucket Versioning: **Enable** (enables one-click rollbacks).
   - Encryption: **Server-side encryption with Amazon S3 managed keys (SSE-S3)**.
4. Click **Create bucket**.

### Part 2: CloudFront Distribution Setup
1. Open the [CloudFront Console](https://console.aws.amazon.com/cloudfront/).
2. Click **Create distribution**.
3. Under **Origin domain**, choose the S3 bucket created in Part 1.
4. Under **Origin access**, select **Origin access control settings (recommended)**:
   - Click **Create control setting**, name it `phishguard-oac`, keep `Sign requests` selected, and click **Create**.
5. Under **Default cache behavior**:
   - Viewer protocol policy: **Redirect HTTP to HTTPS**.
   - Allowed HTTP methods: **GET, HEAD, OPTIONS**.
   - Cache policy: **CachingOptimized**.
6. Under **Custom error response**:
   - Click **Add custom error response**:
     - HTTP error code: **403**
     - Customize error response: **Yes**
     - Response page path: `/index.html`
     - HTTP Response code: **200**
   - Click **Add custom error response**:
     - HTTP error code: **404**
     - Customize error response: **Yes**
     - Response page path: `/index.html`
     - HTTP Response code: **200**
7. Click **Create distribution**.
8. Once created, CloudFront will display a banner: *"The S3 bucket policy needs to be updated"*. Click **Copy policy**, go to your S3 bucket's **Permissions** tab, and paste it into the **Bucket policy** editor.

### Part 3: EC2 Backend Setup
1. Open the [EC2 Console](https://ap-south-1.console.aws.amazon.com/ec2/).
2. Click **Launch instances**:
   - Name: `phishguard-backend-prod`
   - OS Image: **Ubuntu Server 24.04 LTS (HVM)**
   - Instance type: `t4g.small` (64-bit Arm) or `t3.small` (64-bit x86)
   - Key pair: Select existing or choose *"Proceed without a key pair"* (using SSM Session Manager).
   - Network settings:
     - Allow HTTPS traffic from the internet (port 443).
     - Allow HTTP traffic from the internet (port 80).
     - Restrict SSH (port 22) to your IP only.
   - Advanced details:
     - IAM instance profile: Select role with `AmazonSSMManagedInstanceCore`.
3. Click **Launch instance**.
4. Once running, connect via **Session Manager** or SSH.
5. Execute the provisioning commands:
   ```bash
   sudo su - ubuntu
   git clone https://github.com/rahul15-manch/networksecurity.git /home/ubuntu/networksecurity
   cd /home/ubuntu/networksecurity
   git checkout fix/phase1-security-runTime
   sudo ./deploy/aws/setup_ec2_backend.sh
   ```

---

## 5. Security & SSRF Audit Verification

PhishGuard contains active SSRF protections tested and verified prior to deployment:

```bash
# 1. Verification that private IP ranges are rejected
curl -X POST http://127.0.0.1:8000/predict-url \
     -H "Content-Type: application/json" \
     -d '{"url":"http://169.254.169.254/latest/meta-data"}'
# Response: 400 Bad Request: "Security violation: Link-local / Cloud metadata address (169.254.169.254)"

# 2. Verification that localhost and internal domains are rejected
curl -X POST http://127.0.0.1:8000/predict-url \
     -H "Content-Type: application/json" \
     -d '{"url":"http://localhost:8000"}'
# Response: 400 Bad Request: "Security violation: Host 'localhost' references a local or internal domain name."

# 3. Verification of strict mode enforcement
curl -X POST http://127.0.0.1:8000/predict-url \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com","allow_heuristics":false}'
# Response: {"status":"unsupported_features","feature_coverage":"incomplete","prediction":null}
```

---

## 6. Verification and Smoke Testing Checklist

After completing deployment:

- [ ] **HTTPS Enforced:** Navigate to `http://<your-cloudfront-domain>` and verify it redirects to `https://`.
- [ ] **SPA Asset Loading:** Verify CSS styles, Lucide icons, and React UI render without JavaScript errors.
- [ ] **Health Endpoint:** Query `https://api.yourdomain.com/health` and verify HTTP 200 with `model_loaded: true`.
- [ ] **Strict Mode Check:** Submit a URL with default settings; verify response indicates incomplete analysis with guidance to enable heuristics.
- [ ] **Heuristic Mode Check:** Enable heuristics; verify response returns classification, probability breakdown, and explicit disclosure of observed vs estimated feature counts.
- [ ] **Suspicious URL Protection:** Submit `https://testsafebrowsing.appspot.com/s/phishing.html` with heuristics enabled; verify verdict displays **"Uncertain / Suspicious Risk Detected"** with amber badge and zero false safe signatures.
- [ ] **CORS Verification:** In browser dev tools, verify headers contain `Access-Control-Allow-Origin: <your-cloudfront-domain>`.
