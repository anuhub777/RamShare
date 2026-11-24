# RAMShare AWS Deployment Guide

This guide describes how to deploy the RAMShare Control Plane infrastructure to Amazon Web Services using AWS SAM (Serverless Application Model).

---

## 1. Prerequisites
1. **AWS CLI** configured with administrator credentials (`aws configure`).
2. **AWS SAM CLI** installed (`sam --version`).
3. **Docker** installed for building containerized Lambda layers.

---

## 2. Infrastructure Architecture
Deploying `infrastructure/template.yaml` provisions:
- **Amazon API Gateway**: REST API with CORS and Cognito Authorizer.
- **AWS Lambda**: FastAPI API routing powered by Mangum.
- **Amazon Cognito User Pool**: Secure user directory and token issuer.
- **4 Amazon DynamoDB Tables**:
  - `ramshare-users-{stage}`
  - `ramshare-providers-{stage}`
  - `ramshare-jobs-{stage}`
  - `ramshare-credits-{stage}`
- **Amazon SQS**:
  - `ramshare-job-queue-{stage}`
  - `ramshare-job-dlq-{stage}` (Dead Letter Queue)
- **Amazon S3**:
  - `ramshare-storage-{stage}-{account-id}`

---

## 3. Build & Deploy Commands

1. Validate the SAM template:
   ```bash
   cd infrastructure
   sam validate
   ```

2. Build the application package:
   ```bash
   sam build
   ```

3. Deploy using guided deployment (first time):
   ```bash
   sam deploy --guided
   ```
   Provide the following parameters:
   - **Stack Name**: `ramshare-control-plane`
   - **AWS Region**: `us-east-1`
   - **Stage**: `dev`
   - Confirm changes and allow SAM CLI to create IAM roles.

---

## 4. Post-Deployment Configuration
After deployment completes, note the Stack Outputs printed by SAM:
- `ApiEndpoint`
- `CognitoUserPoolId`
- `CognitoClientId`
- `StorageBucket`
- `JobQueueUrl`

Update your production `.env` or frontend environment:
```ini
VITE_API_URL=https://{api-id}.execute-api.us-east-1.amazonaws.com/dev
```
