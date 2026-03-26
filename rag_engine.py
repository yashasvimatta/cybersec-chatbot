"""
RAG Engine
Handles document indexing, embeddings, vector search, and answer generation
Now supports: Anthropic Claude, OpenAI GPT-4, and Google Gemini
Vector store: PostgreSQL + pgvector (cosine similarity)
"""
import os
import time
import hashlib
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from openai import OpenAI
import anthropic
import google.generativeai as genai

# Load environment variables
load_dotenv()


# ──────────────────────────────────────────────────────────────
#  Core FAQ — always injected into prompts so the LLM can answer
#  common cybersecurity questions even without a KB hit.
#  Tailored for C&S Wholesale Groceries.
# ──────────────────────────────────────────────────────────────
CORE_FAQ = """
## C&S Cybersecurity – Frequently Asked Questions

### Secure Email Sharing (Encryption)
Always use company-approved email encryption when sending sensitive information (e.g., personal data, financial details, confidential documents). Double-check recipients before sending, avoid auto-forwarding to personal accounts, and never send passwords in the same email as attachments. When unsure, contact the Cybersecurity Team.

### Secure File Sharing
Share files only through approved secure platforms (e.g., company cloud storage or secure collaboration tools). Set proper access permissions (least privilege), use password protection when required, and avoid using personal file-sharing apps. Revoke access when it is no longer needed.

### Acceptable Use – Internet Browsing
Use the internet primarily for business purposes. Avoid visiting suspicious, illegal, or non-work-related high-risk websites. Do not download unauthorized software. Follow company policies and ensure company devices are used responsibly and securely at all times.

### Blocked Messages – Who Do I Contact?
If a legitimate email or file is blocked, contact the IT Service Desk or Cybersecurity Team immediately. Do not attempt to bypass security controls. Provide details (sender, subject, time received) so the team can review and safely release it if appropriate.

### Phishing – Suspicious Emails
Do not click links, open attachments, or reply to suspicious emails. Report the email immediately using the company's phishing reporting tool or forward it to the Cybersecurity Team. Delete it only after reporting. If you accidentally clicked something, notify IT immediately.

### What Can I Do to Help Keep Us Cyber Secure?
- Practice safe browsing
- Report phishing or suspicious activity immediately
- Use strong, unique passwords and enable MFA
- Never share credentials
- Lock your device when unattended
- Keep software updated
- Follow company security policies
Cybersecurity is everyone's responsibility.

### Contact Information – Cybersecurity Team
- **Email:** CyberSecurity@cswg.com
- **Helpdesk Phone:** 603-354-7500
- **Cybersecurity Website:** https://sites.google.com/cswg.com/cybersecurity

If you see an error message, a blocked file, or anything suspicious — don't hesitate! Reach out to the Cybersecurity team immediately at **CyberSecurity@cswg.com** or call **603-354-7500**.

For any security question — policy clarification, incident reporting, access requests, vendor security reviews — email **CyberSecurity@cswg.com**. The team is here to help, not to judge. No question is too small.

Visit our Cybersecurity website for policies, training materials, and self-service resources: https://sites.google.com/cswg.com/cybersecurity
""".strip()


class SimpleTextSplitter:
    """Simple text splitter — larger chunks = fewer API calls = faster indexing"""

    def __init__(self, chunk_size: int = 2500, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Get chunk
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence end
                last_period = chunk.rfind('. ')
                last_newline = chunk.rfind('\n')
                last_space = chunk.rfind(' ')

                # Use the best boundary found
                break_point = max(last_period, last_newline, last_space)
                if break_point > self.chunk_size * 0.5:  # Only use if reasonably far in
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())

            # Move start position with overlap
            start = end - self.chunk_overlap
            if start <= 0:
                start = end

        return [c for c in chunks if c]  # Filter empty chunks


