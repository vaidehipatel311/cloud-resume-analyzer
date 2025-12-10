import boto3
import json
import numpy as np
import os

# ------------------------
# Config
# ------------------------
BUCKET = "resume-analyzer-group13"
EMB_FOLDER = "resume-embeddings/"
TMP_DIR = "backend/tmp/"
SIMILARITY_THRESHOLD = 0.6  # only return matches above this

s3 = boto3.client("s3")

# Ensure temporary directory exists
os.makedirs(TMP_DIR, exist_ok=True)


# ------------------------
# Load embeddings from S3
# ------------------------
def load_all_embeddings_from_s3():
    """
    Load all embeddings from S3.
    Assumes each JSON is a plain array of numbers.
    Returns a dict: {resume_id: numpy_array_embedding}
    """
    embeddings = {}

    # List all files in the embeddings folder
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=EMB_FOLDER)
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".json"):
            resume_id = key.split("/")[-1].replace(".json", "")
            tmp_file = os.path.join(TMP_DIR, f"{resume_id}.json")

            # Download from S3
            s3.download_file(BUCKET, key, tmp_file)

            # Load embedding
            with open(tmp_file, "r", encoding="utf-8") as f:
                embedding_vector = json.load(f)
                embeddings[resume_id] = np.array(embedding_vector)

    return embeddings

ALL_EMBEDDINGS = load_all_embeddings_from_s3()

# ------------------------
# Cosine similarity
# ------------------------
def cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two numpy vectors
    """
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


# ------------------------
# Match similar resumes
# ------------------------
def match_similar_resumes(candidate_embedding, top_k=5):
    """
    Find top-k resumes most similar to candidate_embedding.

    candidate_embedding: list or numpy array
    Returns list of dicts: [{"resume_id": ..., "similarity": ...}, ...]
    """
    all_embeddings = load_all_embeddings_from_s3()
    candidate_vec = np.array(candidate_embedding)
    similarities = []

    for resume_id, emb_vec in all_embeddings.items():
        sim = cosine_similarity(candidate_vec, emb_vec)
        if sim >= SIMILARITY_THRESHOLD:
            similarities.append({"resume_id": resume_id, "similarity": sim})

    # Sort by similarity descending
    similarities.sort(key=lambda x: x["similarity"], reverse=True)

    # Return top_k
    return similarities[:top_k]
