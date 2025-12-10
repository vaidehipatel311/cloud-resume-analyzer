import boto3
import os
import tempfile
from pdfminer.high_level import extract_text

BUCKET = "resume-analyzer-group13"
RAW_PREFIX = "resumes/"
PROCESSED_PREFIX = "processed-texts/"

s3 = boto3.client("s3")

# Use OS temp directory (Windows/Linux/Mac/AWS Lambda)
TMP_DIR = tempfile.gettempdir()

def extract_text_from_pdf(pdf_path):
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def process_all_resumes():
    print("Fetching resume list from S3...")

    objects = s3.list_objects_v2(Bucket=BUCKET, Prefix=RAW_PREFIX)

    if "Contents" not in objects:
        print("❌ No files found in resumes/ folder.")
        return

    for obj in objects["Contents"]:
        key = obj["Key"]

        # Skip folder markers
        if key.endswith("/"):
            continue

        # Only process PDF files
        if not key.lower().endswith(".pdf"):
            continue

        file_name = key.replace(RAW_PREFIX, "")

        # Proper temp paths
        local_pdf = os.path.join(TMP_DIR, file_name)
        local_text = os.path.join(TMP_DIR, file_name.replace(".pdf", ".txt"))

        s3_output_key = f"{PROCESSED_PREFIX}{file_name.replace('.pdf', '.txt')}"

        print(f"\n📥 Downloading: {file_name}")
        s3.download_file(BUCKET, key, local_pdf)

        print("📝 Extracting text...")
        extracted = extract_text_from_pdf(local_pdf)

        print("💾 Saving locally...")
        with open(local_text, "w", encoding="utf-8") as f:
            f.write(extracted)

        print(f"⬆️ Uploading processed file to {s3_output_key}")
        s3.upload_file(local_text, BUCKET, s3_output_key)

    print("\n✅ ALL RESUMES PROCESSED SUCCESSFULLY!")

if __name__ == "__main__":
    process_all_resumes()
