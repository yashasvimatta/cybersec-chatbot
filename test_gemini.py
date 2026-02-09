"""
Quick Test Script for Gemini API
Run this to verify your Gemini API key works
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("🧪 Testing Gemini API Connection")
print("=" * 50)
print()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("   Please add your Gemini API key to .env:")
    print("   GEMINI_API_KEY=your-key-here")
    exit(1)

# Mask the key for display
masked_key = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else '***'
print(f"✅ API Key found: {masked_key}")
print()

# Test 1: Configure Gemini
print("📋 Test 1: Configuring Gemini")
print("-" * 50)

try:
    genai.configure(api_key=api_key)
    print("✅ Gemini configured successfully")
except Exception as e:
    print(f"❌ Configuration failed: {str(e)}")
    exit(1)

print()

# Test 2: Test Chat Model
print("📋 Test 2: Testing Chat Model (Gemini 2.0 Flash)")
print("-" * 50)

try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Say 'Hello! Gemini is working!' and nothing else.")
    print(f"✅ Chat response: {response.text}")
except Exception as e:
    print(f"❌ Chat test failed: {str(e)}")
    print()
    print("💡 Common issues:")
    print("   - Invalid API key")
    print("   - API key doesn't have access to Gemini 2.0 Flash")
    print("   - Network connectivity issues")
    exit(1)

print()

# Test 3: Test Embeddings
print("📋 Test 3: Testing Embeddings")
print("-" * 50)

try:
    result = genai.embed_content(
        model='models/text-embedding-004',
        content="This is a test for embeddings.",
        task_type="retrieval_document"
    )
    embedding_length = len(result['embedding'])
    print(f"✅ Embedding generated successfully")
    print(f"   Embedding dimensions: {embedding_length}")
except Exception as e:
    print(f"❌ Embedding test failed: {str(e)}")
    exit(1)

print()

# Final Summary
print("=" * 50)
print("✅ All Gemini API tests passed!")
print()
print("🎯 Your Gemini API is ready to use")
print()
print("Next steps:")
print("   1. Configure your .env file with Google Drive credentials")
print("   2. Run: python test_setup.py")
print("   3. Start the server: python main.py")
print()
