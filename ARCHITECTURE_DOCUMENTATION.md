# Fiona - C&S Cybersecurity Assistant: Full Architecture Documentation

## Overview

**Fiona** is a full-stack cybersecurity assistant built for C&S Wholesale Groceries. It uses **RAG (Retrieval-Augmented Generation)** to answer employee questions about security policies, incident response, and compliance based on internal organizational documents.

**Core Stack:**
- **Frontend:** React 18 + Vite
- **Backend:** Python FastAPI
- **Vector Store:** PostgreSQL + pgvector (cosine similarity)
- **Database:** SQLite (conversations, analytics, incidents)
- **LLM:** Google Gemini (default), with OpenAI and Anthropic as alternatives
- **Knowledge Base:** Local documents in `kb_raw/` folder

---

## High-Level Architecture

```
User (Browser)
    |
    v
React Frontend (port 5173)
    |  Axios HTTP requests
    v
FastAPI Backend (port 8000) -- main_local.py
    |
    |--- RAG Engine (rag_engine.py)
    |       |--- Document Chunking (2500 chars, 200 overlap)
    |       |--- Embedding (Gemini text-embedding-004)
    |       |--- PostgreSQL + pgvector (vector search, cosine similarity)
    |       |--- LLM Generation (Gemini 2.0 Flash)
    |
    |--- SQLite Database (database.py)
    |       |--- Conversations, Feedback, Incidents
    |       |--- Escalations, Analytics, Subscriptions
    |
    |--- File Handler (local_file_handler.py)
    |       |--- PDF, Word, Excel, PPT, CSV, TXT extraction
    |       |--- Recursive folder scanning
    |
    |--- Supporting Modules
            |--- checklists.py (department security checklists)
            |--- security_tips.py (37 rotating daily tips)
            |--- email_service.py (mailto link generation)
```

---

## Project Structure

```
fiona/
├── main_local.py            # FastAPI server & API endpoints (orchestrator)
├── rag_engine.py            # RAG pipeline: chunking, embedding, retrieval, generation
├── database.py              # SQLite persistence (conversations, analytics, feedback)
├── local_file_handler.py    # Document extraction (PDF, Word, Excel, PPT, etc.)
├── checklists.py            # Department-specific security checklists
├── security_tips.py         # 37 rotating daily security tips
├── email_service.py         # Mailto link builders for incidents/escalations
├── query.py                 # CLI utility for testing /query endpoint
├── index_local.py           # CLI utility for manual document indexing
├── requirements.txt         # Python dependencies
├── start.sh                 # Startup script (backend + frontend)
├── run_backend.sh           # Backend-only startup
├── .env                     # Environment config (API keys, providers)
├── fiona.db                 # SQLite database file
├── fiona.db                 # SQLite database (conversations, analytics)
├── kb_raw/                  # Knowledge base documents
│   ├── IS Policies - ACTIVE/
│   ├── FireMon/
│   ├── KPI_s/
│   ├── Knowledge Articles/
│   ├── Vulnerability Management/
│   └── *.pdf, *.docx, etc.
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx              # Central state management & routing
        ├── App.css              # Global styles
        ├── components/
        │   ├── Onboarding.jsx       # 3-step department/role selection
        │   ├── Header.jsx           # Navigation, tools menu, status
        │   ├── ChatWindow.jsx       # Message display, markdown, feedback
        │   ├── ChatInput.jsx        # Message input form
        │   ├── IncidentReport.jsx   # Security incident reporting modal
        │   ├── SecurityChecklist.jsx # Interactive security checklists
        │   └── AnalyticsDashboard.jsx # Analytics (IS/ELT only)
        └── assets/
            └── logo.png
```

---

## Backend Components

### 1. main_local.py - FastAPI Orchestrator

The core backend server that ties everything together.

**Responsibilities:**
- Serves all API endpoints
- Manages user sessions (in-memory, 2-hour timeout, max 20 exchanges per session)
- Auto-indexes documents from `kb_raw/` on startup
- Starts a background file watcher for real-time KB changes (via `watchfiles`)
- Generates follow-up question suggestions after each response

**Session Management:**
- Sessions stored in-memory as a dictionary
- Session ID format: `session_{timestamp}_{random}`
- Automatic cleanup of sessions older than 2 hours
- Conversation history (last 20 exchanges) passed to LLM for context

### 2. rag_engine.py - RAG Pipeline

The core intelligence layer handling document indexing, retrieval, and answer generation.

**Text Chunking:**
- Chunk size: 2,500 characters with 200-character overlap
- Splits at sentence/word boundaries for semantic coherence
- Uses `SimpleTextSplitter` class

