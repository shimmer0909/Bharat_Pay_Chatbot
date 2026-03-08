# vector_db/qdrant_store.py

from models.embedding import generate_embedding
import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
import uuid
from tqdm import tqdm

# Connect to local Qdrant
client = QdrantClient(host="localhost", port=6333)

# Collection name
COLLECTION_NAME = "document_chunks"

# Create collection if it doesn't exist
existing_collections = [c.name for c in client.get_collections().collections]
if COLLECTION_NAME not in existing_collections:
    print(f"Creating collection: {COLLECTION_NAME}")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,        # <- Your model's embedding dimension
            distance="Cosine"
        )
    )
else:
    print(f"Collection {COLLECTION_NAME} already exists")

# Load your chunks_with_embeddings.json
with open("./chunks_with_embeddings.json", "r") as f:
    chunks = json.load(f)

# Prepare points
points = []
for chunk in tqdm(chunks, desc="Preparing points"):
    points.append(
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"])),
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "title": chunk.get("title"),
                "source": chunk.get("source"),
                "document_type": chunk.get("document_type"),
                "url": chunk.get("url"),
            }
        )
    )

# Upload to Qdrant
print("Uploading points to Qdrant...")
client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)
print("Upload complete!")

# Optional: Simple search function
# def search(query_vector, top_k=5):
#     results = client.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=query_vector,
#         limit=top_k
#     )
#     return [
#         {
#             "id": point.id,
#             "score": point.score,
#             "text": point.payload.get("text")
#         }
#         for point in results
#     ]

# Example usage:
# if __name__ == "__main__":

#     test_query = "Explain RBI circulars related to banks"
#     query_vector = generate_embedding(test_query)
#     top_results = search(query_vector, top_k=5)
#     for idx, res in enumerate(top_results, 1):
#         print(f"{idx}. {res['text'][:200]}...")  # preview first 200 chars