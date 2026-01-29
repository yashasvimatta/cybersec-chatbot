import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { GoogleGenAI } from '@google/genai';
import { buildRagContext, getRagStatus, initRag } from './knowledge/rag.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Configuration
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-3-flash-preview';

if (!GEMINI_API_KEY || GEMINI_API_KEY === 'YOUR_API_KEY_HERE') {
  console.error('ERROR: Missing GEMINI_API_KEY in .env file');
  console.error('Get your API key from: https://aistudio.google.com/apikey');
  process.exit(1);
}

// Initialize Gemini AI
const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

// Start knowledge base sync (Drive → local index) if configured
initRag({ ai }).catch((e) => console.error('📚 initRag error:', e));

const SYSTEM_PROMPT = `You are a cybersecurity assistant for C&S Wholesale Groceries.

Rules:
- Provide defensive, ethical, and legal guidance only
- Refuse requests that enable wrongdoing (phishing, malware, exploitation)
- Focus on risk, impact, and mitigation
- Be concise but comprehensive
- Use clear formatting with sections when appropriate

Always respond in this format when applicable:

Answer:
Risk/Impact:
Recommended Actions:
Questions to Confirm:`;

// In-memory session storage
const conversations = new Map();

// Cleanup old sessions (2 hours)
setInterval(() => {
  const twoHoursAgo = Date.now() - 2 * 60 * 60 * 1000;
  for (const [sessionId, data] of conversations.entries()) {
    if (data.lastActivity < twoHoursAgo) {
      console.log(`🗑️  Cleaning up session: ${sessionId}`);
      conversations.delete(sessionId);
    }
  }
}, 30 * 60 * 1000);

// Routes
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    activeSessions: conversations.size,
    model: GEMINI_MODEL,
    rag: getRagStatus(),
    timestamp: new Date().toISOString()
  });
});

app.post('/chat', async (req, res) => {
  try {
    const { message, sessionId } = req.body;

    if (!message || !sessionId) {
      return res.status(400).json({ error: 'Missing message or sessionId' });
    }

    console.log(` [${sessionId.substring(0, 8)}...] ${message.substring(0, 50)}...`);

    // Get or create session
    if (!conversations.has(sessionId)) {
      console.log(` New session: ${sessionId}`);
      conversations.set(sessionId, {
        history: [],
        lastActivity: Date.now()
      });
    }

    const session = conversations.get(sessionId);
    session.lastActivity = Date.now();

    const { context } = await buildRagContext({ ai, queryText: message });

    // Build contents array for Gemini API
    const contents = [];
    
    // Add system prompt on first message by including it in the first user message
    if (session.history.length === 0) {
      const firstText = context
        ? `${SYSTEM_PROMPT}\n\n${context}\n\nUser question:\n${message}`
        : `${SYSTEM_PROMPT}\n\n${message}`;
      contents.push({
        role: 'user',
        parts: [{ text: firstText }]
      });
    } else {
      // Convert conversation history to Gemini format
      for (const msg of session.history) {
        contents.push({
          role: msg.role === 'user' ? 'user' : 'model',
          parts: [{ text: msg.content }]
        });
      }
      // Add current message
      const msgText = context ? `${context}\n\nUser question:\n${message}` : message;
      contents.push({
        role: 'user',
        parts: [{ text: msgText }]
      });
    }

    // Call Gemini API
    try {
      const response = await ai.models.generateContent({
        model: GEMINI_MODEL,
        contents: contents
      });

      const reply = response.text || 'No response';

      // Update conversation history
      session.history.push(
        { role: 'user', content: message },
        { role: 'assistant', content: reply }
      );

      // Keep last 20 messages (10 exchanges)
      if (session.history.length > 20) {
        session.history = session.history.slice(-20);
      }

      console.log(` Response sent (${session.history.length / 2} exchanges)`);

      res.json({
        reply,
        conversationLength: session.history.length / 2
      });
    } catch (error) {
      console.error(' Gemini API error:', error);
      return res.status(500).json({ 
        error: error?.message || 'Gemini API request failed' 
      });
    }

  } catch (error) {
    console.error(' Server error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/reset', (req, res) => {
  try {
    const { sessionId } = req.body;

    if (!sessionId) {
      return res.status(400).json({ error: 'Missing sessionId' });
    }

    conversations.delete(sessionId);
    console.log(` Reset session: ${sessionId}`);

    res.json({ success: true, message: 'Conversation reset' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n C&S Chat Backend Started`);
  console.log(` Server: http://localhost:${PORT}`);
  console.log(` Health: http://localhost:${PORT}/health`);
  console.log(` Model: ${GEMINI_MODEL}`);
  console.log(` Provider: Google Gemini`);
  console.log(`\n Ready for connections!\n`);
});
