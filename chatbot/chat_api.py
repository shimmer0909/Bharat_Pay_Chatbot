# chat_api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from models.embedding import generate_embedding  # your existing embedding function
# from vector_db.qdrant_store import client, COLLECTION_NAME, generate_embedding, PointStruct
import traceback
from models.llm import generate_answer

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="Semantic Search Chat API")

# -----------------------------
# Vector DB client
# -----------------------------
COLLECTION_NAME = "document_chunks"
client = QdrantClient(host="localhost", port=6333)

# -----------------------------
# Request & Response Models
# -----------------------------
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResult(BaseModel):
    id: str
    score: float
    text: str

class QueryResponse(BaseModel):
    results: List[QueryResult]

class AnswerResponse(BaseModel):
    answer: str
    sources: List[QueryResult]

# -----------------------------
# Helper: Semantic search
# -----------------------------
def semantic_search(query: str, top_k: int = 5) -> List[dict]:
    query_vector = generate_embedding(query)

    # Qdrant 1.17 method
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    return [
        {
            "id": point.id,
            "score": point.score,
            "text": point.payload.get("text")
        }
        for point in results.points
    ]

# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest):
    try:
        results = semantic_search(req.query, req.top_k)
        return {"results": results}
    except Exception as e:
        print("Error in /query:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/answer", response_model=AnswerResponse)
def answer_query_endpoint(req: QueryRequest):
    """
    Returns a summarized answer using top-k relevant chunks.
    """
    try:
        # Step 1: Semantic search
        chunks = semantic_search(req.query, req.top_k)

        if not chunks:
            return {"answer": "No relevant information found.", "sources": []}

        # Step 2: Combine chunks as context
        context = "\n\n".join([c["text"] for c in chunks])
        context = context[:3000]  # limit to first 3000 chars

        # Step 3: Create prompt for LLM
        prompt = f"""
You are an expert assistant. Answer the question based only on the following context.
Context: {context}

Question: {req.query}
Answer concisely and clearly. Provide actionable or numeric details if present in the context.
"""

        # Step 4: Generate answer
        answer = generate_answer(prompt)

        # Step 5: Return answer + sources
        return {"answer": answer, "sources": chunks}

    except Exception as e:
        print("Error in /answer:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

