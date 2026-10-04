from fastapi import FastAPI, File, HTTPException, UploadFile
from botocore.exceptions import ClientError

from app.aws import (
    delete_file,
    download_file,
    health_check,
    list_files,
    upload_file,
)

app = FastAPI(
    title="Secure Cloud File Manager",
    version="1.0.0",
    description="FastAPI + AWS IAM + S3 + KMS portfolio project",
)

@app.get("/")
def root():
    return {
        "message": "Secure Cloud File Manager API",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    try:
        health_check()
        return {"status": "ok", "aws_s3": "connected"}
    except ClientError as exc:
        raise HTTPException(status_code=503, detail="AWS connection failed") from exc

@app.post("/files/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    try:
        upload_file(
            file.file,
            file.filename,
            file.content_type,
        )

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "encrypted": True,
            "encryption": "SSE-KMS",
        }
    except ClientError as exc:
        raise HTTPException(status_code=500, detail="Upload failed") from exc

@app.get("/files")
def files():
    try:
        return {"files": list_files()}
    except ClientError as exc:
        raise HTTPException(status_code=500, detail="Could not list files") from exc

@app.get("/files/{filename}")
def download(filename: str):
    try:
        obj = download_file(filename)

        return {
            "filename": filename,
            "content_type": obj.get("ContentType"),
            "size": obj.get("ContentLength"),
            "message": "Object exists and can be decrypted by AWS KMS",
        }
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code in {"NoSuchKey", "404", "NoSuchBucket"}:
            raise HTTPException(status_code=404, detail="File not found") from exc
        raise HTTPException(status_code=500, detail="Download failed") from exc

@app.delete("/files/{filename}")
def delete(filename: str):
    try:
        delete_file(filename)
        return {"message": "File deleted", "filename": filename}
    except ClientError as exc:
        raise HTTPException(status_code=500, detail="Delete failed") from exc
