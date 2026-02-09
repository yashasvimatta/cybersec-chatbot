#!/usr/bin/env python3
"""
Monitor script to track indexing progress
Run this in a separate terminal while index_local.py is running
"""

import requests
import time
import sys

def monitor_indexing():
    """Monitor the indexing progress by checking stats periodically"""
    
    print("🔍 Indexing Monitor")
    print("=" * 60)
    print("Checking knowledge base stats every 5 seconds...")
    print("Press Ctrl+C to stop")
    print()
    
    stats_url = "http://localhost:8000/stats"
    last_chunk_count = 0
    start_time = time.time()
    
    try:
        while True:
            try:
                response = requests.get(stats_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    chunk_count = data.get('indexed_chunks', 0)
                    elapsed = time.time() - start_time
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)
                    
                    chunks_per_minute = (chunk_count / elapsed) * 60 if elapsed > 0 else 0
                    
                    print(f"\r⏱  {minutes:02d}:{seconds:02d} | 📊 Chunks: {chunk_count:,} | "
                          f"Speed: {chunks_per_minute:.1f} chunks/min", end="", flush=True)
                    
                    if chunk_count > last_chunk_count:
                        last_chunk_count = chunk_count
                    
                else:
                    print(f"\r⚠️  Server returned status {response.status_code}", end="", flush=True)
            
            except requests.exceptions.ConnectionError:
                print(f"\r❌ Cannot connect to server at localhost:8000", end="", flush=True)
            except Exception as e:
                print(f"\r⚠️  Error: {str(e)}", end="", flush=True)
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")
        
        # Final stats
        try:
            response = requests.get(stats_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("\nFinal Statistics:")
                print(f"  Files: {data.get('files', {}).get('total', 'N/A')}")
                print(f"  Chunks indexed: {data.get('indexed_chunks', 'N/A'):,}")
                print(f"  Total size: {data.get('size_mb', 'N/A')} MB")
        except:
            pass

if __name__ == "__main__":
    monitor_indexing()
