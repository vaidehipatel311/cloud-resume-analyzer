from .config import S3_BUCKET, AWS_REGION
import boto3
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3', region_name=AWS_REGION)

def upload_file_to_s3(file_path, s3_key):
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"Uploaded: {file_path} : s3://{S3_BUCKET}/{s3_key}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except NoCredentialsError:
        print("AWS credentials not found.")