class RAGEngine:
    def __init__(self):
        # PostgreSQL connection parameters
        self.pg_dsn = os.getenv('PG_DSN', 'postgresql://localhost:5432/fiona')
        self._embedding_dim = None  # Will be set on first embedding call

        # Initialize PostgreSQL with pgvector
        self._init_pgvector()

        # Determine which LLM to use
        llm_provider = os.getenv('LLM_PROVIDER', 'gemini').lower()

        if llm_provider == 'gemini':
            # Configure Google Gemini with explicit API key
            gemini_key = os.getenv('GEMINI_API_KEY')
            if not gemini_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=gemini_key)
            # Use a stable Gemini model - try latest first, fallback to stable
            self.model = self._find_available_gemini_model()
            self.llm_client = genai.GenerativeModel(self.model)
            self.provider = 'gemini'
            print(f"✓ Using Google Gemini ({self.model})")

        elif llm_provider == 'anthropic':
            self.llm_client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
            self.model = "claude-sonnet-4-20250514"
            self.provider = 'anthropic'
            print("✓ Using Anthropic Claude")

        else:  # openai
            self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = "gpt-4-turbo-preview"
            self.provider = 'openai'
            print("✓ Using OpenAI GPT-4")

        # For embeddings - use Gemini by default
        self.embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'gemini').lower()

        # Initialize OpenAI client only if needed
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        else:
            self.openai_client = None

        if self.embedding_provider == 'gemini':
            # Try to find an available Gemini embedding model
            self.embedding_model = self._find_available_gemini_embedding_model()
            if self.embedding_model:
                print(f"✓ Using Gemini embeddings ({self.embedding_model})")
            else:
                print("⚠️  No Gemini embedding models found, will attempt with available models")
                self.embedding_model = 'models/text-embedding-004'  # Default attempt
        else:
            if not openai_key:
                print("⚠️  OpenAI API key not found, falling back to Gemini")
                self.embedding_provider = 'gemini'
                self.embedding_model = 'models/embedding-001'
            else:
                self.embedding_model = 'text-embedding-3-small'
                print("✓ Using OpenAI embeddings (text-embedding-3-small)")

        # Text splitter — larger chunks = fewer embeddings = faster
        self.text_splitter = SimpleTextSplitter(
            chunk_size=2500,
            chunk_overlap=200
        )

        # Batch size for embedding API calls (Gemini supports up to 100)
        self.embedding_batch_size = int(os.getenv('EMBEDDING_BATCH_SIZE', '100'))

        # Small in-process cache for query embeddings — avoids a round-trip to
        # the embedding API when the same question is asked more than once in a
        # session.  Capped at 512 entries to bound memory usage.
        self._query_embedding_cache: dict = {}
        self._QUERY_CACHE_MAX = 512

        print(f"✓ RAG Engine initialized (LLM: {self.provider}, Vector DB: PostgreSQL+pgvector)")

    # ── PostgreSQL + pgvector ─────────────────────────────────

    def _get_conn(self):
        """Get a new PostgreSQL connection."""
        conn = psycopg2.connect(self.pg_dsn)
        conn.autocommit = False
        return conn

    def _init_pgvector(self):
        """Initialize pgvector extension and create tables if needed."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            # Create the chunks table — embedding column added dynamically on first insert
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kb_chunks (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_path TEXT NOT NULL DEFAULT '',
                    chunk_index INTEGER NOT NULL DEFAULT 0,
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL DEFAULT '',
                    modified_time TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_kb_chunks_source_id ON kb_chunks(source_id);
            """)
            conn.commit()
            print("✓ PostgreSQL + pgvector initialized")
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Failed to initialize pgvector: {e}")
        finally:
            conn.close()

    def _ensure_embedding_column(self, dim: int):
        """Add the embedding vector column if it doesn't exist yet."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            # Check if column exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'kb_chunks' AND column_name = 'embedding';
            """)
            if not cur.fetchone():
                cur.execute(f"ALTER TABLE kb_chunks ADD COLUMN embedding vector({dim});")
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding
                    ON kb_chunks USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """)
                conn.commit()
                print(f"✓ Added embedding column (vector({dim})) with IVFFlat index")
            else:
                conn.commit()
        except psycopg2.errors.DuplicateColumn:
            conn.rollback()
        except Exception as e:
            conn.rollback()
            # If IVFFlat index creation fails (needs enough rows), use HNSW or skip
            if "ivfflat" in str(e).lower():
                try:
                    conn2 = self._get_conn()
                    cur2 = conn2.cursor()
                    cur2.execute(f"ALTER TABLE kb_chunks ADD COLUMN IF NOT EXISTS embedding vector({dim});")
                    conn2.commit()
                    conn2.close()
                    print(f"✓ Added embedding column (vector({dim})), index will be created after data load")
                except Exception:
                    pass
            else:
                raise
        finally:
            conn.close()

    def _create_index_if_needed(self):
        """Create the IVFFlat index if enough rows exist and index doesn't exist."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM kb_chunks WHERE embedding IS NOT NULL;")
            count = cur.fetchone()[0]
            if count >= 100:
                cur.execute("""
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'kb_chunks' AND indexname = 'idx_kb_chunks_embedding';
                """)
                if not cur.fetchone():
                    cur.execute("""
                        CREATE INDEX idx_kb_chunks_embedding
                        ON kb_chunks USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100);
                    """)
                    conn.commit()
                    print("✓ Created IVFFlat index on embeddings")
                else:
                    conn.commit()
            else:
                conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    def _find_available_gemini_embedding_model(self) -> str:
        """Find an available Gemini embedding model"""
        try:
            # List available models
            models = genai.list_models()
            embedding_models = [
                m.name for m in models
                if 'embedding' in m.name.lower() and 'embed' in str(m.supported_generation_methods).lower()
            ]
            if embedding_models:
                # Return the first available embedding model
                return embedding_models[0]
        except Exception as e:
            print(f"Could not list models: {str(e)}")

        # Fallback to trying common model names
        for model_name in [
            'models/text-embedding-004',
            'models/embedding-001',
            'models/text-embedding-004-2',
        ]:
            try:
                # Try to use the model with a dummy embedding
                result = genai.embed_content(
                    model=model_name,
                    content="test",
                    task_type="retrieval_document"
                )
                return model_name
            except:
                continue

        return None

    def _find_available_gemini_model(self) -> str:
        """Find an available Gemini LLM model"""
        # Try models in order of preference
        candidate_models = [
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
        ]

        for model_name in candidate_models:
            try:
                # Just try to instantiate the model without testing
                test_model = genai.GenerativeModel(model_name)
                print(f"   ✓ Model '{model_name}' is available")
                return model_name
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "not supported" in error_msg:
                    print(f"   ✗ Model '{model_name}' not found, trying next...")
                    continue
                # For other errors, the model likely exists
                print(f"   ⚠️  Model '{model_name}' available (auth/quota issue but model exists)")
                return model_name

        # If nothing works, return gemini-pro as ultimate fallback
        print(f"   ⚠️  Using fallback model 'gemini-pro'")
        return 'gemini-pro'

    def _doc_hash(self, content: str) -> str:
        """Quick hash to detect unchanged documents"""
        return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

    def _get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a BATCH of texts in a single API call.
        Gemini embed_content supports list input — 1 call for 100 chunks.
        """
        if not texts:
            return []

        if self.embedding_provider == 'gemini':
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=texts,
                    task_type="retrieval_document"
                )
                embeddings = result['embedding']
                # Detect dimension on first call
                if self._embedding_dim is None and embeddings:
                    self._embedding_dim = len(embeddings[0])
                    self._ensure_embedding_column(self._embedding_dim)
                return embeddings
            except Exception as e:
                # Fallback: if batch fails, try individually
                print(f"\n    ⚠️  Batch embed failed ({str(e)[:40]}), falling back to sequential")
                return [self._get_embedding_with_retry(t) for t in texts]
        else:
            # OpenAI also supports batch
            if self.openai_client:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=texts
                )
                embeddings = [d.embedding for d in response.data]
                if self._embedding_dim is None and embeddings:
                    self._embedding_dim = len(embeddings[0])
                    self._ensure_embedding_column(self._embedding_dim)
                return embeddings
            return [self._get_embedding_with_retry(t) for t in texts]

    def _index_single_doc(self, doc: Dict, doc_idx: int, total: int) -> int:
        """Index a single document: chunk -> batch embed -> batch insert into PostgreSQL. Returns chunk count."""
        try:
            chunks = self.text_splitter.split_text(doc['content'])
            if not chunks:
                return 0

            print(f"  [{doc_idx}/{total}] 📄 {doc['name'][:50]} ({len(chunks)} chunks)", flush=True)

            all_rows = []
            content_hash = doc.get('_content_hash', self._doc_hash(doc['content']))

            # Process in batches
            for batch_start in range(0, len(chunks), self.embedding_batch_size):
                batch = chunks[batch_start:batch_start + self.embedding_batch_size]

                # One API call for the entire batch
                embeddings = self._get_batch_embeddings(batch)

                for i, (chunk, emb) in enumerate(zip(batch, embeddings)):
                    idx = batch_start + i
                    chunk_id = f"{doc['id']}_chunk_{idx}"
                    # Compact float format: pgvector stores float4 so 8 sig. digits
                    # is sufficient and produces ~40% shorter SQL strings.
                    emb_str = '[' + ','.join(f'{v:.8g}' for v in emb) + ']'
                    all_rows.append((
                        chunk_id,
                        doc['id'],
                        doc['name'],
                        doc['path'],
                        idx,
                        chunk,
                        content_hash,
                        str(doc.get('modifiedTime', '')),
                        emb_str,
                    ))

            # Batch insert into PostgreSQL
            if all_rows:
                conn = self._get_conn()
                try:
                    cur = conn.cursor()
                    execute_values(cur, """
                        INSERT INTO kb_chunks (id, source_id, source_name, source_path, chunk_index, content, content_hash, modified_time, embedding)
                        VALUES %s
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            content_hash = EXCLUDED.content_hash,
                            modified_time = EXCLUDED.modified_time,
                            embedding = EXCLUDED.embedding
                    """, all_rows, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s::vector)")
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()

            print(f"      ✓ {len(all_rows)} chunks indexed", flush=True)
            return len(all_rows)

        except Exception as e:
            print(f"      ❌ {doc['name'][:40]}: {str(e)[:60]}")
            return 0

    def _get_indexed_doc_hashes(self) -> Dict[str, str]:
        """Get a map of source_id -> content_hash for all indexed docs."""
        indexed = {}
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT source_id, content_hash FROM kb_chunks WHERE content_hash != '';")
            for row in cur.fetchall():
                indexed[row[0]] = row[1]
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()
        return indexed

    def _remove_doc_chunks(self, source_id: str):
        """Remove all chunks for a given source_id."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM kb_chunks WHERE source_id = %s;", (source_id,))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    def index_documents(self, documents: List[Dict]) -> int:
        """
        Index documents — FAST version with change detection.
        - Skips unchanged docs (by content hash)
        - Re-indexes modified docs automatically
        - Removes deleted docs from the index
        - Batch embeddings + batch PostgreSQL upserts
        - Parallel processing
        """
        valid_docs = [d for d in documents if d['content'].strip()]

        # Get hashes of already-indexed docs
        indexed_hashes = self._get_indexed_doc_hashes()
        indexed_source_ids = set(indexed_hashes.keys())
        current_source_ids = set(d['id'] for d in valid_docs)

        # Detect new, changed, and deleted docs
        docs_to_index = []
        skipped = 0
        updated = 0

        for doc in valid_docs:
            doc_hash = self._doc_hash(doc['content'])
            old_hash = indexed_hashes.get(doc['id'])

            if old_hash == doc_hash:
                skipped += 1  # Unchanged
            elif old_hash is not None:
                # File changed — remove old chunks, re-index
                self._remove_doc_chunks(doc['id'])
                doc['_content_hash'] = doc_hash
                docs_to_index.append(doc)
                updated += 1
            else:
                # New file
                doc['_content_hash'] = doc_hash
                docs_to_index.append(doc)

        # Remove docs that were deleted from kb_raw
        deleted_ids = indexed_source_ids - current_source_ids
        for sid in deleted_ids:
            self._remove_doc_chunks(sid)

        total = len(docs_to_index)
        print(f"\n📚 Index sync: {total} to index ({skipped} unchanged, {updated} updated, {len(deleted_ids)} removed)")
        if total == 0:
            print("✓ Index is up to date\n")
            return 0

        print("=" * 60)
        start_time = time.time()

        total_chunks = 0
        max_workers = min(4, total)

        if max_workers <= 1 or total <= 2:
            for idx, doc in enumerate(docs_to_index, 1):
                total_chunks += self._index_single_doc(doc, idx, total)
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._index_single_doc, doc, idx, total): doc
                    for idx, doc in enumerate(docs_to_index, 1)
                }
                for future in as_completed(futures):
                    try:
                        total_chunks += future.result()
                    except Exception as e:
                        doc = futures[future]
                        print(f"      ❌ {doc['name'][:40]}: {str(e)[:60]}")

        elapsed = time.time() - start_time
        print("=" * 60)
        print(f"✓ Indexed {total_chunks} chunks from {total} docs in {elapsed:.1f}s")
        if total_chunks > 0:
            print(f"  Speed: {total_chunks / elapsed:.0f} chunks/sec")
        print("=" * 60 + "\n")

        # Try to create index if enough data
        self._create_index_if_needed()

        return total_chunks

    def _get_query_embedding(self, query: str) -> List[float]:
        """
        Embedding for a search query.
        Uses `retrieval_query` task_type (better semantic matching than `retrieval_document`).
        Caches results so repeated queries skip the API round-trip.
        """
        cache_key = query.strip().lower()
        if cache_key in self._query_embedding_cache:
            return self._query_embedding_cache[cache_key]

        if self.embedding_provider == 'gemini':
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=query,
                    task_type="retrieval_query",
                )
                emb = result['embedding']
            except Exception:
                # Fall back to the general embedding path on any error
                emb = self._get_embedding(query)
        else:
            emb = self._get_embedding(query)

        if len(self._query_embedding_cache) < self._QUERY_CACHE_MAX:
            self._query_embedding_cache[cache_key] = emb
        return emb

    def retrieve_relevant_docs(self, query: str, folder_id: str = None, top_k: int = 10, similarity_threshold: float = 0.2) -> List[Dict]:
        """
        Retrieve most relevant document chunks for a query using pgvector cosine distance.
        similarity_threshold: minimum similarity (1 - cosine_distance) to include.
        """
        # Use query-optimised embedding with in-process cache
        query_embedding = self._get_query_embedding(query)
        # Use compact float representation — pgvector stores float4 (~6 sig. digits),
        # so 8 significant digits is more than sufficient and produces ~40% shorter strings.
        emb_str = '[' + ','.join(f'{v:.8g}' for v in query_embedding) + ']'

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            # Use cosine distance operator <=> from pgvector
            cur.execute("""
                SELECT content, source_id, source_name, source_path, chunk_index,
                       modified_time, content_hash,
                       (embedding <=> %s::vector) AS distance
                FROM kb_chunks
                WHERE embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT %s;
            """, (emb_str, top_k))

            rows = cur.fetchall()
            conn.commit()
        except Exception:
            conn.rollback()
            return []
        finally:
            conn.close()

        # Format results with similarity threshold filter
        relevant_docs = []
        for row in rows:
            distance = row[7]
            similarity = max(0, 1 - distance)

            if similarity >= similarity_threshold:
                relevant_docs.append({
                    'content': row[0],
                    'metadata': {
                        'source_id': row[1],
                        'source_name': row[2],
                        'source_path': row[3],
                        'chunk_index': row[4],
                        'modified_time': row[5],
                        'content_hash': row[6],
                    },
                    'distance': distance,
                    'similarity': similarity,
                })

        return relevant_docs

    def generate_answer(self, query: str, relevant_docs: List[Dict], history: List[Dict] = None, persona: Dict = None) -> Tuple[str, List[dict], float]:
        """
        Generate answer using LLM with retrieved context
        If relevant docs exist, answer based on them
        If no relevant docs, allow LLM to use its general knowledge
        history: optional list of {role, content} for conversation context
        persona: optional dict with department and role
        Returns: (answer, sources, confidence_score)
        """
        history = history or []

        # Build context from relevant documents if available
        context = self._build_context(relevant_docs) if relevant_docs else None

        # Create appropriate prompt based on whether we have context
        if context and relevant_docs:
            # We have relevant documents - use RAG mode
            prompt = self._create_prompt_with_context(query, context, history, persona)
        else:
            # No relevant documents - use general knowledge mode
            prompt = self._create_prompt_general_knowledge(query, history, persona)

        # Generate answer based on provider
        if self.provider == 'gemini':
            answer = self._generate_with_gemini(prompt)
        elif self.provider == 'anthropic':
            answer = self._generate_with_anthropic(prompt)
        else:
            answer = self._generate_with_openai(prompt)

        # Post-process: strip refusal phrases that Gemini sometimes inserts
        answer = self._clean_refusals(answer, query)

        # Extract sources (only if we used documents)
        sources = self._extract_sources(relevant_docs) if relevant_docs else []

        # Calculate confidence (only if we used documents)
        confidence = self._calculate_confidence(relevant_docs) if relevant_docs else 0.0

        return answer, sources, confidence

    def _clean_refusals(self, answer: str, query: str) -> str:
        """Strip refusal phrases from the response. If the entire response is a refusal, replace it."""
        import re

        refusal_patterns = [
            r"I\s*(am\s+)?sorry,?\s*but\s+I\s+cannot\b.*?\.",
            r"I\s+cannot\s+answer\b.*?\.",
            r"I\s+can'?t\s+provide\b.*?\.",
            r"I\s+don'?t\s+have\s+(access|information|data)\b.*?\.",
            r"I\s+am\s+unable\s+to\b.*?\.",
            r"I\s+do\s+not\s+have\s+(the\s+)?(ability|information|access)\b.*?\.",
            r"The\s+provided\s+knowledge\s+base\s+does\s+not\s+contain\b.*?\.",
        ]

        cleaned = answer
        for pat in refusal_patterns:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

        # Remove leftover blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()

        # If the entire response was a refusal (now empty), generate a fallback
        if len(cleaned) < 20:
            cleaned = (
                f"I don't have specific information about \"{query}\" in our knowledge base yet. "
                f"This topic may not be indexed. Try rephrasing your question, or ask me something "
                f"about our security policies, incident response, or other indexed documents."
            )

        return cleaned

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.embedding_provider == 'gemini':
            # Use Gemini embeddings
            try:
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                emb = result['embedding']
                if self._embedding_dim is None:
                    self._embedding_dim = len(emb)
                    self._ensure_embedding_column(self._embedding_dim)
                return emb
            except Exception as e:
                error_msg = str(e)
                if "not found" in error_msg or "not supported" in error_msg:
                    # Model doesn't exist, try to find another one (only once)
                    if not hasattr(self, '_model_search_attempted'):
                        self._model_search_attempted = True
                        print(f"\n⚠️  Model {self.embedding_model} not available")
                        new_model = self._find_available_gemini_embedding_model()
                        if new_model and new_model != self.embedding_model:
                            print(f"   Trying {new_model}...")
                            self.embedding_model = new_model
                            return self._get_embedding(text)  # Retry with new model

                # If we have OpenAI as fallback, try it
                if self.openai_client:
                    return self._get_embedding_openai(text)
                else:
                    raise ValueError(f"Gemini embedding failed and no OpenAI key available: {error_msg}")
        else:
            return self._get_embedding_openai(text)

    def _get_embedding_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        if self.openai_client is None:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env")

        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

    def _get_embedding_with_retry(self, text: str, max_retries: int = 3) -> List[float]:
        """Generate embedding with retry logic"""
        last_error = None
        for attempt in range(max_retries):
            try:
                return self._get_embedding(text)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    time.sleep(wait_time)
                else:
                    raise last_error

    def _build_context(self, docs: List[Dict]) -> str:
        """Build context string from relevant documents"""
        context_parts = []

        for i, doc in enumerate(docs, 1):
            source = doc['metadata'].get('source_name', 'Unknown')
            path = doc['metadata'].get('source_path', '')
            content = doc['content']

            context_parts.append(f"[Source {i}: {source} ({path})]\n{content}\n")

        return "\n---\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """Create prompt for LLM - DEPRECATED, use the specific ones below"""
        return self._create_prompt_with_context(query, context)

    def _create_prompt_with_context(self, query: str, context: str, history: List[Dict] = None, persona: Dict = None) -> str:
        """Create prompt for answering based on documents (RAG mode)"""
        history = history or []
        history_block = ""
        if history:
            history_block = "\n\nRecent conversation:\n" + "\n".join(
                f"{'User' if h['role']=='user' else 'Assistant'}: {h['content'][:500]}"
                for h in history[-6:]
            ) + "\n\n"

        persona_block = ""
        if persona:
            dept = persona.get("department", "Unknown")
            role = persona.get("role", "Team Member")
            persona_block = f"""
