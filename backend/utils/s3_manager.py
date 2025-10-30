from config import S3_BUCKET, get_s3_client

def upload_file_to_s3(file_path, object_name):
    s3 = get_s3_client()
    s3.upload_file(file_path, S3_BUCKET, object_name)
    return f"s3://{S3_BUCKET}/{object_name}"

