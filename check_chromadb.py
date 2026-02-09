#!/usr/bin/env python3
"""
Diagnostic script to check ChromaDB contents
"""

import chromadb
from chromadb.config import Settings

print("=" * 70)
print("🔍 Checking ChromaDB Contents")
print("=" * 70)
print()

try:
    # Connect to ChromaDB
    client = chromadb.Client(Settings(
        anonymized_telemetry=False,
        allow_reset=True
    ))
    
    # Get collection
    collection = client.get_or_create_collection(
        name="knowledge_base",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Get count
    count = collection.count()
    print(f"📊 Total chunks in database: {count}")
    print()
    
    if count == 0:
        print("❌ Database is EMPTY!")
        print()
        print("This means indexing didn't save anything to ChromaDB.")
        print()
        print("Possible causes:")
        print("  1. Indexing failed silently")
        print("  2. ChromaDB path issue")
        print("  3. Different database instance")
        print()
        print("Solution:")
        print("  Re-index your documents:")
        print("  python index_local.py")
        print()
    else:
        print("✅ Database has content!")
        print()
        
        # Get a sample
        results = collection.get(limit=5, include=['documents', 'metadatas'])
        
        print("📄 Sample documents in database:")
        print("-" * 70)
        
        for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
            print(f"\n{i}. Source: {meta.get('source_name', 'Unknown')}")
            print(f"   Path: {meta.get('source_path', 'Unknown')}")
            print(f"   Preview: {doc[:150]}...")
        
        print()
        print("-" * 70)
        print()
        
        # Check unique sources
        all_results = collection.get(include=['metadatas'])
        sources = set()
        for meta in all_results['metadatas']:
            sources.add(meta.get('source_name', 'Unknown'))
        
        print(f"📚 Unique source documents: {len(sources)}")
        print()
        print("Documents indexed:")
        for source in sorted(sources):
            print(f"  - {source}")
    
    print()
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print()
    import traceback
    traceback.print_exc()