**Indexing Pipeline:**
1. Calculate MD5 hash of each document's content
2. Compare with previously indexed hashes (skip unchanged files)
3. Remove old chunks for changed/deleted documents
4. Split new/changed documents into chunks
5. Batch embed chunks (up to 100 per API call via Gemini)
6. Upsert to PostgreSQL via `execute_values` with metadata (source name, path, chunk index, hash)
7. Parallel processing with ThreadPoolExecutor (4 workers)

**Retrieval:**
- Generates query embedding
- Searches PostgreSQL pgvector with cosine distance operator `<=>` (top 10 results, threshold 0.2)
- Returns documents, metadata, and similarity scores

**Answer Generation (Two Modes):**
1. **RAG Mode** (documents found): Answers from documents + fills gaps with general knowledge
2. **General Knowledge Mode** (no documents): Uses built-in Core FAQ + LLM knowledge

**Core FAQ:** Built-in common cybersecurity Q&A (secure email, phishing, acceptable use, etc.) that is always injected into prompts, ensuring users always get a useful answer.

**Refusal Handling:** Strips Gemini refusal phrases and generates fallback answers if response becomes too short.

**Confidence Scoring:**
- Formula: `1 - average_distance` of retrieved documents (0-1 scale)
- User-facing labels: High (70%+), Moderate (40-69%), General knowledge (<40%)

**Supported LLM Providers:**
| Provider | Model | Notes |
|----------|-------|-------|
| Gemini (default) | gemini-2.0-flash (auto-detected) | All safety settings BLOCK_NONE, retry with backoff |
| Anthropic | Claude Sonnet | max_tokens=1024 |
| OpenAI | GPT-4 Turbo Preview | max_tokens=1024 |

**Supported Embedding Providers:**
| Provider | Model | Batch Size |
|----------|-------|------------|
| Gemini (default) | text-embedding-004 | Up to 100 |
| OpenAI | text-embedding-3-small | 1 at a time |

### 3. database.py - SQLite Persistence

Thread-safe SQLite database with WAL mode.

**Tables:**

| Table | Purpose |
|-------|---------|
| `feedback` | Thumbs up/down ratings per message |
| `conversations` | Full chat history (JSON), per session |
| `incidents` | Security incident reports with reference numbers |
| `escalations` | Questions escalated to human cybersecurity team |
| `acknowledgments` | Policy acknowledgment tracking |
| `analytics_events` | Query logs (event type, department, confidence) |
| `subscriptions` | Weekly digest email subscriptions |

**Analytics Functions:**
- `get_analytics_summary(days)` - Total queries, by department, daily volume, low-confidence queries
- `get_popular_questions(dept, limit)` - Most asked questions (for KB gap analysis)
- `get_kb_gaps(limit)` - Queries with <35% confidence OR thumbs-down feedback
- `get_feedback_stats(days)` - Satisfaction percentage

### 4. local_file_handler.py - Document Ingestion

Extracts text from files in the `kb_raw/` folder.

**Supported Formats:**
- PDF (PyPDF2) - page-by-page extraction
- Word (.docx, .doc) - paragraphs + tables
- Excel (.xlsx, .xls) - all sheets with headers
- PowerPoint (.pptx, .ppt) - slide-by-slide
- CSV, plain text, JSON, Markdown, log files - raw text with encoding detection

**Features:**
- Recursive subfolder traversal
- Encoding detection (UTF-8 -> Latin-1 -> CP1252 -> ISO-8859-1)
- Metadata extraction (filename, path, MIME type, modification time)
- Unique IDs based on full file path

### 5. Supporting Modules

**checklists.py** - 6 security checklists targeted by department:
- New Employee Security Setup (all departments)
- Quarterly Access Review (IS, Finance, HR, Procurement)
- Incident Response (all departments)
- Vendor Security (Procurement, IS, Legal, Supply Chain)
- Remote Work Security (all departments)
- Sensitive Data Handling (Finance, HR, Legal, ELT)

**security_tips.py** - 37 daily rotating tips covering phishing, passwords, physical security, file sharing, USB safety, social engineering, MFA, ransomware, and more.

**email_service.py** - Generates pre-filled mailto links for:
- Incident reports -> `CyberSecurity@cswg.com` with reference number, urgency, type, description
- Escalations -> `CyberSecurity@cswg.com` with conversation context

---

## Frontend Components

### App.jsx - Central State Management

Manages all application state and conditional rendering:
- If no persona selected -> show Onboarding
- If persona exists -> show Header + ChatWindow + ChatInput + Modals

