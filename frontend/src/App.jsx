import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import Header from "./components/Header.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import ChatInput from "./components/ChatInput.jsx";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [status, setStatus] = useState("Connected");

  const sessionId = useMemo(
    () => `session_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`,
    []
  );

  // Python backend (FastAPI + RAG with kb_raw + Gemini)
  const API_BASE = "http://localhost:8000";

  const checkHealth = async () => {
    try {
      await axios.get(`${API_BASE}/health`);
      setStatus("Connected");
    } catch (error) {
      setStatus("Backend offline");
      console.error("Health check failed:", error);
    }
  };

  useEffect(() => {
    checkHealth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = async (overrideText) => {
    const message = (overrideText ?? inputMessage).trim();
    if (!message || isTyping) return;

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: "user",
        text: message,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);

    setInputMessage("");
    setIsTyping(true);
    setStatus("Thinking...");

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message,
        sessionId,
      });

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "bot",
          text: response.data.reply || "No reply",
          timestamp: new Date().toLocaleTimeString(),
          sources: response.data.sources || [],
        },
      ]);

      setStatus("Connected");
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "error",
          text: `Error: ${error.response?.data?.error || error.message}`,
        },
      ]);
      setStatus("Connection failed");
      console.error("Error:", error);
    } finally {
      setIsTyping(false);
    }
  };

  const indexKnowledgeBase = async () => {
    setStatus("Indexing...");
    try {
      const res = await axios.post(`${API_BASE}/index`, {});
      setStatus(`Indexed ${res.data.chunk_count} chunks from ${res.data.document_count} docs`);
      setTimeout(() => setStatus("Connected"), 4000);
    } catch (error) {
      setStatus("Index failed");
      console.error(error);
      setTimeout(() => setStatus("Connected"), 3000);
    }
  };

  const resetChat = async () => {
    // Keep simple confirm
    if (!confirm("Are you sure you want to reset the conversation?")) return;

    try {
      await axios.post(`${API_BASE}/reset`, { sessionId });
      setMessages([]);
      setStatus("Reset successful");
      setTimeout(() => setStatus("Connected"), 2000);
    } catch (error) {
      console.error("Reset error:", error);
      setStatus("Reset failed");
    }
  };

  return (
    <div className="app-container">
      <Header status={status} onReset={resetChat} onIndexKB={indexKnowledgeBase} />

      <div className="container">
        <ChatWindow
          messages={messages}
          isTyping={isTyping}
          onSendSuggestion={(text) => sendMessage(text)}
        />

        <ChatInput
          value={inputMessage}
          disabled={isTyping}
          onChange={setInputMessage}
          onSend={() => sendMessage()}
        />

        <div className="hint">
          Searches your kb_raw folder + Gemini. Index docs first if needed.
        </div>
      </div>
    </div>
  );
}

