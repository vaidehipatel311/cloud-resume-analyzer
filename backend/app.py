from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.config import get_s3_client, S3_BUCKET
import uuid
from utils.upload_dataset import upload_dataset_to_s3
from utils.config import get_dynamodb_resource

app = Flask(__name__)
CORS(app)

# Step 1: Ensure dataset is in S3
print("Checking and uploading dataset if needed...")
# upload_dataset_to_s3()
print("Dataset ready in S3.")

# Step 2: Continue with your API logic
dynamodb = get_dynamodb_resource()

@app.route("/")
def home():
    return {"message": "Flask server running, dataset uploaded."}

@app.route('/upload-job', methods=['POST'])
def upload_job_description():
    data = request.get_json()
    job_text = data.get('job_description', '')
    if not job_text:
        return jsonify({'error': 'Job description required'}), 400

    s3 = get_s3_client()
    key = f"job_descriptions/job_{uuid.uuid4()}.txt"
    s3.put_object(Body=job_text.encode('utf-8'), Bucket=S3_BUCKET, Key=key)

    return jsonify({
        'message': 'Job description uploaded successfully',
        's3_key': key
    }), 200


@app.route("/resumes", methods=["GET"])
def list_resumes():
    s3=get_s3_client();
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="resumes/")
    files = [obj["Key"].split("/")[-1] for obj in response.get("Contents", []) if obj["Key"].endswith(".pdf")]
    return jsonify({"resumes": files})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