**Key State:**
- `theme` (dark/light, persisted to localStorage)
- `persona` (department + role)
- `messages` (chat history array)
- `sessionId` (unique session identifier)
- `status` ("Connected", "Backend offline", "Thinking...")
- Modal states for incidents, checklists, analytics

### Onboarding.jsx - 3-Step Persona Selection

**Step 1: Department** - Choose from 9 departments (Finance, Supply Chain, IS, Retail, Commercial, Procurement, Legal, HR, ELT)

**Step 2: Role** - Choose role within selected department (6 roles per department, e.g., Finance: CFO, Controller, Analyst, AP/AR, Treasurer, Other)

**Step 3: Confirmation** - Summary with department description, use cases, and "Get Started" button

### ChatWindow.jsx - Message Display

**Welcome Screen (no messages):**
- Fiona avatar + personalized greeting
- Tip of the day (dismissible, department-filtered)
- Department-specific suggestion chips (4 per department)
- Common security question chips (6 universal)
- Popular/trending questions from real usage

**Message Rendering:**
- Markdown support (bold, italic, code, headings, lists, code blocks)
- Confidence badge (High/Moderate/General knowledge)
- Sources list (documents used for answer)
- Feedback buttons (thumbs up/down)
- Copy to clipboard
- "Ask a Human" escalation (appears after thumbs down)
- Follow-up suggestion chips

### Header.jsx - Navigation Bar

- Fiona branding + current department/role display
- Connection status indicator
- Theme toggle (Dark/Light)
- Tools dropdown: Report Incident, Security Tasks, Analytics (IS/ELT only), External links
- Switch Role button (returns to onboarding)
- Reset Chat button

### IncidentReport.jsx - Incident Reporting Modal

**Form Fields:**
1. Email address
2. Incident type (7 options: Phishing, Suspicious Activity, Data Leak, Lost Device, Malware, Unauthorized Access, Other)
3. Urgency (Low, Medium, High, Critical)
4. Description

**Flow:** Submit -> Gets reference number (e.g., INC-20260316-0001) -> Opens email client pre-filled to CyberSecurity@cswg.com

### SecurityChecklist.jsx - Interactive Checklists

- Department-filtered checklists with progress bars
- Checkboxes for each item
- Progress persisted to localStorage

### AnalyticsDashboard.jsx - Admin Analytics (IS/ELT Only)

- Total queries (30 days), satisfaction %, feedback totals
- Queries by department (bar chart), daily volume (14-day trend)
- KB gaps (low confidence queries, thumbs-down feedback)

---

## RAG Pipeline Flow

### Indexing (Startup & File Changes)

```
kb_raw/ folder
    |
    v
LocalFileHandler.fetch_all_documents()
    |  Recursively scans, extracts text from PDF/Word/Excel/PPT/CSV/TXT
    v
RAGEngine.index_documents(documents)
    |
    |-- MD5 hash comparison (skip unchanged files)
    |-- Remove old chunks for changed/deleted docs
    |-- Split into 2,500-char chunks (200 overlap)
    |-- Batch embed (100 chunks/API call via Gemini)
    |-- Upsert to PostgreSQL with metadata
    v
PostgreSQL table "kb_chunks"
    (chunk text + 768-dim embeddings + metadata)
```

### Query (POST /chat)

```
User message + department + role
    |
    v
1. RETRIEVAL
    |-- Generate query embedding (Gemini)
    |-- Search PostgreSQL pgvector (top 10, cosine distance)
    |-- Filter by threshold (0.2)
    v
2. CONTEXT BUILDING
    |-- Format retrieved documents as context
    |-- Inject Core FAQ (always available)
    |-- Add conversation history (last 6 exchanges)
    |-- Add persona context (department + role)
    v
3. LLM GENERATION
    |-- Send prompt to Gemini (or OpenAI/Anthropic)
    |-- Strip refusal phrases if any
    v
4. POST-PROCESSING
    |-- Extract source documents
    |-- Calculate confidence (1 - avg_distance)
    |-- Generate 3 follow-up suggestions (separate LLM call)
    v
5. RESPONSE
    |-- Return: {reply, sources, confidence, followUps}
    |-- Log analytics event to SQLite
    |-- Save conversation to database
```

---

## API Endpoints Reference

### Chat & Conversation
| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Main conversation endpoint (message, sessionId, department, role) |
| POST | `/query` | Direct knowledge base query |
| POST | `/reset` | Clear conversation history |
| GET | `/history` | Retrieve persisted conversation |

### Knowledge Base
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info with KB metadata |
| POST | `/index` | Manual full indexing |
| POST | `/refresh` | Clear and re-index all documents |
| GET | `/stats` | KB statistics (files, chunks, size) |
| GET | `/health` | System health check |

