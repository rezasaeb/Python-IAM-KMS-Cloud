import boto3

from app.config import AWS_REGION, S3_BUCKET_NAME, KMS_KEY_ARN

s3 = boto3.client("s3", region_name=AWS_REGION)

def upload_file(file_obj, object_key: str, content_type: str | None = None):
    extra_args = {
        "ServerSideEncryption": "aws:kms",
        "SSEKMSKeyId": KMS_KEY_ARN,
        "BucketKeyEnabled": True,
    }

    if content_type:
        extra_args["ContentType"] = content_type

    s3.upload_fileobj(
        file_obj,
        S3_BUCKET_NAME,
        object_key,
        ExtraArgs=extra_args,
    )

def list_files():
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)

    return [
        {
            "key": item["Key"],
            "size": item["Size"],
            "last_modified": item["LastModified"].isoformat(),
        }
        for item in response.get("Contents", [])
    ]

def download_file(object_key: str):
    return s3.get_object(
        Bucket=S3_BUCKET_NAME,
        Key=object_key,
    )

def delete_file(object_key: str):
    s3.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=object_key,
    )

def health_check():
    s3.head_bucket(Bucket=S3_BUCKET_NAME)
    return True
