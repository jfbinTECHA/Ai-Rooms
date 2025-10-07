from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from typing import Optional

app = FastAPI(title="AI Rooms Model Workers", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-3.5-turbo"
    max_tokens: Optional[int] = 150

class ChatResponse(BaseModel):
    response: str

# Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = openai.ChatCompletion.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            max_tokens=request.max_tokens
        )
        return ChatResponse(response=response.choices[0].message.content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    try:
        models = openai.Model.list()
        return {"models": [model.id for model in models.data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Placeholder for local models
@app.post("/local_chat", response_model=ChatResponse)
async def local_chat(request: ChatRequest):
    # TODO: Implement local model inference
    return ChatResponse(response=f"Local model echo: {request.message}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)