### Feedback & Incidents
| Method | Path | Description |
|--------|------|-------------|
| POST | `/feedback` | Submit thumbs up/down rating |
| POST | `/incident` | Report security incident |
| GET | `/incidents` | List all incidents |
| POST | `/escalate` | Escalate question to human team |

### Tools & Analytics
| Method | Path | Description |
|--------|------|-------------|
| GET | `/checklists` | Department security checklists |
| GET | `/tip` | Daily security tip |
| POST | `/acknowledge` | Policy acknowledgment |
| GET | `/analytics/summary` | Query volume, satisfaction, gaps |
| GET | `/analytics/popular` | Most asked questions by dept |
| GET | `/analytics/gaps` | KB gaps (low confidence / negative feedback) |

### Subscriptions
| Method | Path | Description |
|--------|------|-------------|
| POST | `/subscribe` | Subscribe to weekly digest |
| POST | `/unsubscribe` | Unsubscribe from digest |
| GET | `/digest/preview` | Preview weekly digest |

---

## Database Schema

### SQLite (fiona.db)

```sql
feedback (id, session_id, message_id, query, answer, rating, department, role, created_at)
conversations (id, session_id UNIQUE, department, role, messages JSON, created_at, updated_at)
incidents (id, reference UNIQUE, session_id, department, role, incident_type, description, urgency, status, created_at)
escalations (id, reference UNIQUE, session_id, department, role, query, conversation_context, status, created_at)
acknowledgments (id, session_id, department, role, policy_name, created_at)
analytics_events (id, event_type, session_id, department, role, query, confidence, data JSON, created_at)
subscriptions (id, email UNIQUE, department, role, active, created_at)
```

### PostgreSQL + pgvector

```sql
kb_chunks (
    id TEXT PRIMARY KEY,            -- "{source_id}_chunk_{idx}"
    source_id TEXT,                 -- full file path
    source_name TEXT,               -- filename
    source_path TEXT,               -- relative path
    chunk_index INTEGER,
    content TEXT,                   -- chunk text
    content_hash TEXT,              -- MD5 for change detection
    modified_time TEXT,
    embedding vector(768),          -- pgvector column (Gemini embedding dim)
    created_at TIMESTAMPTZ
)
+ IVFFlat index on embedding using cosine distance
```

---

## Environment Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `KB_FOLDER` | `kb_raw` | Local knowledge base folder path |
| `LLM_PROVIDER` | `gemini` | LLM provider (gemini, anthropic, openai) |
| `GEMINI_API_KEY` | - | Google Gemini API key |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (if using) |
| `OPENAI_API_KEY` | - | OpenAI API key (if using) |
| `EMBEDDING_PROVIDER` | `gemini` | Embedding provider (gemini, openai) |
| `EMBEDDING_BATCH_SIZE` | `100` | Chunks per embedding API call |
| `PG_DSN` | `postgresql://localhost:5432/fiona` | PostgreSQL connection string |
| `FIONA_DB_PATH` | `fiona.db` | SQLite database file path |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

---

## Dependencies

### Backend (Python)
- **fastapi** + **uvicorn** - Web server
- **google-generativeai** - Gemini LLM & embeddings
- **psycopg2-binary** - PostgreSQL driver (pgvector for vector search)
- **PyPDF2**, **python-docx**, **python-pptx**, **openpyxl**, **pandas** - Document extraction
- **openai**, **anthropic** - Alternative LLM providers
- **watchfiles** - Real-time file system monitoring
- **tiktoken** - Token counting
- **tqdm** - Progress bars

### Frontend (Node.js)
- **react** 18.3 + **react-dom** - UI framework
- **axios** - HTTP client
- **vite** 5 - Build tool

---

## Key Design Decisions

1. **Incremental Indexing** - MD5 hashes prevent re-indexing unchanged documents, saving time and API costs
2. **Batch Embeddings** - Up to 100 chunks per API call reduces indexing time by ~100x
3. **Core FAQ Injection** - Ensures users always get an answer, even without KB matches
4. **Department Personalization** - Tailored responses, suggestions, checklists, and tips per department
5. **Refusal Stripping** - Ensures Gemini never returns an unhelpful "I can't help" response
6. **Real-Time KB Sync** - Background file watcher with 3-second debounce auto-reindexes on changes
7. **Analytics & Gap Detection** - Tracks low-confidence answers and negative feedback to identify missing documentation
8. **Multi-Provider Support** - Can switch between Gemini, OpenAI, and Anthropic without code changes
