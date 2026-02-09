#!/usr/bin/env python3
"""
Debug script to check what's being retrieved from ChromaDB
"""

from rag_engine import RAGEngine

engine = RAGEngine()

# Test queries
queries = [
    "Who invented the internet?",
    "What is the incident response procedure?",
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    # Get query embedding
    query_embedding = engine._get_embedding(query)
    
    # Raw search with no threshold
    results = engine.collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    
    print(f"\nTop 5 raw results (no threshold):")
    if results['documents'] and results['documents'][0]:
        for i in range(len(results['documents'][0])):
            distance = results['distances'][0][i]
            similarity = max(0, 1 - distance)
            source = results['metadatas'][0][i].get('source_name', 'Unknown')
            preview = results['documents'][0][i][:60].replace('\n', ' ')
            print(f"\n  [{i+1}] Source: {source}")
            print(f"      Distance: {distance:.4f}")
            print(f"      Similarity: {similarity:.4f} (threshold=0.3: {'PASS' if similarity >= 0.3 else 'FAIL'})")
            print(f"      Preview: {preview}...")
    
    # Now test with retrieve_relevant_docs
    print(f"\nUsing retrieve_relevant_docs (threshold=0.3):")
    relevant = engine.retrieve_relevant_docs(query, top_k=5, similarity_threshold=0.3)
    print(f"  Found {len(relevant)} relevant documents")
    for i, doc in enumerate(relevant, 1):
        source = doc['metadata'].get('source_name', 'Unknown')
        similarity = doc.get('similarity', 0)
        print(f"  [{i}] {source} (similarity: {similarity:.4f})")

