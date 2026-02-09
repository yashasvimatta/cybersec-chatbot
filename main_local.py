"""
RAG Chatbot Backend - FastAPI Server (Local Folder Version)
Works with local knowledge base folder instead of Google Drive
Frontend-compatible: /chat, /reset, /health
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import time
from dotenv import load_dotenv

from local_file_handler import LocalFileHandler
from rag_engine import RAGEngine

load_dotenv()

app = FastAPI(title="RAG Chatbot API - Local KB")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get knowledge base folder from env or use default
KB_FOLDER = os.getenv('KB_FOLDER', 'kb_raw')

# Initialize handlers
file_handler = LocalFileHandler(KB_FOLDER)
rag_engine = RAGEngine()

# In-memory session storage for conversation history (frontend compatibility)
conversations: dict = {}
SESSION_TIMEOUT = 2 * 60 * 60  # 2 hours


class QueryRequest(BaseModel):
    query: str
    folder_path: Optional[str] = None  # Optional subfolder path


class IndexRequest(BaseModel):
    folder_path: Optional[str] = None  # Optional subfolder path, None = index all


class ChatRequest(BaseModel):
    message: str
    sessionId: str


class ResetRequest(BaseModel):
    sessionId: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float


@app.get("/")
async def root():
    """API information"""
    stats = file_handler.get_folder_stats()
    
    return {
        "message": "RAG Chatbot API (Local KB) is running",
        "knowledge_base": KB_FOLDER,
        "stats": {
            "total_files": stats['total_files'],
            "total_folders": stats['total_folders'],
            "file_types": stats['file_types'],
            "size_mb": round(stats['total_size_mb'], 2)
        },
        "endpoints": {
            "/index": "POST - Index documents from local folder",
            "/query": "POST - Query the knowledge base",
            "/refresh": "POST - Refresh the entire index",
            "/health": "GET - Check system health",
            "/stats": "GET - Get knowledge base statistics"
        }
    }


@app.post("/index")
async def index_documents(request: IndexRequest = None):
    """
    Index all documents from local folder
    This should be run initially and periodically to update the knowledge base
    """
    try:
        folder_path = request.folder_path if request else None
        
        # Fetch all documents from local folder
        documents = file_handler.fetch_all_documents(folder_path)
        
        if not documents:
            raise HTTPException(
                status_code=404, 
                detail=f"No documents found in folder: {KB_FOLDER}"
            )
        
        # Process and index documents
        indexed_count = rag_engine.index_documents(documents)
        
        return {
            "status": "success",
            "message": f"Indexed {indexed_count} chunks from {len(documents)} documents",
            "document_count": len(documents),
            "chunk_count": indexed_count,
            "folder": KB_FOLDER
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.post("/query", response_model=ChatResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base with a user question
    Returns answer with sources (if available)
    
    Supports two modes:
    1. Document-based (RAG): If relevant documents found, answers based on them
    2. General knowledge: If no relevant docs, answers using LLM's general knowledge
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get relevant documents
        relevant_docs = rag_engine.retrieve_relevant_docs(
            request.query,
            folder_id=request.folder_path  # Can filter by subfolder
        )
        
        # Generate answer (with or without documents)
        # If relevant_docs is empty, the generate_answer method will use general knowledge
        answer, sources, confidence = rag_engine.generate_answer(
            request.query,
            relevant_docs if relevant_docs else []  # Pass empty list if no docs found
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            confidence=confidence
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Check if all systems are operational - frontend compatible"""
    try:
        folder_status = file_handler.check_connection()
        rag_status = rag_engine.check_status()
        
        return {
            "status": "ok" if (folder_status and rag_status) else "degraded",
            "activeSessions": len(conversations),
            "model": getattr(rag_engine, 'model', 'gemini'),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "knowledge_base_folder": KB_FOLDER,
            "folder_accessible": folder_status,
            "rag_engine": rag_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def _cleanup_old_sessions():
    """Remove sessions older than SESSION_TIMEOUT"""
    now = time.time()
    to_remove = [sid for sid, data in conversations.items() if now - data.get("lastActivity", 0) > SESSION_TIMEOUT]
    for sid in to_remove:
        del conversations[sid]


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint - frontend compatible.
    Accepts { message, sessionId }, returns { reply }.
    Uses RAG with kb_raw + Gemini.
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        _cleanup_old_sessions()
        
        # Get or create session
        if request.sessionId not in conversations:
            conversations[request.sessionId] = {"history": [], "lastActivity": time.time()}
        
        session = conversations[request.sessionId]
        session["lastActivity"] = time.time()
        
        # Build history for context (last 10 exchanges)
        history = session["history"][-20:]  # Last 20 messages (10 exchanges)
        
        # Get relevant docs from kb_raw (empty if not indexed yet)
        try:
            relevant_docs = rag_engine.retrieve_relevant_docs(request.message)
        except Exception:
            relevant_docs = []
        
        # Generate answer with optional conversation history
        answer, sources, confidence = rag_engine.generate_answer(
            request.message,
            relevant_docs if relevant_docs else [],
            history=history
        )
        
        # Update session history
        session["history"].append({"role": "user", "content": request.message})
        session["history"].append({"role": "assistant", "content": answer})
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]
        
        return {
            "reply": answer,
            "conversationLength": len(session["history"]) // 2,
            "sources": sources if relevant_docs else [],
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_chat(request: ResetRequest):
    """Reset conversation - frontend compatible"""
    try:
        if request.sessionId in conversations:
            del conversations[request.sessionId]
        return {"success": True, "message": "Conversation reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the knowledge base"""
    try:
        stats = file_handler.get_folder_stats()
        
        # Get RAG engine stats
        chunk_count = rag_engine.collection.count() if rag_engine.collection else 0
        
        return {
            "folder": KB_FOLDER,
            "files": {
                "total": stats['total_files'],
                "by_type": stats['file_types']
            },
            "folders": stats['total_folders'],
            "size_mb": round(stats['total_size_mb'], 2),
            "indexed_chunks": chunk_count,
            "llm_provider": rag_engine.provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/refresh")
async def refresh_index(request: IndexRequest = None):
    """
    Refresh the index - useful for periodic updates
    Clears existing index and re-indexes all documents
    """
    try:
        # Clear existing index
        rag_engine.clear_index()
        
        # Re-index
        folder_path = request.folder_path if request else None
        documents = file_handler.fetch_all_documents(folder_path)
        
        if not documents:
            raise HTTPException(
                status_code=404,
                detail=f"No documents found in folder: {KB_FOLDER}"
            )
        
        indexed_count = rag_engine.index_documents(documents)
        
        return {
            "status": "success",
            "message": f"Refreshed index with {indexed_count} chunks from {len(documents)} documents",
            "document_count": len(documents),
            "chunk_count": indexed_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Get host and port from env or use defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    
    print("\n" + "=" * 60)
    print("🚀 RAG Chatbot Server (Local KB Version)")
    print("=" * 60)
    print(f"Knowledge Base Folder: {KB_FOLDER}")
    print(f"Server: http://{host}:{port}")
    print("=" * 60 + "\n")
    
    uvicorn.run(app, host=host, port=port)
