from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.config import get_s3_client, S3_BUCKET
import uuid
from utils.config import get_dynamodb_resource
import boto3, os, pytesseract
from pdf2image import convert_from_bytes
from nlp.similarity import load_all_embeddings_from_s3
from nlp.embeddings import embed_job_description

app = Flask(__name__)
s3 = boto3.client('s3')
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
    print(data);
    job_text = data.get('job', '')
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



@app.route("/new-file", methods=["POST"])
def process_file():
    data = request.get_json()
    bucket = data["bucket"]
    key = data["key"]
    
    # Download file from S3
    local_pdf = os.path.basename(key)
    s3.download_file(bucket, key, local_pdf)
    
    # Convert and OCR
    pages = convert_from_bytes(open(local_pdf, 'rb').read())
    text = "\n".join(pytesseract.image_to_string(p) for p in pages)
    
    # Upload result to processed-texts/
    output_key = f"processed-texts/{os.path.splitext(os.path.basename(key))[0]}.txt"
    s3.put_object(Bucket=bucket, Key=output_key, Body=text.encode("utf-8"))

    print(f"Extracted and uploaded text for {key}")
    return {"message": "processed"}

# generate_resume_embeddings_once()

# all_embeddings = load_all_embeddings_from_s3()


@app.post("/upload-jobdesc")
def upload_jobdesc():
    data = request.get_json()
    text = data.get("job_description")
    
    if not text:
        return jsonify({"error": "No job description provided"}), 400

    # Generate embedding for the job description
    job_embedding = embed_job_description(text)

    # Match with resumes in S3
    from nlp.similarity import match_similar_resumes
    matches = match_similar_resumes(job_embedding, top_k=10)

    if not matches:
        return jsonify({"matches": [], "message": "No resumes matched this job description"})

    return jsonify({"matches": matches})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
