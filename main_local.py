"""
RAG Chatbot Backend - FastAPI Server (Local Folder Version)
Works with local knowledge base folder instead of Google Drive
Frontend-compatible: /chat, /reset, /health
Auto-indexes kb_raw on startup + watches for new/changed files
Extended: feedback, history, tips, incidents, escalations, acknowledgments, analytics, checklists
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import os
import json
import time
import threading

from dotenv import load_dotenv

from local_file_handler import LocalFileHandler
from rag_engine import RAGEngine
from watchfiles import watch, Change
import database as db
from security_tips import get_tip_of_the_day
from checklists import get_checklists_for_department
from email_service import build_incident_mailto, build_escalation_mailto

load_dotenv()

# Get knowledge base folder from env or use default
KB_FOLDER = os.getenv('KB_FOLDER', 'kb_raw')

# Initialize handlers
file_handler = LocalFileHandler(KB_FOLDER)
rag_engine = RAGEngine()

# Background watcher state
_watcher_thread = None
_watcher_stop = threading.Event()

# Debounce: avoid re-indexing multiple times for a batch of file changes
_last_sync = 0
_SYNC_DEBOUNCE = 3  # seconds


def _sync_index():
    """Sync kb_raw -> ChromaDB. Only indexes new/changed files, skips unchanged."""
    global _last_sync
    now = time.time()
    if now - _last_sync < _SYNC_DEBOUNCE:
        return
    _last_sync = now
    try:
        documents = file_handler.fetch_all_documents()
        if documents:
            rag_engine.index_documents(documents)
    except Exception as e:
        print(f"Warning: Auto-index error: {e}")


def _watcher_loop():
    """Background thread: watches kb_raw for file changes in real time."""
    kb_path = os.path.abspath(KB_FOLDER)
    print(f"Watching {kb_path} for changes (real-time)...")
    try:
        for changes in watch(kb_path, stop_event=_watcher_stop, debounce=2000):
            if _watcher_stop.is_set():
                break
            for change_type, path in changes:
                label = {Change.added: "added", Change.modified: "modified", Change.deleted: "deleted"}.get(change_type, "changed")
                print(f"File {label}: {os.path.basename(path)}")
            print("Re-syncing index...")
            _sync_index()
    except Exception as e:
        if not _watcher_stop.is_set():
            print(f"Warning: Watcher error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB + auto-index + start real-time watcher. Shutdown: stop watcher."""
    global _watcher_thread

    # Initialize SQLite database
    db.init_db()
    print("Database initialized (fiona.db)")

    # Auto-index on startup (only new/changed -- instant if nothing changed)
    print("\nAuto-indexing kb_raw on startup...")
    _sync_index()

    # Start real-time file watcher
    _watcher_stop.clear()
    _watcher_thread = threading.Thread(target=_watcher_loop, daemon=True)
    _watcher_thread.start()

    yield

    # Shutdown
    _watcher_stop.set()
    if _watcher_thread:
        _watcher_thread.join(timeout=5)
    print("Watcher stopped.")


app = FastAPI(title="Fiona - C&S Cybersecurity Assistant API", lifespan=lifespan)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage for conversation history (frontend compatibility)
conversations: dict = {}
SESSION_TIMEOUT = 2 * 60 * 60  # 2 hours


# ── Pydantic Models ───────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    folder_path: Optional[str] = None

class IndexRequest(BaseModel):
    folder_path: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    sessionId: str
    department: Optional[str] = None
    role: Optional[str] = None

class ResetRequest(BaseModel):
    sessionId: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float

class FeedbackRequest(BaseModel):
    sessionId: str
    messageId: str
    query: Optional[str] = None
    answer: Optional[str] = None
    rating: str  # "up" or "down"
    department: Optional[str] = None
    role: Optional[str] = None

class IncidentRequest(BaseModel):
    sessionId: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    incidentType: str
    description: str
    urgency: str = "medium"
    senderEmail: Optional[str] = None

class EscalateRequest(BaseModel):
    sessionId: str
    query: str
    conversationContext: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    senderEmail: Optional[str] = None

class AcknowledgeRequest(BaseModel):
    sessionId: str
    policyName: str
    department: Optional[str] = None
    role: Optional[str] = None


# ── Core Endpoints ────────────────────────────────────────

@app.get("/")
async def root():
    """API information"""
    stats = file_handler.get_folder_stats()
    return {
        "message": "Fiona API is running",
        "knowledge_base": KB_FOLDER,
        "stats": {
            "total_files": stats['total_files'],
            "total_folders": stats['total_folders'],
            "file_types": stats['file_types'],
            "size_mb": round(stats['total_size_mb'], 2)
        },
    }


@app.post("/index")
async def index_documents(request: IndexRequest = None):
    """Index all documents from local folder"""
    try:
        folder_path = request.folder_path if request else None
        documents = file_handler.fetch_all_documents(folder_path)
        if not documents:
            raise HTTPException(status_code=404, detail=f"No documents found in folder: {KB_FOLDER}")
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
    """Query the knowledge base with a user question"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        relevant_docs = rag_engine.retrieve_relevant_docs(request.query, folder_id=request.folder_path)
        answer, sources, confidence = rag_engine.generate_answer(request.query, relevant_docs if relevant_docs else [])
        return ChatResponse(answer=answer, sources=sources, confidence=confidence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Check if all systems are operational"""
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
        return {"status": "unhealthy", "error": str(e)}


