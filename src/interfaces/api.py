"""
TARS FastAPI Backend
REST API for interacting with TARS chatbot.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core import TARSEngine, get_tars_engine
from src.utils.config import get_config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tars.api")


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to send to TARS")
    enhance_response: bool = Field(True, description="Whether to add personality enhancements")
    stream: bool = Field(False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    response: str = Field(..., description="TARS response")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class SettingsRequest(BaseModel):
    humor: Optional[int] = Field(None, ge=0, le=100, description="Humor level (0-100)")
    honesty: Optional[int] = Field(None, ge=0, le=100, description="Honesty level (0-100)")
    discretion: Optional[int] = Field(None, ge=0, le=100, description="Discretion level (0-100)")
    responseSpeed: Optional[int] = Field(None, ge=0, le=100, description="Response speed (0=slow/thoughtful, 100=fast)")
    verbosity: Optional[int] = Field(None, ge=0, le=100, description="Verbosity (0=terse, 100=detailed)")
    cautionLevel: Optional[int] = Field(None, ge=0, le=100, description="Caution level (0=bold, 100=careful)")
    trustLevel: Optional[int] = Field(None, ge=0, le=100, description="Trust level (0=skeptical, 100=trusting)")


class SettingsResponse(BaseModel):
    humor: int = Field(..., description="Current humor level")
    honesty: int = Field(..., description="Current honesty level")
    discretion: int = Field(..., description="Current discretion level")
    responseSpeed: int = Field(60, description="Response speed setting")
    verbosity: int = Field(50, description="Verbosity setting")
    cautionLevel: int = Field(40, description="Caution level setting")
    trustLevel: int = Field(70, description="Trust level setting")


class RAGStatsResponse(BaseModel):
    total_documents: int
    loaded_datasets: int
    topics: List[str]
    embedding_model: str
    embedding_dimension: int


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    rag_enabled: bool
    voice_enabled: bool


# Create FastAPI app
app = FastAPI(
    title="TARS API",
    description="REST API for TARS - The sarcastic AI chatbot from Interstellar",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global TARS engine instance
_engine: TARSEngine | None = None


def get_engine() -> TARSEngine:
    """Get or create the TARS engine."""
    global _engine
    if _engine is None:
        _engine = get_tars_engine()
    return _engine


# === Health & Status ===

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "TARS online. Humor at 60%, honesty at 90%. Ready for your queries.",
        "docs": "/docs",
        "version": "2.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health status."""
    config = get_config()
    engine = get_engine()
    
    return HealthResponse(
        status="operational",
        llm_provider=config.llm_provider,
        rag_enabled=engine.use_rag,
        voice_enabled=config.voice_enabled
    )


# === Chat Endpoints ===

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to TARS and get a response.
    
    This is the main chat endpoint for interacting with TARS.
    """
    try:
        engine = get_engine()
        
        if request.stream:
            # For streaming, redirect to streaming endpoint
            return StreamingResponse(
                stream_response(request.message),
                media_type="text/event-stream"
            )
        
        response = engine.chat(request.message, enhance_response=request.enhance_response)
        
        return ChatResponse(
            response=response,
            conversation_id=engine.memory.active_conversation_id
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/greeting")
async def get_greeting():
    """Get a TARS greeting message."""
    engine = get_engine()
    return {"greeting": engine.get_greeting()}


async def stream_response(message: str):
    """Generator for streaming responses."""
    engine = get_engine()
    
    for chunk in engine.chat_stream(message):
        yield f"data: {chunk}\n\n"
        await asyncio.sleep(0.01)  # Small delay for smooth streaming
    
    yield "data: [DONE]\n\n"


@app.websocket("/api/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    engine = get_engine()
    
    # Send greeting
    greeting = engine.get_greeting()
    await websocket.send_json({"type": "greeting", "content": greeting})
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
            
            # Check for streaming mode
            if data.get("stream", False):
                # Stream response
                await websocket.send_json({"type": "start"})
                
                full_response = ""
                for chunk in engine.chat_stream(message):
                    full_response += chunk
                    await websocket.send_json({"type": "chunk", "content": chunk})
                    await asyncio.sleep(0.01)
                
                await websocket.send_json({"type": "end", "full_response": full_response})
            else:
                # Regular response
                response = engine.chat(message)
                await websocket.send_json({"type": "response", "content": response})
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


# === Settings Endpoints ===

@app.get("/api/settings", response_model=SettingsResponse)
async def get_settings():
    """Get current TARS personality settings."""
    config = get_config()
    
    return SettingsResponse(
        humor=int(config.tars_humor_level * 100),
        honesty=int(config.tars_honesty_level * 100),
        discretion=int(config.tars_discretion_level * 100),
        responseSpeed=60,
        verbosity=50,
        cautionLevel=40,
        trustLevel=70
    )


@app.put("/api/settings", response_model=SettingsResponse)
async def update_settings(request: SettingsRequest):
    """Update TARS personality settings."""
    engine = get_engine()
    
    humor = request.humor / 100 if request.humor is not None else None
    honesty = request.honesty / 100 if request.honesty is not None else None
    
    settings = engine.update_personality(humor=humor, honesty=honesty)
    
    return SettingsResponse(
        humor=settings["humor"],
        honesty=settings["honesty"],
        discretion=settings["discretion"],
        responseSpeed=request.responseSpeed or 60,
        verbosity=request.verbosity or 50,
        cautionLevel=request.cautionLevel or 40,
        trustLevel=request.trustLevel or 70
    )


# === History Endpoints ===

@app.get("/api/history")
async def get_history():
    """Get conversation history."""
    engine = get_engine()
    history = engine.get_conversation_history()
    
    return {
        "conversation_id": engine.memory.active_conversation_id,
        "messages": history,
        "count": len(history)
    }


@app.delete("/api/history")
async def clear_history():
    """Clear conversation history."""
    engine = get_engine()
    engine.clear_memory()
    
    return {"message": "Conversation history cleared", "status": "success"}


# === RAG Endpoints ===

@app.get("/api/rag/stats", response_model=RAGStatsResponse)
async def get_rag_stats():
    """Get RAG system statistics."""
    engine = get_engine()
    
    if not engine.use_rag or not engine.rag_system:
        raise HTTPException(status_code=503, detail="RAG system not enabled")
    
    stats = engine.rag_system.get_stats()
    return RAGStatsResponse(**stats)


@app.post("/api/rag/index")
async def index_datasets(directory: str = None):
    """Index datasets for RAG. Uses default directory if not specified."""
    engine = get_engine()
    
    if not engine.use_rag or not engine.rag_system:
        raise HTTPException(status_code=503, detail="RAG system not enabled")
    
    try:
        if directory:
            count = engine.rag_system.index_directory(Path(directory))
        else:
            # Re-index default datasets
            config = get_config()
            datasets_dir = config.project_root / "Datasets Questions and Answers of TARS"
            count = engine.rag_system.index_directory(datasets_dir)
        
        return {"indexed": count, "total": engine.rag_system.get_stats()["total_documents"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/search")
async def search_rag(query: str, n_results: int = 5, topic: str = None):
    """Search the RAG knowledge base."""
    engine = get_engine()
    
    if not engine.use_rag or not engine.rag_system:
        raise HTTPException(status_code=503, detail="RAG system not enabled")
    
    context = engine.rag_system.retrieve(query, n_results=n_results, topic=topic)
    
    return {"query": query, "results": context}


# Run with uvicorn
def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    import uvicorn
    uvicorn.run("src.interfaces.api:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_api()