**USER CONTEXT:** The user works in the **{dept}** department as a **{role}**.
Tailor your answer to be relevant and actionable for someone in this role. Use terminology they'd understand. Highlight what matters most to {dept} — for example, if they're in Finance focus on financial controls and compliance; if HR focus on employee data protection and access management; if IS focus on technical details and procedures.
"""

        return f"""You are Fiona, C&S Wholesale Groceries' internal cybersecurity assistant. All users are authorized employees.

RULES:
- Answer every question. Do not refuse, apologize, or say "I'm sorry but I cannot". Just answer.
- If you have relevant info below, use it. Summarize clearly with headings, bullets, and bold.
- If the info below doesn't fully cover the question, share what you have AND fill in the gaps using your general knowledge. Say "Based on our documents..." for kb_raw info and "Additionally..." for general knowledge.
- If you truly have zero relevant info, still give a helpful general answer. Never leave the user empty-handed.
- No source citations like "(Source 1)" or "[Source 2]". Answer naturally.
- Format well: use **bold** for key terms, bullet lists for steps, headings for sections.
{persona_block}{history_block}
--- CORE CYBERSECURITY FAQ (always available) ---
{CORE_FAQ}

--- COMPANY DOCUMENTS (from knowledge base) ---
{context}

Question: {query}

