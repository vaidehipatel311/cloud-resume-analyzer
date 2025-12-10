import boto3
import os
import json
import numpy as np

BUCKET = "resume-analyzer-group13"
EMBEDDINGS_PREFIX = "resume-embeddings/"
TMP_DIR = "backend/tmp/"
SIMILARITY_THRESHOLD = 0.0  # KEEP ALL RESUMES

os.makedirs(TMP_DIR, exist_ok=True)
s3 = boto3.client("s3")


# ------------------------------
# LOAD ALL RESUME EMBEDDINGS
# ------------------------------
def load_all_embeddings_from_s3():
    embeddings = {}

    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=EMBEDDINGS_PREFIX)

    for obj in response.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".json"):
            continue

        resume_id = key.split("/")[-1].replace(".json", "")
        tmp_path = os.path.join(TMP_DIR, resume_id + ".json")

        s3.download_file(BUCKET, key, tmp_path)

        with open(tmp_path, "r") as f:
            vector = json.load(f)

        embeddings[resume_id] = np.array(vector)

    return embeddings


# ------------------------------
# COSINE SIMILARITY
# ------------------------------
def cosine_similarity(a, b):
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ------------------------------
# MATCH RESUMES
# ------------------------------
def match_similar_resumes(job_embedding, top_k=10):
    all_embs = load_all_embeddings_from_s3()

    job_vec = np.array(job_embedding)
    results = []

    for resume_id, emb in all_embs.items():
        sim = cosine_similarity(job_vec, emb)
        results.append({"resume": resume_id, "similarity": sim})

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]
