import os
import json
import boto3
from sentence_transformers import SentenceTransformer

BUCKET = "resume-analyzer-group13"
PROCESSED_PREFIX = "processed-texts/"
EMBEDDINGS_PREFIX = "resume-embeddings/"

TMP_DIR = os.path.join("backend", "tmp")
os.makedirs(TMP_DIR, exist_ok=True)

s3 = boto3.client("s3")
model = SentenceTransformer("all-MiniLM-L6-v2")


# ------------------------------
# CREATE EMBEDDINGS FOR RESUMES
# ------------------------------
def generate_resume_embeddings_once():
    objs = s3.list_objects_v2(Bucket=BUCKET, Prefix=PROCESSED_PREFIX)

    if "Contents" not in objs:
        print("No processed resumes found.")
        return

    for obj in objs["Contents"]:
        key = obj["Key"]
        if not key.endswith(".txt"):
            continue

        emb_key = key.replace(PROCESSED_PREFIX, EMBEDDINGS_PREFIX).replace(".txt", ".json")

        try:
            s3.head_object(Bucket=BUCKET, Key=emb_key)
            print(f"Skipping existing embedding: {emb_key}")
            continue
        except:
            pass

        local_txt = os.path.join(TMP_DIR, os.path.basename(key))
        s3.download_file(BUCKET, key, local_txt)

        with open(local_txt, "r", encoding="utf-8") as f:
            text = f.read()

        embedding = model.encode(text).tolist()

        local_emb = local_txt.replace(".txt", ".json")
        with open(local_emb, "w") as f:
            json.dump(embedding, f)

        s3.upload_file(local_emb, BUCKET, emb_key)
        print("Uploaded:", emb_key)


# ------------------------------
# JOB & RESUME EMBEDDINGS
# ------------------------------
def embed_job_description(text: str):
    return model.encode(text).tolist()


def embed_resume_text(text: str):
    return model.encode(text).tolist()


def get_embeddings_model():
    return model
