# from flask import Flask, request, jsonify
# from utils.s3_manager import upload_file_to_s3

# app = Flask(__name__)

# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         return jsonify({"error": "No file provided"}), 400
    
#     file = request.files["file"]
#     filename = file.filename
#     local_path = f"/tmp/{filename}"  # save temporarily
#     file.save(local_path)
    
#     # 🧩 Here's where this line belongs:
#     s3_url = upload_file_to_s3(local_path, f"resumes/{filename}")
    
#     return jsonify({"message": "Upload successful", "s3_url": s3_url}), 200

# if __name__ == "__main__":
#     app.run(debug=True)

from utils.config import get_s3_client, S3_BUCKET
import os

def upload_file_to_s3(file_path, object_name):
    """Uploads a given file to the configured S3 bucket."""
    s3 = get_s3_client()
    s3.upload_file(file_path, S3_BUCKET, object_name)
    print(f"✅ Uploaded to s3://{S3_BUCKET}/{object_name}")


local_file_path = r"C:\Vaidehi\3rd sem\CC\VaidehiPatel_Resume.pdf"
object_name = f"resumes/{os.path.basename(local_file_path)}"

# Upload
upload_file_to_s3(local_file_path, object_name)

