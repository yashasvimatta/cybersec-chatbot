#!/bin/bash
# Start C&S Cybersecurity Chatbot - Python backend + React frontend
# Uses kb_raw + Gemini for RAG

cd "$(dirname "$0")"

echo "🚀 C&S Cybersecurity Chatbot"
echo "   Backend: Python FastAPI + RAG (kb_raw + Gemini)"
echo "   Frontend: React + Vite"
echo ""

# Ensure .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env not found. Create it with GEMINI_API_KEY and GOOGLE_CLOUD_PROJECT."
    exit 1
fi

# Start Python backend
echo "Starting backend (port 8000)..."
python main_local.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 4
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend may still be starting..."
fi

# Start frontend
echo "Starting frontend (port 5173)..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "📌 First time? Index your kb_raw documents:"
echo "   In a new terminal: python index_local.py"
echo ""
echo "   Then open http://localhost:5173 in your browser."
echo ""
echo "Press Ctrl+C to stop both servers."

wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
