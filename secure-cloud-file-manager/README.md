# Secure Cloud File Manager

A practical cloud-security portfolio project using:

- Python
- FastAPI
- AWS IAM
- Amazon S3
- AWS KMS
- Boto3
- GitHub
- Optional Docker

## Architecture

Client -> FastAPI -> IAM permissions -> S3 -> KMS encryption

Files are stored in Amazon S3 using server-side encryption with a customer-managed AWS KMS key (SSE-KMS).

## 1. Prerequisites

Install:

- Python 3.11+ (3.12 recommended)
- AWS CLI
- Git
- An AWS account

Verify:

```powershell
python --version
aws --version
git --version
```

## 2. Create the project

```powershell
git clone YOUR_REPOSITORY_URL
cd secure-cloud-file-manager
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. AWS setup

Choose one AWS Region and use it consistently. Example:

```text
us-east-1
```

### Create S3 bucket

The bucket name must be globally unique.

Example:

```text
secure-file-manager-123456789012
```

In AWS Console:

S3 -> Create bucket

Recommended settings:

- Block all public access: ON
- Object Ownership: Bucket owner enforced
- Versioning: ON (recommended)
- Region: same region as your KMS key

Do NOT make the bucket public.

### Create KMS key

AWS Console:

KMS -> Customer managed keys -> Create key

Select:

- Key type: Symmetric
- Key usage: Encrypt and decrypt
- Alias: alias/secure-file-manager

The KMS key and S3 bucket must be in the same AWS Region.

Copy the KMS key ARN. It looks like:

```text
arn:aws:kms:us-east-1:123456789012:key/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Create IAM policy

Open:

IAM -> Policies -> Create policy -> JSON

Paste `iam-policy.json`.

Replace:

```text
REPLACE_BUCKET_NAME
```

with your bucket name.

Replace:

```text
REPLACE_KMS_KEY_ARN
```

with your KMS key ARN.

Name the policy:

```text
SecureCloudFileManagerPolicy
```

### Create IAM user for local development

IAM -> Users -> Create user

Example name:

```text
secure-cloud-file-manager-dev
```

Attach:

```text
SecureCloudFileManagerPolicy
```

Create an access key for local development.

IMPORTANT:
Never commit the access key or secret key to GitHub.

### Configure AWS CLI

Run:

```powershell
aws configure
```

Enter:

```text
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: us-east-1
Default output format: json
```

Verify:

```powershell
aws sts get-caller-identity
```

If this works, your Python application can use the same AWS credential chain through Boto3.

## 4. Configure the application

Copy:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-real-bucket-name
KMS_KEY_ARN=your-real-kms-key-arn
```

Do NOT put AWS access keys in `.env`.

The `.env` file is ignored by Git.

## 5. Optional S3 encryption policy

After replacing the placeholders in `s3-bucket-policy.json`, apply it:

```powershell
aws s3api put-bucket-policy `
  --bucket YOUR_BUCKET_NAME `
  --policy file://s3-bucket-policy.json
```

This policy rejects object uploads that do not request SSE-KMS with your selected key.

## 6. Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 7. Test

### Health

```powershell
curl http://127.0.0.1:8000/health
```

### Upload

Use Swagger:

```text
http://127.0.0.1:8000/docs
```

Open:

```text
POST /files/upload
```

Click:

```text
Try it out
```

Choose a file and execute.

### List files

```text
GET /files
```

### Delete

```text
DELETE /files/{filename}
```

## 8. Verify encryption

AWS Console:

S3 -> your bucket -> uploaded object -> Properties

Look for server-side encryption.

It should show:

```text
AWS Key Management Service key (SSE-KMS)
```

You can also run:

```powershell
aws s3api head-object `
  --bucket YOUR_BUCKET_NAME `
  --key YOUR_FILE_NAME
```

Look for:

```text
ServerSideEncryption: aws:kms
SSEKMSKeyId: ...
```

## 9. Run tests

```powershell
pytest
```

## 10. Docker

Build:

```powershell
docker build -t secure-cloud-file-manager .
```

Run:

```powershell
docker run --rm -p 8000:8000 `
  -e AWS_REGION=us-east-1 `
  -e S3_BUCKET_NAME=YOUR_BUCKET_NAME `
  -e KMS_KEY_ARN=YOUR_KMS_KEY_ARN `
  secure-cloud-file-manager
```

For production, prefer an AWS IAM role instead of long-lived access keys.

## 11. GitHub

Initialize:

```powershell
git init
git add .
git status
git commit -m "Initial secure cloud file manager"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/secure-cloud-file-manager.git
git push -u origin main
```

Before pushing, make absolutely sure:

```text
.env
```

is ignored.

Check:

```powershell
git status
```

If `.env` appears, DO NOT push yet.

## Security concepts demonstrated

1. IAM controls what the application can do.
2. S3 stores the files.
3. KMS protects encryption keys.
4. S3 performs server-side encryption with KMS.
5. The IAM policy grants only the S3/KMS permissions required by this application.
6. The bucket is private.
7. Secrets are kept outside GitHub.

## Important

Never use the AWS root account access key for this application.

Never upload:

- AWS access keys
- AWS secret keys
- `.env`
- private credentials

If a credential is accidentally pushed to GitHub, rotate/revoke it immediately.
