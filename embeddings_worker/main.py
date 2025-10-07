from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI(title="AI Rooms Embeddings Worker", version="1.0.0")

class EmbedRequest(BaseModel):
    text: str
    model: str = "all-MiniLM-L6-v2"

class EmbedResponse(BaseModel):
    embeddings: list[float]

# Load model
model = SentenceTransformer(model)

@app.post("/embed", response_model=EmbedResponse)
async def embed_text(request: EmbedRequest):
    try:
        embeddings = model.encode(request.text)
        return EmbedResponse(embeddings=embeddings.tolist())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# TODO: Add search functionality with vector DB

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)