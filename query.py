#!/usr/bin/env python3
"""
Simple script to query your knowledge base
Usage: python query.py "Your question here"
"""

import sys
import requests
import json

def query_kb(question):
    """Query the knowledge base"""
    
    print(f"❓ Question: {question}")
    print()
    print("🔍 Searching knowledge base...")
    print()
    
    # API endpoint
    url = "http://localhost:8000/query"
    
    # Request payload
    payload = {
        "query": question
    }
    
    try:
        # Make request
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            
            # Print answer
            print("💡 Answer:")
            print("-" * 60)
            print(data['answer'])
            print("-" * 60)
            print()
            
            # Print sources
            if data['sources']:
                print("📚 Sources:")
                for i, source in enumerate(data['sources'], 1):
                    print(f"   {i}. {source['name']}")
                    print(f"      Path: {source['path']}")
                print()
            
            # Print confidence
            confidence_percent = int(data['confidence'] * 100)
            confidence_emoji = "🟢" if confidence_percent >= 80 else "🟡" if confidence_percent >= 60 else "🔴"
            print(f"🎯 Confidence: {confidence_emoji} {confidence_percent}%")
            print()
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server")
        print("   Make sure the server is running: python main.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    
    # Check if question provided
    if len(sys.argv) < 2:
        print("Usage: python query.py \"Your question here\"")
        print()
        print("Examples:")
        print('  python query.py "What is our password policy?"')
        print('  python query.py "How do I report a security incident?"')
        print('  python query.py "What are the indicators of APT29?"')
        print()
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    
    # Check if server is running
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code != 200:
            print("⚠️  Backend server responded but might have issues")
            print()
    except:
        print("❌ Backend server is not running!")
        print("   Start it with: python main.py")
        print()
        sys.exit(1)
    
    # Query
    success = query_kb(question)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
