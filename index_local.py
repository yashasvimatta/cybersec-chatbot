#!/usr/bin/env python3
"""
Simple script to index your local knowledge base folder
Usage: python index_documents.py
"""

import requests
import json
import sys

def index_documents():
    """Index all documents from local folder"""
    
    print("🔄 Indexing documents from local folder (kb_raw)")
    print("This may take 10-30 minutes depending on the number and size of documents...")
    print()
    
    # API endpoint
    url = "http://localhost:8000/index"
    
    try:
        # Make request
        print("📡 Sending request to backend...")
        print("⏳ Waiting for Gemini API to generate embeddings (this is the slow part)...")
        print()
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={},  # Empty body since folder is configured in .env
            timeout=3600  # 1 hour timeout for large folders
        )
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print()
            print("=" * 60)
            print("✅ Success!")
            print("=" * 60)
            print(f"📊 Documents: {data.get('document_count', 'N/A')}")
            print(f"📊 Chunks indexed: {data.get('chunk_count', 'N/A')}")
            print(f"📁 Folder: {data.get('folder', 'N/A')}")
            print()
            print("🎉 Your knowledge base is ready!")
            print()
            print("Try querying:")
            print('  python query.py "What is our security policy?"')
            print()
            return True
        else:
            print()
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print()
        print("❌ Error: Could not connect to backend server")
        print()
        print("Make sure the server is running:")
        print("  python main_local.py")
        print()
        return False
    except requests.exceptions.Timeout:
        print()
        print("❌ Error: Request timed out")
        print("   Your folder might be too large.")
        print("   Try with fewer documents first.")
        print()
        return False
    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")
        print()
        return False

def main():
    """Main function"""
    
    # Check if server is running
    print("🔍 Checking if backend server is running...")
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code == 200:
            print("✅ Backend server is running")
            print()
        else:
            print("⚠️  Backend server responded but might have issues")
            print()
    except:
        print("❌ Backend server is not running!")
        print()
        print("Start it with:")
        print("  python main_local.py")
        print()
        sys.exit(1)
    
    # Index documents
    success = index_documents()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
