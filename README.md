# Fiona: Cybersecurity RAG Assistant

Fiona is a local-first cybersecurity assistant for internal knowledge retrieval and employee support.

It combines:
- a React frontend
- a FastAPI backend
- RAG over local documents in `kb_raw/`
- PostgreSQL + pgvector for vector search
- SQLite for conversations, incidents, feedback, and analytics

## Architecture

- Full documentation: `ARCHITECTURE_DOCUMENTATION.md`
- Diagram: `docs/fiona-architecture-diagram.svg`

## Tech Stack

- Frontend: React 18, Vite, Axios
- Backend: Python 3.11, FastAPI, Uvicorn, Pydantic
- RAG/AI: Google Gemini (default), optional OpenAI/Anthropic
- Vector DB: PostgreSQL + pgvector
- App DB: SQLite (`fiona.db`)
- File parsing: PyPDF2, python-docx, python-pptx, pandas/openpyxl

## Repository Layout

- `main_local.py`: Backend API entrypoint
- `rag_engine.py`: Chunking, embeddings, retrieval, answer generation
- `local_file_handler.py`: Reads/extracts text from local files
- `database.py`: SQLite persistence layer
- `frontend/`: React client
- `kb_raw/`: Source knowledge base documents

## Quick Start

### 1. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL with pgvector

```bash
brew install postgresql@16
brew services start postgresql@16
createdb fiona
psql -d fiona -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Create `.env`

Create `.env` in repo root with at least:

```env
GEMINI_API_KEY=your-key
KB_FOLDER=kb_raw
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
PG_DSN=postgresql://localhost:5432/fiona
```

### 4. Start backend

```bash
python main_local.py
```

Backend runs at `http://localhost:8000`.

### 5. Start frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 6. Index documents (optional manual trigger)

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

## Data Storage

Both databases are used:
- PostgreSQL + pgvector stores embeddings/chunks for semantic retrieval.
- SQLite stores operational app data (history, feedback, incidents, analytics, subscriptions).

## Notes

For detailed local setup and extended usage examples, see `README_LOCAL.md`.
