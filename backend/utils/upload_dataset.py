# backend/utils/upload_dataset.py
import os
import boto3
from utils.s3_manager import upload_file_to_s3
from .config import S3_BUCKET

DATASET_DIR=r"C:\Vaidehi\3rd sem\CC\cloud-resume-analyzer\backend\dataset\resumes\data\data"

s3 = boto3.client("s3")

def get_existing_s3_files():
    """Fetch existing resume filenames from S3."""
    existing = set()
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="resumes/")
    for obj in response.get("Contents", []):
        existing.add(obj["Key"].split("/")[-1])
    return existing

def upload_dataset_to_s3():
    from utils.config import S3_BUCKET, get_s3_client
    s3 = get_s3_client()

    # Walk through subfolders
    local_files = []
    for root, dirs, files in os.walk(DATASET_DIR):
        for file in files:
            if file.lower().endswith(('.pdf', '.docx', '.txt')):
                local_files.append(os.path.join(root, file))

    print(f"Found {len(local_files)} local resumes.")

    # Get already uploaded files from S3
    existing = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="resumes/")
    existing_files = [obj['Key'] for obj in existing.get('Contents', [])] if 'Contents' in existing else []

    uploaded_count = 0
    for file_path in local_files:
        key = f"resumes/{os.path.basename(file_path)}"
        if key in existing_files:
            continue
        upload_file_to_s3(file_path, key)
        uploaded_count += 1

    print(f"Uploaded {uploaded_count} new resumes to S3.")
    print("Dataset ready in S3.")
