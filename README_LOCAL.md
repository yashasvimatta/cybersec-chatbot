# Cybersecurity RAG Chatbot - LOCAL FOLDER Setup

## 🎯 Overview

This is a simplified version that works with **local files** instead of Google Drive. Perfect for when you don't have Google Cloud access!

**What it does:**
- Reads documents from a local folder (`kb_raw`)
- Creates a vector database for fast similarity search
- Answers employee questions using Google Gemini AI
- Provides source citations for all answers

**No Google Drive setup needed!** Just drop your files in a folder.

---

## 📋 Prerequisites

✅ **Python 3.9 or higher**
✅ **Your organization's Gemini API key**
✅ **Your cybersecurity documents (PDF, Word, Excel, PowerPoint, etc.)**

❌ **NO Google Cloud setup needed**
❌ **NO service account needed**
❌ **NO Drive API configuration**

---

## 🚀 Quick Start (3 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key

Create a `.env` file:
```bash
cp .env.local.template .env
```

Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your-gemini-api-key-here
KB_FOLDER=kb_raw
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
```

**Get your Gemini API key:**
- Free: https://aistudio.google.com/app/apikey
- Or use your organization's Gemini API key

### 3. Add Your Documents

Create the knowledge base folder and add your documents:
```bash
# The folder will be created automatically, but you can create it manually:
mkdir kb_raw

# Copy your cybersecurity documents to this folder
# You can organize them in subfolders too!
```

**Example structure:**
```
kb_raw/
├── IS Policies - ACTIVE/
│   ├── AI Management Policy.pdf
│   ├── Asset Management Policy.pdf
│   ├── Incident Management Policy.pdf
│   └── ... (all your policies)
├── Procedures/
│   └── ... (your procedures)
└── Training/
    └── ... (training materials)
```

**Supported file types:**
- ✅ PDF (.pdf)
- ✅ Word (.docx, .doc)
- ✅ Excel (.xlsx, .xls)
- ✅ PowerPoint (.pptx, .ppt)
- ✅ CSV (.csv)
- ✅ Text (.txt, .md)

### 4. Test Your Setup

```bash
python test_setup_local.py
```

You should see all ✅ checkmarks.

### 5. Start the Server

```bash
python main_local.py
```

You should see:
```
✓ Found knowledge base folder: kb_raw
✓ Using Google Gemini
✓ Gemini embeddings
✓ RAG Engine initialized (LLM: gemini)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal running!**

### 6. Index Your Documents

In a **new terminal**:
```bash
python index_local.py
```

This will:
- Scan all files in `kb_raw/`
- Extract text from PDFs, Word docs, etc.
- Create embeddings with Gemini
- Store in vector database

**Takes 5-15 minutes** depending on how many documents you have.

### 7. Query Your Knowledge Base

```bash
python query.py "What is our incident response procedure?"
```

---

## 📂 Organizing Your Knowledge Base

### Recommended Folder Structure

```
kb_raw/
├── 📁 Policies/
│   ├── Security_Policy_2024.pdf
│   ├── Incident_Response_Plan.pdf
│   ├── Data_Classification.xlsx
│   └── Acceptable_Use_Policy.docx
│
├── 📁 Threat_Intelligence/
│   ├── APT_Reports/
│   │   ├── APT29_Analysis.pdf
│   │   └── APT28_TTPs.docx
│   ├── IOCs/
│   │   └── IOC_Database.csv
│   └── Vulnerability_Reports/
│
├── 📁 Compliance/
│   ├── GDPR_Guide.pdf
│   ├── NIST_Framework.xlsx
│   └── SOC2_Requirements.docx
│
├── 📁 Procedures/
│   ├── Runbooks/
│   └── Playbooks/
│
└── 📁 Training/
    └── Security_Awareness/
```

### Tips for Better Results

✅ **DO:**
- Use descriptive file names
- Organize in logical folders
- Keep documents up to date
- Remove outdated content

❌ **DON'T:**
- Use unclear abbreviations
- Mix unrelated content
- Duplicate files
- Store large non-text files (videos, etc.)

---

## 💬 Using the Chatbot

### Example Queries

**Policy Questions:**
```bash
python query.py "What is our password policy?"
python query.py "What's the data classification scheme?"
python query.py "Who approves security exceptions?"
```

**Incident Response:**
```bash
python query.py "How do I report a security incident?"
python query.py "What's the ransomware response procedure?"
python query.py "Who is on the incident response team?"
```

**Threat Intelligence:**
```bash
python query.py "What do we know about APT29?"
python query.py "Latest phishing techniques we've seen"
python query.py "Current threat indicators"
```

