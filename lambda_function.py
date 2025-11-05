import boto3
import textract

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    file_path = f"/tmp/{key}"
    s3.download_file(bucket, key, file_path)

    text = textract.process(file_path)
    return {"statusCode": 200, "body": text.decode("utf-8")}
