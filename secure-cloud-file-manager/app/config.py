import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
KMS_KEY_ARN = os.getenv("KMS_KEY_ARN")

if not S3_BUCKET_NAME:
    raise RuntimeError("S3_BUCKET_NAME is missing from .env")

if not KMS_KEY_ARN:
    raise RuntimeError("KMS_KEY_ARN is missing from .env")