**Compliance:**
```bash
python query.py "What are our GDPR requirements?"
python query.py "SOC 2 controls checklist"
python query.py "NIST framework implementation"
```

**Technical Procedures:**
```bash
python query.py "How do I configure MFA?"
python query.py "Steps for secure remote access"
python query.py "Vulnerability management process"
```

---

## 🔄 Updating Your Knowledge Base

### When You Add/Change Documents

**Option 1: Manual Refresh**
```bash
# Re-index everything
curl -X POST http://localhost:8000/refresh
```

**Option 2: Using Script**
```bash
python index_local.py
```

**When to refresh:**
- ✅ Added new documents
- ✅ Updated existing documents
- ✅ Removed old documents
- ✅ Reorganized folder structure

---

## 📊 API Endpoints

### GET /
Get API info and knowledge base statistics
```bash
curl http://localhost:8000/
```

### POST /index
Index all documents from local folder
```bash
curl -X POST http://localhost:8000/index
```

### POST /query
Query the knowledge base
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is our security policy?"}'
```

### POST /refresh
Refresh the entire index
```bash
curl -X POST http://localhost:8000/refresh
```

### GET /health
Check system health
```bash
curl http://localhost:8000/health
```

### GET /stats
Get knowledge base statistics
```bash
curl http://localhost:8000/stats
```

---

## 💰 Cost Breakdown (Gemini)

### Free Tier (Perfect for Testing!)
- **15 requests per minute**
- **1,500 requests per day**
- **Cost: $0.00**

### Typical Usage (500 documents, 100 employees)

**Initial Indexing:**
- 500 documents
- ~1M tokens for embeddings
- **Cost: FREE** (within free tier)
- **Time: 10-15 minutes**

**Monthly Queries:**
- 100 employees × 10 queries/day = 1,000 queries/day
- 30,000 queries/month
- **Cost: FREE** (within free tier)

**If you exceed free tier:**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- 30M tokens/month ≈ **$2-3/month**

---

## 🔧 Configuration Options

### Change Knowledge Base Folder

Edit `.env`:
```env
KB_FOLDER=my_custom_folder
```

### Change Server Port

Edit `.env`:
```env
PORT=8001
```

Then access at: http://localhost:8001

### Use Different LLM

Edit `.env`:
```env
# For Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# For OpenAI GPT-4
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
EMBEDDING_PROVIDER=openai
```

---

## 🐛 Troubleshooting

### "No documents found"
```bash
# Check if folder exists
ls kb_raw/

# Check if files are there
ls -la kb_raw/

# Add some documents!
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### "Gemini API error"
```bash
# Test your API key
python test_gemini.py

# Check .env file
cat .env | grep GEMINI_API_KEY
```

### "Port already in use"
```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Or change port in .env
PORT=8001
```

### "Cannot extract text from PDF"
```bash
# Install required packages
pip install PyPDF2 --upgrade

# Some PDFs are scanned images - need OCR
# For now, skip those or convert to text first
```

### "ChromaDB errors"
```bash
# Delete and recreate database
rm -rf chroma_db/

# Restart server and re-index
python main_local.py
python index_local.py
```

---

## 🔒 Security Considerations

### Current Security

✅ **All data stays local** - Never leaves your machine
✅ **No cloud dependencies** - Works offline
✅ **API keys in .env** - Not in code
✅ **Read-only access** - System only reads files

### For Production Deployment

Add these security measures:

1. **Authentication**
   ```python
   # Add to main_local.py
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   @app.post("/query")
   async def query(request: QueryRequest, credentials = Depends(security)):
       # Verify token
       pass
   ```

2. **Rate Limiting**
   ```bash
   pip install slowapi
   ```

3. **Access Logging**
   ```python
   import logging
   
   logging.basicConfig(
       filename='access.log',
       format='%(asctime)s - %(message)s'
   )
   ```

4. **HTTPS**
   - Use nginx with SSL certificate
   - Deploy behind VPN for internal use

5. **File Access Control**
   - Restrict who can add/modify files in kb_raw
   - Regular security audits of indexed content

---

## 📈 Performance Tips

### For Faster Indexing

1. **Remove unnecessary files**
   ```bash
   # Remove backups, duplicates
   find kb_raw -name "*.bak" -delete
   ```

2. **Optimize PDFs**
   - Ensure PDFs are text-based (not scanned images)
   - Use PDF optimization tools

3. **Batch processing**
   - Index in smaller batches if folder is huge
   - Use subfolders to organize

### For Better Answers

1. **Use specific questions**
   - ✅ "What is the password policy for privileged accounts?"
   - ❌ "Tell me about passwords"

