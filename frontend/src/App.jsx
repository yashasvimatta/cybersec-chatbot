import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import Sidebar from "./components/Sidebar.jsx";
import Header from "./components/Header.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import ChatInput from "./components/ChatInput.jsx";
import IncidentReport from "./components/IncidentReport.jsx";
import SecurityChecklist from "./components/SecurityChecklist.jsx";
import AnalyticsDashboard from "./components/AnalyticsDashboard.jsx";

function getInitialTheme() {
  try {
    const saved = localStorage.getItem("fiona-theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch {}
  return "dark";
}

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme);
  const [persona, setPersona] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [status, setStatus] = useState("Connected");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Modal states
  const [showIncidentReport, setShowIncidentReport] = useState(false);
  const [showChecklists, setShowChecklists] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Tip of the day
  const [tip, setTip] = useState(null);
  const [tipDismissed, setTipDismissed] = useState(false);

  // Popular questions
  const [popularQuestions, setPopularQuestions] = useState([]);

  // Keep <html> data-theme in sync
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("fiona-theme", theme); } catch {}
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  const sessionId = useMemo(
    () => `session_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`,
    []
  );

  const API_BASE = "http://localhost:8000";

  // Health check
  const checkHealth = async () => {
    try {
      await axios.get(`${API_BASE}/health`);
      setStatus("Connected");
    } catch {
      setStatus("Backend offline");
    }
  };

  // Initial health check
  useEffect(() => {
    checkHealth();
  }, []);

  // Load tip of the day + popular questions on persona set
  useEffect(() => {
    if (!persona) return;

    // Tip
    axios
      .get(`${API_BASE}/tip`, { params: { department: persona.department } })
      .then((res) => setTip(res.data))
      .catch(() => {});

    // Popular questions
    axios
      .get(`${API_BASE}/analytics/popular`, { params: { department: persona.department, limit: 5 } })
      .then((res) => setPopularQuestions(res.data.questions || []))
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [persona]);

  // ── Send message ──────────────────────────────────────

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
        department: persona?.department,
        role: persona?.role,
      });

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "bot",
          text: response.data.reply || "No reply",
          timestamp: new Date().toLocaleTimeString(),
          sources: response.data.sources || [],
          confidence: response.data.confidence,
          followUps: response.data.followUps || [],
        },
      ]);

      setStatus("Connected");
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "error",
          text: `Error: ${error.response?.data?.detail || error.response?.data?.error || error.message}`,
        },
      ]);
      setStatus("Connection failed");
    } finally {
      setIsTyping(false);
    }
  };


  // ── Reset ─────────────────────────────────────────────

  const resetChat = async () => {
    if (!confirm("Are you sure you want to reset the conversation?")) return;
    try {
      await axios.post(`${API_BASE}/reset`, { sessionId });
      setMessages([]);
      setStatus("Reset successful");
      setTimeout(() => setStatus("Connected"), 2000);
    } catch {
      setStatus("Reset failed");
    }
  };

  // ── Persona change from sidebar ─────────────────────────

  const handlePersonaChange = (newPersona) => {
    setPersona(newPersona);
    setMessages([]);
    setTip(null);
    setTipDismissed(false);
  };

  // ── Feedback handler ──────────────────────────────────

  const handleFeedback = async (msg, rating) => {
    try {
      // Find the user query that preceded this bot message
      const idx = messages.findIndex((m) => m.id === msg.id);
      const userMsg = idx > 0 ? messages[idx - 1] : null;

      await axios.post(`${API_BASE}/feedback`, {
        sessionId,
        messageId: String(msg.id),
        query: userMsg?.text || "",
        answer: msg.text,
        rating,
        department: persona?.department,
        role: persona?.role,
      });
    } catch {
      // Silently fail — don't interrupt UX
    }
  };

  // ── Escalation handler ────────────────────────────────

  const handleEscalate = async (msg) => {
    try {
      const idx = messages.findIndex((m) => m.id === msg.id);
      const userMsg = idx > 0 ? messages[idx - 1] : null;

      const res = await axios.post(`${API_BASE}/escalate`, {
        sessionId,
        query: userMsg?.text || msg.text,
        conversationContext: messages
          .slice(Math.max(0, idx - 4), idx + 1)
          .map((m) => `${m.type}: ${m.text}`)
          .join("\n"),
        department: persona?.department,
        role: persona?.role,
      });

      // Add a system message showing escalation confirmation
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: "bot",
          text: `Your question has been escalated to the Cybersecurity Team.\n\n**Reference:** ${res.data.reference}\n\nThe team will review your conversation context and follow up. You can continue chatting in the meantime.`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: "error",
          text: "Failed to escalate. Please contact the IT Service Desk directly.",
        },
      ]);
    }
  };

  // ── Incident report handler ───────────────────────────

  const handleIncidentSubmit = async ({ incidentType, description, urgency, senderEmail }) => {
    const res = await axios.post(`${API_BASE}/incident`, {
      sessionId,
      department: persona?.department,
      role: persona?.role,
      incidentType,
      description,
      urgency,
      senderEmail,
    });
    return res.data;
  };

  return (
    <div className="app-layout">
      <Sidebar
        persona={persona}
        onPersonaChange={handlePersonaChange}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((c) => !c)}
      />

      <div className="app-main">
        <Header
          status={status}
          onReset={resetChat}
          persona={persona}
          theme={theme}
          onToggleTheme={toggleTheme}
          onReportIncident={() => setShowIncidentReport(true)}
          onOpenChecklists={() => setShowChecklists(true)}
          onOpenAnalytics={() => setShowAnalytics(true)}
        />

        <div className="container">
          {!persona ? (
            <div className="chat-window">
              <div className="welcome-pick-dept">
                <div className="welcome-pick-icon">&#9664;</div>
                <h2>Welcome to Fiona</h2>
                <p>Select your department and role from the sidebar to get started with personalized cybersecurity assistance.</p>
              </div>
            </div>
          ) : (
            <ChatWindow
              messages={messages}
              isTyping={isTyping}
              onSendSuggestion={(text) => sendMessage(text)}
              persona={persona}
              onFeedback={handleFeedback}
              onEscalate={handleEscalate}
              tip={tipDismissed ? null : tip}
              onDismissTip={() => setTipDismissed(true)}
              onReportIncident={() => setShowIncidentReport(true)}
              onOpenChecklists={() => setShowChecklists(true)}
            />
          )}

          <ChatInput
            value={inputMessage}
            disabled={isTyping || !persona}
            onChange={setInputMessage}
            onSend={() => sendMessage()}
          />

          {persona && (
            <div className="hint">
              {persona.department} &middot; {persona.role}
            </div>
          )}
        </div>

        {/* Modals */}
        {showIncidentReport && (
          <IncidentReport
            onClose={() => setShowIncidentReport(false)}
            onSubmit={handleIncidentSubmit}
            persona={persona}
          />
        )}
        {showChecklists && (
          <SecurityChecklist
            onClose={() => setShowChecklists(false)}
            persona={persona}
          />
        )}
        {showAnalytics && (
          <AnalyticsDashboard onClose={() => setShowAnalytics(false)} />
        )}
      </div>
    </div>
  );
}
