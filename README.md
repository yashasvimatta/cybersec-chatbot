# Fiona: Cybersecurity RAG Assistant

Fiona is a local-first cybersecurity assistant for internal knowledge retrieval and employee support.

It combines:
- a React frontend
- a FastAPI backend
- RAG over local documents in `kb_raw/`
- ChromaDB for vector search
- SQLite for conversations, incidents, feedback, and analytics

## Architecture

- Blueprint: `ARCHITECTURE_BLUEPRINT.md`
- Diagram: `docs/fiona-architecture-diagram.svg`

## Tech Stack

- Frontend: React 18, Vite, Axios
- Backend: Python 3.11, FastAPI, Uvicorn, Pydantic
- RAG/AI: Google Gemini (default), optional OpenAI/Anthropic
- Vector DB: ChromaDB (`chroma_db/`)
- App DB: SQLite (`fiona.db`)
- File parsing: PyPDF2, python-docx, python-pptx, pandas/openpyxl

## Repository Layout

- `main_local.py`: Backend API entrypoint
- `rag_engine.py`: Chunking, embeddings, retrieval, answer generation
- `local_file_handler.py`: Reads/extracts text from local files
- `database.py`: SQLite persistence layer
- `frontend/`: React client
- `kb_raw/`: Source knowledge base documents
- `chroma_db/`: Vector store persistence

## Quick Start

### 1. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env`

Create `.env` in repo root with at least:

```env
GEMINI_API_KEY=your-key
KB_FOLDER=kb_raw
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
```

### 3. Start backend

```bash
python main_local.py
```

Backend runs at `http://localhost:8000`.

### 4. Start frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 5. Index documents (optional manual trigger)

In a new terminal:

```bash
python index_local.py
```

Note: backend also auto-syncs `kb_raw/` on startup and watches for file changes.

## Useful Endpoints

- `GET /health`
- `POST /chat`
- `POST /index`
- `POST /refresh`
- `GET /stats`
- `POST /incident`
- `POST /escalate`
- `GET /analytics/summary`

## Data Storage Clarification

Both databases are used:
- ChromaDB stores embeddings/chunks for semantic retrieval.
- SQLite stores operational app data (history, feedback, incidents, analytics, subscriptions).

## Notes

For detailed local setup and extended usage examples, see `README_LOCAL.md`.