2. **Reference document names when known**
   - "According to the Incident Response Plan, what are the steps?"

3. **Check confidence scores**
   - Low confidence (<60%)? Try rephrasing

4. **Review sources**
   - Always verify the information from sources

---

## 🚀 Production Deployment Options

### Option 1: Local Server (Simplest)

Keep running on your local machine:
```bash
# Use systemd (Linux) or screen (any Unix)
screen -S chatbot
python main_local.py
# Press Ctrl+A, then D to detach
```

### Option 2: Internal Server

Deploy on internal company server:
```bash
# Copy all files to server
scp -r * user@server:/path/to/chatbot/

# SSH to server
ssh user@server

# Run server
cd /path/to/chatbot
python main_local.py
```

### Option 3: Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy your kb_raw folder
COPY kb_raw/ kb_raw/

CMD ["python", "main_local.py"]
```

Deploy:
```bash
docker build -t cybersec-chatbot .
docker run -p 8000:8000 --env-file .env cybersec-chatbot
```

### Option 4: Cloud Deployment (if allowed)

**Railway:**
```bash
railway login
railway init
railway up
```

**Render:**
- Push to GitHub
- Connect repository
- Deploy

---

## 📊 Monitoring

### Check System Status

```bash
# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats
```

### Monitor Logs

```bash
# Server logs (in terminal running main_local.py)
# Look for errors, slow queries, etc.

# Add detailed logging if needed:
# Edit main_local.py and add: logging.basicConfig(level=logging.DEBUG)
```

### Track Usage

Create a simple analytics endpoint:
```python
# Add to main_local.py

query_count = 0

@app.post("/query")
async def query_knowledge_base(request: QueryRequest):
    global query_count
    query_count += 1
    # ... rest of code

@app.get("/analytics")
async def analytics():
    return {"total_queries": query_count}
```

---

## 🎓 Advanced Features

### Custom Chunk Size

Edit `rag_engine.py`:
```python
# For longer context (more accurate but slower)
self.text_splitter = SimpleTextSplitter(
    chunk_size=2000,  # Default: 1000
    chunk_overlap=400  # Default: 200
)

# For faster queries (less context)
self.text_splitter = SimpleTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
```

### Filter by Subfolder

Query specific subfolders only:
```python
# Query only policies folder
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the password policy?", "folder_path":"Policies"}'
```

### Conversation Memory (Future Enhancement)

Track chat history for context-aware responses:
```python
# Store conversation in database
# Reference previous questions/answers
# Provide more coherent multi-turn conversations
```

---

## 📞 Support & Help

### Quick Diagnostics

```bash
# 1. Test setup
python test_setup_local.py

# 2. Check server is running
curl http://localhost:8000/health

# 3. Check files are accessible
python -c "from local_file_handler import LocalFileHandler; h=LocalFileHandler(); print(h.get_folder_stats())"

# 4. Test Gemini API
python test_gemini.py
```

### Common Issues Checklist

- [ ] .env file exists with GEMINI_API_KEY
- [ ] kb_raw folder exists with documents
- [ ] All dependencies installed (pip install -r requirements.txt)
- [ ] Server is running (python main_local.py)
- [ ] Documents are indexed (python index_local.py)

---

## 🎉 You're Ready!

### Quick Start Commands

```bash
# 1. One-time setup
pip install -r requirements.txt
cp .env.local.template .env
# Edit .env with your GEMINI_API_KEY

# 2. Add documents
# Copy files to kb_raw/ folder

# 3. Start server
python main_local.py

# 4. Index (in another terminal)
python index_local.py

# 5. Query
python query.py "What is our security policy?"
```

---

## 📚 File Overview

**Core Files:**
- `main_local.py` - FastAPI server (local version)
- `local_file_handler.py` - Reads local files
- `rag_engine.py` - Vector DB + AI logic
- `requirements.txt` - Python dependencies

**Helper Scripts:**
- `test_setup_local.py` - Test your setup
- `test_gemini.py` - Test Gemini API
- `index_local.py` - Index documents
- `query.py` - Query from terminal

**Configuration:**
- `.env` - Your API keys (create this)
- `.env.local.template` - Template for .env

**Knowledge Base:**
- `kb_raw/` - Put your documents here

---

## 🌟 Next Steps

1. ✅ **Index your documents** - Run `python index_local.py`
2. ✅ **Test queries** - Try some example questions
3. ✅ **Integrate frontend** - Add React chatbot if needed
4. ✅ **Deploy** - Move to server for team access
5. ✅ **Monitor** - Track usage and improve

Your cybersecurity knowledge base is now AI-powered! 🚀