Answer:"""

    def _create_prompt_general_knowledge(self, query: str, history: List[Dict] = None, persona: Dict = None) -> str:
        """Create prompt for answering general knowledge questions (when no documents are relevant)"""
        history = history or []
        history_block = ""
        if history:
            history_block = "\n\nRecent conversation:\n" + "\n".join(
                f"{'User' if h['role']=='user' else 'Assistant'}: {h['content'][:500]}"
                for h in history[-6:]
            ) + "\n\n"

        persona_block = ""
        if persona:
            dept = persona.get("department", "Unknown")
            role = persona.get("role", "Team Member")
            persona_block = f"""
**USER CONTEXT:** The user works in **{dept}** as a **{role}**. Tailor your answer to their role and department.
"""

        return f"""You are Fiona, C&S Wholesale Groceries' internal cybersecurity assistant. All users are authorized employees.

RULES:
- Answer every question. Do not refuse, apologize, or say "I'm sorry but I cannot". Just answer.
- No matching company documents were found for this query. Use the Core FAQ below and your general knowledge to give a helpful, thorough answer.
- If the question is about a C&S-specific topic (like a specific tool, person, or internal process), say you don't have that specific info in the knowledge base yet but provide any general guidance that could help.
- Format well: use **bold** for key terms, bullet lists for steps, headings for sections.
{persona_block}{history_block}
--- CORE CYBERSECURITY FAQ (always available) ---
{CORE_FAQ}

