from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import boto3
import os

from pdf2image import convert_from_bytes
import pytesseract

from nlp.embeddings import embed_job_description
from nlp.similarity import match_similar_resumes

app = Flask(__name__)
CORS(app)

S3_BUCKET = "resume-analyzer-group13"
s3 = boto3.client("s3")


@app.route("/")
def home():
    return {"message": "Backend running."}


# ------------------------------
# UPLOAD JOB DESCRIPTION + MATCH
# ------------------------------
@app.post("/upload-jobdesc")
def upload_jobdesc():
    data = request.get_json()
    text = data.get("job_description")

    if not text:
        return jsonify({"error": "job_description missing"}), 400

    # Save job description in S3
    key = f"job_descriptions/job_{uuid.uuid4()}.txt"

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=text.encode("utf-8")
        )
    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"error": str(e)}), 500

    # Generate embedding
    job_emb = embed_job_description(text)

    # Match resumes
    matches = match_similar_resumes(job_emb, top_k=10)

    return {
        "message": "Job description uploaded",
        "s3_key": key,
        "matches": matches
    }


# ------------------------------
# LIST RESUMES
# ------------------------------
@app.get("/resumes")
def list_resumes():
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="resumes/")
    files = [obj["Key"].split("/")[-1] for obj in response.get("Contents", []) if obj["Key"].endswith(".pdf")]
    return jsonify({"resumes": files})


# ------------------------------
# PROCESS PDF -> TEXT -> S3
# ------------------------------
@app.post("/new-file")
def process_file():
    data = request.get_json()
    bucket = data["bucket"]
    key = data["key"]

    local_pdf = os.path.basename(key)
    s3.download_file(bucket, key, local_pdf)

    pages = convert_from_bytes(open(local_pdf, "rb").read())
    text = "\n".join(pytesseract.image_to_string(p) for p in pages)

    output_key = f"processed-texts/{os.path.splitext(local_pdf)[0]}.txt"

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=text.encode("utf-8")
    )

    return {"message": "processed", "key": output_key}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
