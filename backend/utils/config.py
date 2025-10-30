import boto3

AWS_REGION = "us-east-1"
S3_BUCKET = "resume-analyzer-bucket"

def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=AWS_REGION)
