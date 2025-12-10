import os
import json
import boto3
from sentence_transformers import SentenceTransformer

# S3 bucket + prefixes
BUCKET = "resume-analyzer-group13"
PROCESSED_PREFIX = "processed-texts/"
EMBEDDINGS_PREFIX = "resume-embeddings/"

# Windows-safe temporary directory
TMP_DIR = os.path.join("backend", "tmp")
os.makedirs(TMP_DIR, exist_ok=True)

# S3 + model
s3 = boto3.client("s3")
model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------------------------------
# GENERATE EMBEDDINGS FOR ALL RESUMES (RUN ONLY ONCE)
# --------------------------------------------------------
def generate_resume_embeddings_once():
    print("Generating resume embeddings...")

    # list processed text files in S3
    objs = s3.list_objects_v2(Bucket=BUCKET, Prefix=PROCESSED_PREFIX)

    if "Contents" not in objs:
        print("No processed resumes found in S3")
        return

    for obj in objs["Contents"]:
        key = obj["Key"]

        # skip folders
        if not key.endswith(".txt"):
            continue

        # name for final embedding JSON in S3
        emb_key = key.replace(PROCESSED_PREFIX, EMBEDDINGS_PREFIX).replace(".txt", ".json")

        # skip if embedding already exists
        try:
            s3.head_object(Bucket=BUCKET, Key=emb_key)
            print(f"Skipping, embedding already exists: {emb_key}")
            continue
        except:
            pass  # object does not exist

        # download text temporarily
        filename = os.path.basename(key)
        local_txt = os.path.join(TMP_DIR, filename)

        s3.download_file(BUCKET, key, local_txt)

        # read text
        with open(local_txt, "r", encoding="utf-8") as f:
            text = f.read()

        # generate embedding
        embedding = model.encode(text).tolist()

        # save embedding to local temp JSON
        local_json = os.path.join(TMP_DIR, filename.replace(".txt", ".json"))
        with open(local_json, "w") as f:
            json.dump(embedding, f)

        # upload to S3
        s3.upload_file(local_json, BUCKET, emb_key)
        print(f"Uploaded embedding to S3: {emb_key}")

    print("Resume embedding generation complete.")


# --------------------------------------------------------
# INDIVIDUAL EMBEDDING FUNCTIONS (USED BY BACKEND API)
# --------------------------------------------------------
def embed_job_description(text: str):
    """Generate embedding for job description."""
    embedding = model.encode(text)
    return embedding.tolist()


def embed_resume_text(text: str):
    """Generate embedding for raw resume text."""
    embedding = model.encode(text)
    return embedding.tolist()


def get_embeddings_model():
    """Return embedding model instance."""
    return model

def match_similar_resumes(job_embedding):
    """
    Compare the job description embedding with all resume embeddings stored in S3
    and return similarity scores.
    """

    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    results = []

    # list all resume embedding files from S3
    objs = s3.list_objects_v2(Bucket=BUCKET, Prefix=EMBEDDINGS_PREFIX)

    if "Contents" not in objs:
        print("No resume embeddings found in S3.")
        return []

    for obj in objs["Contents"]:
        key = obj["Key"]
        if not key.endswith(".json"):
            continue

        # download the embedding JSON
        filename = os.path.basename(key)
        local_json = os.path.join(TMP_DIR, filename)
        s3.download_file(BUCKET, key, local_json)

        # load resume embedding
        with open(local_json, "r") as f:
            resume_emb = json.load(f)

        # compute similarity
        sim = cosine_similarity(
            [job_embedding],
            [resume_emb]
        )[0][0]

        results.append({
            "resume": filename.replace(".json", ""),
            "similarity": float(sim)
        })

    # sort by highest similarity first
    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results