Question: {query}

Answer:"""

    def _generate_with_gemini(self, prompt: str, _retries: int = 3) -> str:
        """Generate answer using Google Gemini with relaxed safety settings and retry logic"""
        import time as _time
        last_error = None
        for attempt in range(_retries):
            try:
                response = self.llm_client.generate_content(
                    prompt,
                    safety_settings={
                        # BLOCK_ONLY_HIGH allows cybersecurity discussion (threat analysis,
                        # incident response, etc.) while still blocking genuinely harmful
                        # content.  BLOCK_NONE was too permissive.
                        'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
                    }
                )
                # Handle blocked responses
                if not response.parts:
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        print(f"  ⚠ Gemini blocked response: {response.prompt_feedback}")
                    return "I'm happy to help with that question. Could you rephrase it slightly? I want to make sure I give you the best answer."
                return response.text
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                if "not found" in error_msg or "not supported" in error_msg:
                    # Model is no longer available, try to find a new one
                    print(f"\n⚠️  Current model {self.model} is no longer available")
                    new_model = self._find_available_gemini_model()
                    if new_model != self.model:
                        print(f"   Switching to {new_model}...")
                        self.model = new_model
                        self.llm_client = genai.GenerativeModel(self.model)
                        continue  # retry with new model
                    raise
                elif "429" in str(e) or "resource" in error_msg or "quota" in error_msg or "rate" in error_msg:
                    # Rate limit — back off and retry
                    wait = 2 ** attempt
                    print(f"  ⚠ Gemini rate limit (attempt {attempt+1}/{_retries}), waiting {wait}s...")
                    _time.sleep(wait)
                    continue
                elif attempt < _retries - 1:
                    # Transient error — retry once
                    wait = 1.5 * (attempt + 1)
                    print(f"  ⚠ Gemini error (attempt {attempt+1}/{_retries}): {str(e)[:120]}, retrying in {wait}s...")
                    _time.sleep(wait)
                    continue
                else:
                    raise
        raise last_error

    def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate answer using Anthropic Claude"""
        message = self.llm_client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def _generate_with_openai(self, prompt: str) -> str:
        """Generate answer using OpenAI GPT"""
        response = self.llm_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024
        )
        return response.choices[0].message.content

    def _extract_sources(self, docs: List[Dict]) -> List[dict]:
        """Extract unique sources from relevant documents"""
        sources = []
        seen = set()

        for doc in docs:
            source_id = doc['metadata'].get('source_id')
            if source_id not in seen:
                sources.append({
                    'name': doc['metadata'].get('source_name', 'Unknown'),
                    'path': doc['metadata'].get('source_path', ''),
                    'id': source_id
                })
                seen.add(source_id)

        return sources

    def _calculate_confidence(self, docs: List[Dict]) -> float:
        """Calculate confidence score based on relevance"""
        if not docs:
            return 0.0

        # Average distance (lower is better, so invert)
        avg_distance = sum(doc.get('distance', 1.0) for doc in docs) / len(docs)
        confidence = max(0.0, min(1.0, 1.0 - avg_distance))

        return round(confidence, 2)

    def clear_index(self):
        """Clear all indexed documents"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM kb_chunks;")
            conn.commit()
            print("✓ Index cleared")
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    def check_status(self) -> bool:
        """Check if RAG engine is operational"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM kb_chunks;")
            count = cur.fetchone()[0]
            conn.commit()
            conn.close()
            print(f"✓ RAG Engine status: {count} chunks indexed (PostgreSQL+pgvector)")
            return True
        except Exception as e:
            print(f"✗ RAG Engine error: {e}")
            return False
