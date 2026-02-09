"""
RAG Engine
Handles document indexing, embeddings, vector search, and answer generation
Now supports: Anthropic Claude, OpenAI GPT-4, and Google Gemini
"""
import os
import time
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import anthropic
import google.generativeai as genai

# Load environment variables
load_dotenv()


class SimpleTextSplitter:
    """Simple text splitter to replace LangChain dependency"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
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
        # Use persistent ChromaDB storage
        self.client = chromadb.Client(Settings(
            is_persistent=True,
            persist_directory="./chroma_db",
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        
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
        
        # Text splitter for chunking documents
        self.text_splitter = SimpleTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        print(f"✓ RAG Engine initialized (LLM: {self.provider})")
    
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
    
    def index_documents(self, documents: List[Dict]) -> int:
        """
        Index documents into vector database with better error handling
        Returns number of chunks indexed
        """
        total_chunks = 0
        valid_docs = [d for d in documents if d['content'].strip()]
        
        print(f"\n📚 Starting indexing of {len(valid_docs)} documents...")
        print("=" * 60)
        
        for doc_idx, doc in enumerate(valid_docs, 1):
            try:
                # Split document into chunks
                chunks = self.text_splitter.split_text(doc['content'])
                
                print(f"\n[{doc_idx}/{len(valid_docs)}] 📄 {doc['name'][:50]}")
                print(f"    ↳ Splitting: {len(chunks)} chunks...", end=" ", flush=True)
                
                chunks_processed = 0
                for i, chunk in enumerate(chunks):
                    try:
                        # Generate embedding with retry logic
                        embedding = self._get_embedding_with_retry(chunk)
                        
                        # Create unique ID
                        chunk_id = f"{doc['id']}_chunk_{i}"
                        
                        # Add to collection
                        self.collection.add(
                            ids=[chunk_id],
                            embeddings=[embedding],
                            documents=[chunk],
                            metadatas=[{
                                'source_id': doc['id'],
                                'source_name': doc['name'],
                                'source_path': doc['path'],
                                'chunk_index': i,
                                'modified_time': doc.get('modifiedTime', '')
                            }]
                        )
                        
                        total_chunks += 1
                        chunks_processed += 1
                        
                        # Progress indicator every 5 chunks
                        if chunks_processed % 5 == 0 or i == len(chunks) - 1:
                            print(f"\r    ↳ Indexing: {chunks_processed}/{len(chunks)} chunks", end=" ", flush=True)
                    
                    except Exception as chunk_error:
                        print(f"\n    ⚠️  Skipped chunk {i}: {str(chunk_error)[:60]}")
                        continue
                
                print(f" ✓")
                
            except Exception as doc_error:
                print(f"\n    ❌ Error processing document: {str(doc_error)[:60]}")
                continue
        
        print("\n" + "=" * 60)
        print(f"✓ Indexing complete: {total_chunks} chunks from {len(valid_docs)} documents")
        print("=" * 60 + "\n")
        return total_chunks
    
    def retrieve_relevant_docs(self, query: str, folder_id: str = None, top_k: int = 5, similarity_threshold: float = 0.3) -> List[Dict]:
        """
        Retrieve most relevant document chunks for a query
        Only returns documents with similarity above the threshold
        (For cosine distance: 0.0-1.0 scale, where 0 = identical, 1 = completely different)
        similarity_threshold default: 0.5 (cosine distance < 0.5, or similarity > 0.5)
        """
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        # Search vector database
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results with similarity threshold filter
        relevant_docs = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i] if 'distances' in results else 0
                # Convert cosine distance to similarity score (lower distance = higher similarity)
                # Similarity = 1 - distance (so similarity ranges from 0 to 1)
                similarity = max(0, 1 - distance)
                
                # Only include documents that meet the similarity threshold
                if similarity >= similarity_threshold:
                    relevant_docs.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': distance,
                        'similarity': similarity
                    })
        
        return relevant_docs
    
    def generate_answer(self, query: str, relevant_docs: List[Dict]) -> Tuple[str, List[dict], float]:
        """
        Generate answer using LLM with retrieved context
        If relevant docs exist, answer based on them
        If no relevant docs, allow LLM to use its general knowledge
        Returns: (answer, sources, confidence_score)
        """
        # Build context from relevant documents if available
        context = self._build_context(relevant_docs) if relevant_docs else None
        
        # Create appropriate prompt based on whether we have context
        if context and relevant_docs:
            # We have relevant documents - use RAG mode
            prompt = self._create_prompt_with_context(query, context)
            answer_source = "documents"
        else:
            # No relevant documents - use general knowledge mode
            prompt = self._create_prompt_general_knowledge(query)
            answer_source = "general"
        
        # Generate answer based on provider
        if self.provider == 'gemini':
            answer = self._generate_with_gemini(prompt)
        elif self.provider == 'anthropic':
            answer = self._generate_with_anthropic(prompt)
        else:
            answer = self._generate_with_openai(prompt)
        
        # Extract sources (only if we used documents)
        sources = self._extract_sources(relevant_docs) if relevant_docs else []
        
        # Calculate confidence (only if we used documents)
        confidence = self._calculate_confidence(relevant_docs) if relevant_docs else 0.0
        
        return answer, sources, confidence
    
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
                return result['embedding']
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
    
    def _create_prompt_with_context(self, query: str, context: str) -> str:
        """Create prompt for answering based on documents (RAG mode)"""
        return f"""You are a helpful AI assistant with access to an organization's knowledge base. 

**IMPORTANT:** Answer the user's question ONLY based on the provided context from the knowledge base.

If the context doesn't contain enough information to answer the question, clearly state what information you cannot find in the documents.

Always cite which source(s) you're using in your answer.

Context from knowledge base:
{context}

User Question: {query}

Answer:"""
    
    def _create_prompt_general_knowledge(self, query: str) -> str:
        """Create prompt for answering general knowledge questions (when no documents are relevant)"""
        return f"""You are a helpful AI assistant.

The user is asking a question that doesn't match any documents in our knowledge base.
You can use your general knowledge to answer this question.

User Question: {query}

Answer:"""
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate answer using Google Gemini"""
        try:
            response = self.llm_client.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "not supported" in error_msg.lower():
                # Model is no longer available, try to find a new one
                print(f"\n⚠️  Current model {self.model} is no longer available")
                new_model = self._find_available_gemini_model()
                if new_model != self.model:
                    print(f"   Switching to {new_model}...")
                    self.model = new_model
                    self.llm_client = genai.GenerativeModel(self.model)
                    # Retry with new model
                    return self._generate_with_gemini(prompt)
            raise
    
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
        self.client.delete_collection("knowledge_base")
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ Index cleared")
    
    def check_status(self) -> bool:
        """Check if RAG engine is operational"""
        try:
            count = self.collection.count()
            print(f"✓ RAG Engine status: {count} chunks indexed")
            return True
        except:
            return False