"""
Test Script for RAG Chatbot System (Local Version)
Run this to verify your local setup is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🧪 RAG Chatbot System - Local Setup Test Suite")
print("=" * 60)
print()

# Test 1: Environment Variables
print("📋 Test 1: Environment Variables")
print("-" * 60)

required_vars = {
    'GEMINI_API_KEY': 'Gemini API key (for LLM and embeddings)',
}

optional_vars = {
    'KB_FOLDER': 'Knowledge base folder path',
    'LLM_PROVIDER': 'LLM provider choice',
    'EMBEDDING_PROVIDER': 'Embedding provider choice',
}

all_good = True

for var, description in required_vars.items():
    value = os.getenv(var)
    if value:
        # Mask the value if it's an API key
        if 'KEY' in var:
            masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
            print(f"✅ {var}: {masked}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: MISSING - {description}")
        all_good = False

print()
for var, description in optional_vars.items():
    value = os.getenv(var)
    if value:
        if 'KEY' in var:
            masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
            print(f"✅ {var}: {masked}")
        else:
            print(f"✅ {var}: {value}")
    else:
        default = "kb_raw" if var == "KB_FOLDER" else "gemini" if "PROVIDER" in var else "Not set"
        print(f"ℹ️  {var}: Using default ({default})")

print()

# Test 2: Knowledge Base Folder
print("📋 Test 2: Knowledge Base Folder")
print("-" * 60)

kb_folder = os.getenv('KB_FOLDER', 'kb_raw')

if os.path.exists(kb_folder):
    print(f"✅ Folder exists: {kb_folder}")
    
    # Count files
    file_count = 0
    folder_count = 0
    file_types = {}
    
    for root, dirs, files in os.walk(kb_folder):
        folder_count += len(dirs)
        for file in files:
            if not file.startswith('.'):
                file_count += 1
                ext = os.path.splitext(file)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
    
    print(f"   📊 Statistics:")
    print(f"      Files: {file_count}")
    print(f"      Folders: {folder_count}")
    if file_types:
        print(f"      File types: {dict(file_types)}")
    
    if file_count == 0:
        print(f"\n   ⚠️  No files found in {kb_folder}")
        print(f"      Add your cybersecurity documents to this folder!")
        all_good = False
    else:
        print(f"   ✅ Found {file_count} files ready to index")
else:
    print(f"❌ Folder not found: {kb_folder}")
    print(f"   Creating folder...")
    try:
        os.makedirs(kb_folder)
        print(f"   ✅ Created: {kb_folder}")
        print(f"   ⚠️  Add your documents to this folder before indexing")
    except Exception as e:
        print(f"   ❌ Failed to create folder: {e}")
        all_good = False

print()

# Test 3: Python Dependencies
print("📋 Test 3: Python Dependencies")
print("-" * 60)

required_packages = [
    'fastapi',
    'chromadb',
    'pandas',
    'PyPDF2',
    'docx',
    'pptx',
    'openpyxl',
]

for package in required_packages:
    try:
        if package == 'docx':
            __import__('docx')
        elif package == 'pptx':
            __import__('pptx')
        else:
            __import__(package)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - Run: pip install -r requirements.txt")
        all_good = False

print()

# Test 4: Gemini API Connection
print("📋 Test 4: Gemini API Connection")
print("-" * 60)

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured")
        print("   (Full test requires API call - skipped to save costs)")
        print("   Run: python test_gemini.py for full test")
    else:
        print("❌ GEMINI_API_KEY not set")
        all_good = False
except ImportError:
    print("❌ google-generativeai not installed")
    print("   Run: pip install -r requirements.txt")
    all_good = False
except Exception as e:
    print(f"❌ Gemini API error: {str(e)}")
    all_good = False

print()

# Test 5: Local File Handler
print("📋 Test 5: Local File Handler")
print("-" * 60)

try:
    from local_file_handler import LocalFileHandler
    handler = LocalFileHandler(kb_folder)
    
    if handler.check_connection():
        print("✅ Local file handler initialized")
        
        stats = handler.get_folder_stats()
        print(f"   Files: {stats['total_files']}")
        print(f"   Folders: {stats['total_folders']}")
        print(f"   Size: {stats['total_size_mb']:.2f} MB")
    else:
        print("❌ Folder not accessible")
        all_good = False
except Exception as e:
    print(f"❌ Local file handler error: {str(e)}")
    all_good = False

print()

# Test 6: RAG Engine
print("📋 Test 6: RAG Engine")
print("-" * 60)

try:
    from rag_engine import RAGEngine
    engine = RAGEngine()
    
    if engine.check_status():
        print("✅ RAG Engine initialized")
        print(f"   LLM Provider: {engine.provider}")
        print(f"   Embedding Provider: {engine.embedding_provider}")
    else:
        print("⚠️  RAG Engine initialized but may have issues")
except Exception as e:
    print(f"❌ RAG Engine error: {str(e)}")
    all_good = False

print()

# Final Summary
print("=" * 60)
if all_good:
    print("✅ All tests passed! Your setup is ready.")
    print()
    print("🚀 Next steps:")
    print("   1. Add your cybersecurity documents to:")
    print(f"      {kb_folder}/")
    print("      (PDFs, Word docs, Excel, PowerPoint, etc.)")
    print()
    print("   2. Start the server:")
    print("      python main_local.py")
    print()
    print("   3. Index your documents:")
    print("      python index_documents.py")
    print()
    print("   4. Test a query:")
    print('      python query.py "What is our security policy?"')
else:
    print("❌ Some tests failed. Please fix the issues above.")
    print()
    print("💡 Common fixes:")
    print("   - Create/edit .env file with your GEMINI_API_KEY")
    print("   - Add documents to kb_raw folder")
    print("   - Run: pip install -r requirements.txt")

print()
