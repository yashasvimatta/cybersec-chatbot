# 🚀 SUPER QUICK START - Local Folder Version

## What You Have

You have a **folder with cybersecurity documents** (like you showed: IS Policies - ACTIVE).

This system will:
1. Read all those files
2. Create a searchable AI knowledge base
3. Answer questions about your documents

**NO Google Drive setup needed!**

---

## 3-Minute Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
```bash
# Create .env file
cp .env.local.template .env

# Edit it and add your Gemini API key
nano .env
```

Add this line:
```
GEMINI_API_KEY=your-key-here
```

Get free Gemini key: https://aistudio.google.com/app/apikey

### 3. Add Your Documents
```bash
# Create folder
mkdir kb_raw

# Copy YOUR documents to this folder
# The folder you showed me with all those PDFs!
cp -r "path/to/IS Policies - ACTIVE" kb_raw/
```

### 4. Run
```bash
# Terminal 1: Start server
python main_local.py

# Terminal 2: Index documents
python index_local.py

# Terminal 3: Query
python query.py "What is the AI Management Policy?"
```

---

## What's Happening

```
Your Documents (kb_raw/)
    ↓
Extract Text
    ↓
Create Embeddings (Gemini)
    ↓
Store in Vector DB (ChromaDB)
    ↓
Employee Asks Question
    ↓
Find Relevant Chunks (Similarity Search)
    ↓
Generate Answer (Gemini AI)
    ↓
Show Answer + Sources
```

---

## Files You Need

**Must have:**
- ✅ `main_local.py` - Server
- ✅ `local_file_handler.py` - Reads your files
- ✅ `rag_engine.py` - AI logic
- ✅ `requirements.txt` - Dependencies
- ✅ `.env` - Your API key (you create this)

**Helper scripts:**
- ✅ `test_setup_local.py` - Test setup
- ✅ `index_local.py` - Index documents
- ✅ `query.py` - Query from terminal

**Your documents:**
- ✅ `kb_raw/` - Put all your PDFs, Word docs, etc. here

---

## Example Commands

```bash
# Start server (keep running)
python main_local.py

# Index all documents in kb_raw/
python index_local.py

# Ask questions
python query.py "What is our incident response policy?"
python query.py "What are the password requirements?"
python query.py "How do I report a security incident?"
```

---

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "No documents found"
```bash
# Make sure you copied files to kb_raw/
ls kb_raw/

# If empty, copy your documents:
cp -r "your/documents/folder" kb_raw/
```

### "Gemini API error"
```bash
# Check your API key in .env
cat .env | grep GEMINI_API_KEY

# Test it
python test_gemini.py
```

### "Server won't start"
```bash
# Check if port 8000 is free
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Or use different port in .env:
PORT=8001
```

---

## Your Folder Structure Should Look Like:

```
your-project/
├── main_local.py
├── local_file_handler.py
├── rag_engine.py
├── requirements.txt
├── .env (you create this)
└── kb_raw/ (you create this)
    └── IS Policies - ACTIVE/
        ├── AI Management Policy.pdf
        ├── Asset Management Policy.pdf
        ├── Incident Management Policy.pdf
        └── ... (all your documents)
```

---

## Cost

**FREE** with Gemini's free tier!
- 15 requests/minute
- 1,500 requests/day

Perfect for small teams.

---

## Need More Help?

1. Run: `python test_setup_local.py`
2. Read: `README_LOCAL.md` (full guide)
3. Check: Server terminal for errors

---

## That's It!

You now have an AI that can answer questions about your cybersecurity documentation! 🎉

**Try it:**
```bash
python query.py "Summarize our security policies"
```
