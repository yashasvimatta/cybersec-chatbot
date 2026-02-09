# Quick Start Guide - Updated Setup

## Your RAG system is now configured! 🚀

### Step 1: Stop any running servers
If you have the backend server running, press **Ctrl+C** to stop it.

### Step 2: Re-index your documents (with new model detection)
```bash
python index_local.py
```

This will:
- ✅ Auto-detect the best available Gemini embedding model
- ✅ Auto-detect the best available Gemini LLM model  
- ✅ Index all documents from `kb_raw/` folder
- ✅ Save embeddings to ChromaDB

**Expected output:**
```
✓ Using Google Gemini (gemini-1.5-flash)
✓ Using Gemini embeddings (models/text-embedding-004)
✓ RAG Engine initialized (LLM: gemini)

📚 Starting indexing of 29 documents...
[1/29] 📄 Document Name
    ↳ Indexing: X/Y chunks ✓
...
✓ Indexing complete: XXXX chunks from 29 documents
```

### Step 3: Start the backend server
```bash
python main_local.py
```

You should see:
```
✓ Using Google Gemini (gemini-1.5-flash)
✓ Using Gemini embeddings (models/text-embedding-004)
✓ RAG Engine initialized (LLM: gemini)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Query your knowledge base (in a new terminal)
```bash
python query.py "What is our security policy?"
```

Or try other questions:
```bash
python query.py "What are the incident response procedures?"
python query.py "Tell me about access management policies"
python query.py "What is in the data classification policy?"
```

## Troubleshooting

### Issue: "Model not found" errors
- The system now **auto-detects available models**
- If all models fail, it falls back to `gemini-pro`
- Check your GEMINI_API_KEY in `.env`

### Issue: Empty database
- Re-run `python index_local.py`
- Make sure documents are in the `kb_raw/` folder
- Check for error messages during indexing

### Issue: Slow indexing
- This is normal! Large documents take time to embed
- Each chunk needs an API call to Gemini
- The system uses automatic retry with exponential backoff
- Just let it run - can take 10-30 minutes for large folders

## Files Modified
- ✅ `rag_engine.py` - Smart model detection
- ✅ `requirements.txt` - Added tqdm for progress
- All changes are backward compatible!

Happy querying! 🎉
