"""
Simple FastAPI сервер для LangGraph Orchestrator
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
import uvicorn
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator.orchestrator import orchestrator

app = FastAPI(title="LangGraph Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = "anonymous"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def root():
    return {"service": "LangGraph Agent", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "agents": len(orchestrator.agents)}

@app.get("/agents")
async def get_agents():
    return orchestrator.get_agents_status()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = orchestrator.process(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("="*60)
    print("🚀 LangGraph Agent API")
    print("="*60)
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")