def _cleanup_old_sessions():
    """Remove sessions older than SESSION_TIMEOUT"""
    now = time.time()
    to_remove = [sid for sid, data in conversations.items() if now - data.get("lastActivity", 0) > SESSION_TIMEOUT]
    for sid in to_remove:
        del conversations[sid]


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint — returns reply, sources, confidence, and follow-up suggestions.
    Logs analytics event for every query.
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
        history = session["history"][-20:]

        # Get relevant docs from kb_raw
        try:
            relevant_docs = rag_engine.retrieve_relevant_docs(request.message)
        except Exception:
            relevant_docs = []

        # Generate answer with optional conversation history + persona
        persona = None
        if request.department:
            persona = {"department": request.department, "role": request.role or "Team Member"}

        answer, sources, confidence = rag_engine.generate_answer(
            request.message,
            relevant_docs if relevant_docs else [],
            history=history,
            persona=persona
        )

        # Generate follow-up suggestions
        follow_ups = _generate_follow_ups(request.message, answer)

        # Update session history
        session["history"].append({"role": "user", "content": request.message})
        session["history"].append({"role": "assistant", "content": answer})
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]

        # Log analytics event
        try:
            db.log_event(
                event_type="chat",
                session_id=request.sessionId,
                department=request.department,
                role=request.role,
                query=request.message,
                confidence=confidence,
            )
        except Exception:
            pass  # Don't fail chat if analytics logging fails

        # Persist conversation to SQLite
        try:
            db.save_conversation(
                session_id=request.sessionId,
                messages=session["history"],
                department=request.department,
                role=request.role,
            )
        except Exception:
            pass

        return {
            "reply": answer,
            "conversationLength": len(session["history"]) // 2,
            "sources": sources if relevant_docs else [],
            "confidence": round(confidence, 2),
            "followUps": follow_ups,
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"\n❌ /chat error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)[:200]}")


def _generate_follow_ups(query: str, answer: str) -> List[str]:
    """Generate 2-3 follow-up question suggestions based on query + answer."""
    try:
        prompt = f"""Based on this Q&A, suggest exactly 3 short follow-up questions the user might ask next.
Return ONLY a JSON array of 3 strings. No explanation, no markdown, just the JSON array.

Question: {query[:300]}
Answer: {answer[:500]}

JSON array:"""
        if rag_engine.provider == 'gemini':
            response = rag_engine._generate_with_gemini(prompt)
        elif rag_engine.provider == 'anthropic':
            response = rag_engine._generate_with_anthropic(prompt)
        else:
            response = rag_engine._generate_with_openai(prompt)

        # Parse JSON from response
        text = response.strip()
        # Find the JSON array in the response
        start = text.find('[')
        end = text.rfind(']')
        if start >= 0 and end > start:
            arr = json.loads(text[start:end + 1])
            return [str(s).strip() for s in arr[:3] if s]
    except Exception:
        pass
    return []


