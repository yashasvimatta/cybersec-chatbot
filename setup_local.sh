#!/bin/bash

# ===========================================
# RAG Chatbot Quick Setup - LOCAL VERSION
# ===========================================

echo "🚀 RAG Chatbot System - Local Folder Setup"
echo "==========================================="
echo ""
echo "✨ This version works with LOCAL files"
echo "   NO Google Drive setup needed!"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo "📋 Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
echo ""

# Step 2: Install dependencies
echo "📋 Step 2: Installing Python packages..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet --upgrade
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All packages installed successfully${NC}"
else
    echo -e "${RED}❌ Package installation failed${NC}"
    echo "   Try running: pip install -r requirements.txt"
    exit 1
fi
echo ""

# Step 3: Setup .env file
echo "📋 Step 3: Configuring environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.local.template" ]; then
        cp .env.local.template .env
        echo -e "${GREEN}✅ Created .env from template${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file and add:${NC}"
        echo "   GEMINI_API_KEY=your-organization-gemini-key"
        echo ""
    else
        echo -e "${RED}❌ .env.local.template not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi
echo ""

# Step 4: Create knowledge base folder
echo "📋 Step 4: Setting up knowledge base folder..."
KB_FOLDER="kb_raw"

if [ ! -d "$KB_FOLDER" ]; then
    mkdir "$KB_FOLDER"
    echo -e "${GREEN}✅ Created folder: $KB_FOLDER${NC}"
else
    echo -e "${GREEN}✅ Folder already exists: $KB_FOLDER${NC}"
fi

# Check if there are files
FILE_COUNT=$(find "$KB_FOLDER" -type f ! -name ".*" | wc -l)
if [ "$FILE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No files found in $KB_FOLDER${NC}"
    echo ""
    echo "   Please add your cybersecurity documents:"
    echo "   - PDFs, Word docs, Excel files, etc."
    echo "   - Organize in subfolders if you like"
    echo ""
else
    echo -e "${GREEN}✅ Found $FILE_COUNT files in $KB_FOLDER${NC}"
fi
echo ""

# Step 5: Test Gemini API
echo "📋 Step 5: Testing Gemini API connection..."
if [ -f "test_gemini.py" ]; then
    echo "Running Gemini API test..."
    python test_gemini.py
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Gemini API test passed!${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  Please configure your GEMINI_API_KEY in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  test_gemini.py not found, skipping API test${NC}"
fi
echo ""

# Summary
echo "==========================================="
echo "🎉 Setup Complete!"
echo "==========================================="
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Configure your .env file:"
echo "   nano .env"
echo "   Add: GEMINI_API_KEY=your-key-here"
echo ""
echo "2. Add your documents to kb_raw/ folder:"
echo "   cp /path/to/your/docs/* kb_raw/"
echo ""
echo "3. Test your setup:"
echo "   python test_setup_local.py"
echo ""
echo "4. Start the server:"
echo "   python main_local.py"
echo ""
echo "5. Index your documents (in another terminal):"
echo "   python index_local.py"
echo ""
echo "6. Query your knowledge base:"
echo "   python query.py \"What is our security policy?\""
echo ""
echo "==========================================="
echo ""
echo -e "${GREEN}📚 Documentation:${NC}"
echo "   README_LOCAL.md - Complete setup guide"
echo "   CHEATSHEET.md - Quick reference"
echo ""
echo "==========================================="
echo ""

# Ask if user wants to start the server
read -p "Would you like to start the server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting backend server..."
    echo "   Press Ctrl+C to stop"
    echo ""
    python main_local.py
fi
