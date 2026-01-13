import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Configuration
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';

if (!OPENAI_API_KEY || OPENAI_API_KEY === 'YOUR_API_KEY_HERE') {
  console.error('ERROR: Missing OPENAI_API_KEY in .env file');
  console.error('Get your API key from: https://platform.openai.com/api-keys');
  process.exit(1);
}

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
    model: OPENAI_MODEL,
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

    // Build messages array
    const messages = [];
    
    // Add system prompt on first message
    if (session.history.length === 0) {
      messages.push({ role: 'system', content: SYSTEM_PROMPT });
    }

    // Add conversation history
    messages.push(...session.history);

    // Add current message
    messages.push({ role: 'user', content: message });

    // Call OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: OPENAI_MODEL,
        messages,
        temperature: 0.3,
        max_tokens: 2000
      })
    });

    if (!response.ok) {
      const error = await response.json();
      console.error(' OpenAI API error:', error);
      return res.status(500).json({ 
        error: error?.error?.message || 'OpenAI API request failed' 
      });
    }

    const data = await response.json();
    const reply = data?.choices?.[0]?.message?.content || 'No response';

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
  console.log(` Model: ${OPENAI_MODEL}`);
  console.log(`\n Ready for connections!\n`);
});