@app.post("/reset")
async def reset_chat(request: ResetRequest):
    """Reset conversation"""
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
        chunk_count = rag_engine.collection.count() if rag_engine.collection else 0
        return {
            "folder": KB_FOLDER,
            "files": {"total": stats['total_files'], "by_type": stats['file_types']},
            "folders": stats['total_folders'],
            "size_mb": round(stats['total_size_mb'], 2),
            "indexed_chunks": chunk_count,
            "llm_provider": rag_engine.provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/refresh")
async def refresh_index(request: IndexRequest = None):
    """Refresh the index — clears and re-indexes all documents"""
    try:
        rag_engine.clear_index()
        folder_path = request.folder_path if request else None
        documents = file_handler.fetch_all_documents(folder_path)
        if not documents:
            raise HTTPException(status_code=404, detail=f"No documents found in folder: {KB_FOLDER}")
        indexed_count = rag_engine.index_documents(documents)
        return {
            "status": "success",
            "message": f"Refreshed index with {indexed_count} chunks from {len(documents)} documents",
            "document_count": len(documents),
            "chunk_count": indexed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


# ── Feedback ──────────────────────────────────────────────

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Record thumbs up/down feedback on a bot answer."""
    if request.rating not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Rating must be 'up' or 'down'")
    try:
        fid = db.save_feedback(
            session_id=request.sessionId,
            message_id=request.messageId,
            query=request.query,
            answer=request.answer,
            rating=request.rating,
            department=request.department,
            role=request.role,
        )
        return {"success": True, "id": fid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Chat History ──────────────────────────────────────────

@app.get("/history")
async def get_history(sessionId: str):
    """Retrieve persisted conversation history for a session."""
    conv = db.get_conversation(sessionId)
    if conv:
        return {"sessionId": sessionId, "messages": conv["messages"]}
    return {"sessionId": sessionId, "messages": []}


# ── Daily Tip ─────────────────────────────────────────────

@app.get("/tip")
async def daily_tip(department: str = None):
    """Get today's security tip, optionally filtered by department."""
    return get_tip_of_the_day(department)


# ── Incident Reporting ────────────────────────────────────

@app.post("/incident")
async def report_incident(request: IncidentRequest):
    """Submit a security incident report. Returns a mailto: link to CyberSecurity@cswg.com."""
    if not request.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")
    try:
        result = db.save_incident(
            session_id=request.sessionId or "",
            incident_type=request.incidentType,
            description=request.description,
            urgency=request.urgency,
            department=request.department,
            role=request.role,
        )
        db.log_event("incident_report", session_id=request.sessionId,
                     department=request.department, role=request.role,
                     data={"type": request.incidentType, "urgency": request.urgency})

        mailto_url = build_incident_mailto(
            reference=result["reference"],
            incident_type=request.incidentType,
            description=request.description,
            urgency=request.urgency,
            sender_email=request.senderEmail or "",
            department=request.department,
            role=request.role,
        )

        return {"success": True, **result, "mailto_url": mailto_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/incidents")
async def list_incidents():
    """List recent incidents (admin)."""
    return {"incidents": db.get_incidents()}


# ── Escalation ────────────────────────────────────────────

@app.post("/escalate")
async def escalate_to_human(request: EscalateRequest):
    """Escalate a question to the Cybersecurity Team. Returns a mailto: link."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        result = db.save_escalation(
            session_id=request.sessionId,
            query=request.query,
            conversation_context=request.conversationContext or "",
            department=request.department,
            role=request.role,
        )
        db.log_event("escalation", session_id=request.sessionId,
                     department=request.department, role=request.role,
                     query=request.query)

        mailto_url = build_escalation_mailto(
            reference=result["reference"],
            query=request.query,
            conversation_context=request.conversationContext or "",
            sender_email=request.senderEmail or "",
            department=request.department,
            role=request.role,
        )

        return {"success": True, **result, "mailto_url": mailto_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Acknowledgments ───────────────────────────────────────

@app.post("/acknowledge")
async def acknowledge_policy(request: AcknowledgeRequest):
    """Record that a user has read and acknowledged a policy."""
    try:
        aid = db.save_acknowledgment(
            session_id=request.sessionId,
            policy_name=request.policyName,
            department=request.department,
            role=request.role,
        )
        db.log_event("acknowledgment", session_id=request.sessionId,
                     department=request.department, role=request.role,
                     data={"policy": request.policyName})
        return {"success": True, "id": aid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/acknowledgments")
async def get_acknowledgments():
    """Get acknowledgment statistics (admin)."""
    return {"stats": db.get_acknowledgment_stats()}


# ── Analytics ─────────────────────────────────────────────

@app.get("/analytics/summary")
async def analytics_summary(days: int = 30):
    """Get analytics summary for the past N days."""
    return db.get_analytics_summary(days)

@app.get("/analytics/popular")
async def popular_questions(department: str = None, limit: int = 10):
    """Get most popular questions, optionally by department."""
    return {"questions": db.get_popular_questions(department, limit)}

@app.get("/analytics/gaps")
async def kb_gaps(limit: int = 20):
    """Get knowledge base gaps — queries with low confidence or negative feedback."""
    return {"gaps": db.get_kb_gaps(limit)}


# ── Checklists ────────────────────────────────────────────

@app.get("/checklists")
async def get_checklists(department: str = None):
    """Get security checklists relevant to a department."""
    return {"checklists": get_checklists_for_department(department)}


# ── Weekly Digest / Subscriptions ─────────────────────────

class SubscribeRequest(BaseModel):
    email: str
    department: Optional[str] = None
    role: Optional[str] = None

class UnsubscribeRequest(BaseModel):
    email: str

@app.post("/subscribe")
async def subscribe_digest(request: SubscribeRequest):
    """Subscribe to the weekly security digest email."""
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Valid email required")
    ok = db.subscribe(request.email, request.department, request.role)
    return {"success": ok, "message": "Subscribed to weekly digest"}

@app.post("/unsubscribe")
async def unsubscribe_digest(request: UnsubscribeRequest):
    """Unsubscribe from the weekly digest."""
    db.unsubscribe(request.email)
    return {"success": True, "message": "Unsubscribed"}

@app.get("/digest/preview")
async def preview_digest(department: str = None):
    """
    Preview the weekly digest content (for testing / cron integration).
    In production, a cron job would call this endpoint and email it to subscribers.
    """
    data = db.get_digest_data(department)
    tip = get_tip_of_the_day(department)
    subscribers = db.get_active_subscribers()
    return {
        "digest": data,
        "tip_of_the_week": tip,
        "subscriber_count": len(subscribers),
    }


# ── Main ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))

    print("\n" + "=" * 60)
    print("Fiona - C&S Cybersecurity Assistant")
    print("=" * 60)
    print(f"Knowledge Base Folder: {KB_FOLDER}")
    print(f"Server: http://{host}:{port}")
    print("=" * 60 + "\n")

    uvicorn.run(app, host=host, port=port)
